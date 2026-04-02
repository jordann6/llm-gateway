# KMS key for Secrets Manager encryption

resource "aws_kms_key" "secrets" {
  description             = "KMS key for ${var.name_prefix} Secrets Manager"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = var.tags
}

resource "aws_kms_alias" "secrets" {
  name          = "alias/${var.name_prefix}-secrets"
  target_key_id = aws_kms_key.secrets.key_id
}

# OpenAI API key

resource "aws_secretsmanager_secret" "openai" {
  name       = "${var.name_prefix}/openai-api-key"
  kms_key_id = aws_kms_key.secrets.arn

  tags = var.tags
}

resource "aws_secretsmanager_secret_version" "openai" {
  secret_id     = aws_secretsmanager_secret.openai.id
  secret_string = var.openai_api_key
}

# Anthropic API key

resource "aws_secretsmanager_secret" "anthropic" {
  name       = "${var.name_prefix}/anthropic-api-key"
  kms_key_id = aws_kms_key.secrets.arn

  tags = var.tags
}

resource "aws_secretsmanager_secret_version" "anthropic" {
  secret_id     = aws_secretsmanager_secret.anthropic.id
  secret_string = var.anthropic_api_key
}