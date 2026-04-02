"""
LLM Gateway — Log Archival Lambda

Triggered nightly by EventBridge. Scans the DynamoDB request log table for
records older than the retention window (default 7 days), batches them into
gzipped NDJSON files, uploads to S3, then deletes the archived records from
DynamoDB.

Environment Variables:
    DYNAMODB_TABLE  — Name of the request log DynamoDB table
    S3_BUCKET       — S3 bucket for archived logs
    AWS_REGION_VAR  — AWS region
    RETENTION_DAYS  — Days to keep in DynamoDB before archiving (default: 7)
    BATCH_SIZE      — Records per S3 file (default: 500)
"""

import json
import gzip
import os
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DYNAMODB_TABLE = os.environ["DYNAMODB_TABLE"]
S3_BUCKET = os.environ["S3_BUCKET"]
REGION = os.environ.get("AWS_REGION_VAR", "us-east-1")
RETENTION_DAYS = int(os.environ.get("RETENTION_DAYS", "7"))
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "500"))

dynamodb = boto3.resource("dynamodb", region_name=REGION)
s3 = boto3.client("s3", region_name=REGION)
table = dynamodb.Table(DYNAMODB_TABLE)


def get_cutoff_timestamp() -> str:
    """Return ISO timestamp for the retention cutoff."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
    return cutoff.isoformat()


def scan_expired_records(cutoff: str) -> list[dict[str, Any]]:
    """Scan for all records with timestamp before the cutoff.

    Uses a scan with filter since we need records across all partition keys.
    For higher scale, consider a GSI on timestamp.
    """
    records = []
    scan_kwargs = {
        "FilterExpression": "#ts < :cutoff",
        "ExpressionAttributeNames": {"#ts": "timestamp"},
        "ExpressionAttributeValues": {":cutoff": cutoff},
    }

    while True:
        response = table.scan(**scan_kwargs)
        records.extend(response.get("Items", []))

        if "LastEvaluatedKey" not in response:
            break
        scan_kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]

    return records


def convert_decimals(obj: Any) -> Any:
    """Convert DynamoDB Decimal types to int/float for JSON serialization."""
    from decimal import Decimal

    if isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        return float(obj)
    if isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    return obj


def compress_records(records: list[dict]) -> bytes:
    """Compress records as gzipped newline delimited JSON."""
    lines = []
    for record in records:
        cleaned = convert_decimals(record)
        lines.append(json.dumps(cleaned, default=str))
    content = "\n".join(lines) + "\n"
    return gzip.compress(content.encode("utf-8"))


def build_s3_key(batch_index: int) -> str:
    """Build S3 key with date partitioning for Athena compatibility.

    Format: logs/year=YYYY/month=MM/day=DD/archive-{uuid}-{batch}.json.gz
    """
    now = datetime.now(timezone.utc)
    return (
        f"logs/year={now.year}/month={now.month:02d}/day={now.day:02d}/"
        f"archive-{uuid.uuid4().hex[:8]}-{batch_index:04d}.json.gz"
    )


def upload_to_s3(data: bytes, key: str) -> None:
    """Upload gzipped data to S3 with KMS encryption."""
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=data,
        ContentType="application/x-ndjson",
        ContentEncoding="gzip",
        ServerSideEncryption="aws:kms",
    )
    logger.info(f"Uploaded {key} ({len(data)} bytes)")


def delete_archived_records(records: list[dict]) -> int:
    """Batch delete archived records from DynamoDB.

    Uses batch_writer for automatic batching (25 items per batch).
    """
    deleted = 0
    with table.batch_writer() as batch:
        for record in records:
            batch.delete_item(
                Key={
                    "request_id": record["request_id"],
                    "timestamp": record["timestamp"],
                }
            )
            deleted += 1
    return deleted


def handler(event: dict, context: Any) -> dict:
    """Lambda entry point. Triggered by EventBridge nightly schedule."""
    logger.info(f"Starting log archival. Retention: {RETENTION_DAYS} days")

    cutoff = get_cutoff_timestamp()
    logger.info(f"Archiving records older than {cutoff}")

    try:
        records = scan_expired_records(cutoff)
    except ClientError as e:
        logger.error(f"DynamoDB scan failed: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

    total = len(records)
    logger.info(f"Found {total} records to archive")

    if total == 0:
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "No records to archive",
                "cutoff": cutoff,
            }),
        }

    archived = 0
    deleted = 0

    for batch_index in range(0, total, BATCH_SIZE):
        batch = records[batch_index : batch_index + BATCH_SIZE]

        try:
            compressed = compress_records(batch)
            s3_key = build_s3_key(batch_index // BATCH_SIZE)
            upload_to_s3(compressed, s3_key)
            archived += len(batch)
        except ClientError as e:
            logger.error(f"S3 upload failed for batch {batch_index}: {e}")
            continue

        try:
            batch_deleted = delete_archived_records(batch)
            deleted += batch_deleted
        except ClientError as e:
            logger.error(
                f"DynamoDB delete failed for batch {batch_index}: {e}. "
                f"Records are archived in S3 but not removed from DynamoDB. "
                f"They will be retried on next run or cleaned up by TTL."
            )

    summary = {
        "message": "Archival complete",
        "cutoff": cutoff,
        "total_found": total,
        "archived_to_s3": archived,
        "deleted_from_dynamodb": deleted,
    }

    logger.info(json.dumps(summary))

    return {"statusCode": 200, "body": json.dumps(summary)}