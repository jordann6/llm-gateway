data "aws_caller_identity" "current" {}

# IAM role for the archival Lambda

resource "aws_iam_role" "archival" {
  name = "${var.name_prefix}-log-archival"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Condition = {
        StringEquals = {
          "aws:SourceAccount" = data.aws_caller_identity.current.account_id
        }
      }
    }]
  })

  tags = var.tags
}

resource "aws_iam_role_policy" "archival" {
  name = "${var.name_prefix}-archival-permissions"
  role = aws_iam_role.archival.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DynamoDBRead"
        Effect = "Allow"
        Action = [
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:DeleteItem"
        ]
        Resource = [
          var.request_log_table_arn,
          "${var.request_log_table_arn}/index/*"
        ]
      },
      {
        Sid    = "S3Write"
        Effect = "Allow"
        Action = [
          "s3:PutObject"
        ]
        Resource = "${var.log_archive_bucket_arn}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-server-side-encryption" = "aws:kms"
          }
        }
      },
      {
        Sid    = "CloudWatchLogs"
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.archival.arn}:*"
      }
    ]
  })
}

# CloudWatch log group for Lambda

resource "aws_cloudwatch_log_group" "archival" {
  name              = "/aws/lambda/${var.name_prefix}-log-archival"
  retention_in_days = 7

  tags = var.tags
}

# Lambda function package

data "archive_file" "archival" {
  type        = "zip"
  source_dir  = "${path.module}/../../../lambda/log_archival"
  output_path = "${path.module}/log_archival.zip"
}

resource "aws_lambda_function" "archival" {
  function_name = "${var.name_prefix}-log-archival"
  role          = aws_iam_role.archival.arn
  handler       = "handler.handler"
  runtime       = "python3.12"
  timeout       = 120
  memory_size   = 256

  filename         = data.archive_file.archival.output_path
  source_code_hash = data.archive_file.archival.output_base64sha256

  environment {
    variables = {
      DYNAMODB_TABLE = var.request_log_table_name
      S3_BUCKET      = var.log_archive_bucket
      AWS_REGION_VAR = var.aws_region
      RETENTION_DAYS = "7"
      BATCH_SIZE     = "500"
    }
  }

  tags = var.tags

  depends_on = [aws_cloudwatch_log_group.archival]
}

# EventBridge rule: run nightly at 4 AM CT (9 AM UTC)

resource "aws_cloudwatch_event_rule" "nightly_archival" {
  name                = "${var.name_prefix}-nightly-archival"
  schedule_expression = "cron(0 9 * * ? *)"

  tags = var.tags
}

resource "aws_cloudwatch_event_target" "archival" {
  rule = aws_cloudwatch_event_rule.nightly_archival.name
  arn  = aws_lambda_function.archival.arn
}

resource "aws_lambda_permission" "eventbridge" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.archival.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.nightly_archival.arn
}