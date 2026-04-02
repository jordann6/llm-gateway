output "openai_secret_arn" {
  value = aws_secretsmanager_secret.openai.arn
}

output "anthropic_secret_arn" {
  value = aws_secretsmanager_secret.anthropic.arn
}

output "secrets_kms_key_arn" {
  value = aws_kms_key.secrets.arn
}