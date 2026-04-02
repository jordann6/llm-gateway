output "request_log_table_name" {
  value = aws_dynamodb_table.request_log.name
}

output "request_log_table_arn" {
  value = aws_dynamodb_table.request_log.arn
}

output "cache_table_name" {
  value = aws_dynamodb_table.cache.name
}

output "cache_table_arn" {
  value = aws_dynamodb_table.cache.arn
}

output "eval_table_name" {
  value = aws_dynamodb_table.eval.name
}

output "eval_table_arn" {
  value = aws_dynamodb_table.eval.arn
}