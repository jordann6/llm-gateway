"""Centralized AWS client factory."""

import boto3
from app.core import settings


def get_dynamodb_resource():
    """Get DynamoDB resource, with optional local endpoint for dev."""
    kwargs = {"region_name": settings.AWS_REGION}
    if settings.DYNAMODB_ENDPOINT_URL:
        kwargs["endpoint_url"] = settings.DYNAMODB_ENDPOINT_URL
    return boto3.resource("dynamodb", **kwargs)


def get_cloudwatch_client():
    """Get CloudWatch client for metric publishing."""
    return boto3.client("cloudwatch", region_name=settings.AWS_REGION)


def get_s3_client():
    """Get S3 client for log archival."""
    return boto3.client("s3", region_name=settings.AWS_REGION)


dynamodb = get_dynamodb_resource()
cloudwatch = get_cloudwatch_client()
s3 = get_s3_client()
