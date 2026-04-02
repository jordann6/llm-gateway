"""Application configuration loaded from environment variables."""

import os


class Settings:
    """Settings populated from ECS task definition environment variables."""

    PORT: int = int(os.environ.get("PORT", "8000"))
    AWS_REGION: str = os.environ.get("AWS_REGION", "us-east-1")

    # DynamoDB tables
    DYNAMODB_REQUEST_LOG_TABLE: str = os.environ.get(
        "DYNAMODB_REQUEST_LOG_TABLE", "llm-gateway-dev-request-log"
    )
    DYNAMODB_CACHE_TABLE: str = os.environ.get(
        "DYNAMODB_CACHE_TABLE", "llm-gateway-dev-cache"
    )
    DYNAMODB_EVAL_TABLE: str = os.environ.get(
        "DYNAMODB_EVAL_TABLE", "llm-gateway-dev-eval"
    )

    # S3
    S3_LOG_ARCHIVE_BUCKET: str = os.environ.get(
        "S3_LOG_ARCHIVE_BUCKET", ""
    )

    # CloudWatch
    CLOUDWATCH_NAMESPACE: str = os.environ.get(
        "CLOUDWATCH_NAMESPACE", "LLMGateway"
    )

    # Provider API keys (injected from Secrets Manager)
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.environ.get("ANTHROPIC_API_KEY", "")

    # DynamoDB Local endpoint (local dev only)
    DYNAMODB_ENDPOINT_URL: str | None = os.environ.get(
        "DYNAMODB_ENDPOINT_URL", None
    )

    # Cache TTL in seconds (default 1 hour)
    CACHE_TTL_SECONDS: int = int(os.environ.get("CACHE_TTL_SECONDS", "3600"))

    # Request log TTL in seconds (default 7 days)
    REQUEST_LOG_TTL_SECONDS: int = int(
        os.environ.get("REQUEST_LOG_TTL_SECONDS", "604800")
    )

    # Eval sampling rate (0.0 to 1.0)
    EVAL_SAMPLE_RATE: float = float(
        os.environ.get("EVAL_SAMPLE_RATE", "0.1")
    )


settings = Settings()
