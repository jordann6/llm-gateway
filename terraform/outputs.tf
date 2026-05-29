output "api_endpoint" {
  description = "API Gateway endpoint URL"
  value       = module.api_gateway.api_endpoint
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = module.ecs.cluster_name
}

output "ecs_service_name" {
  description = "ECS service name"
  value       = module.ecs.service_name
}

output "cloudwatch_dashboard_url" {
  description = "CloudWatch dashboard URL"
  value       = module.monitoring.dashboard_url
}

output "log_archive_bucket" {
  description = "S3 bucket for archived request logs"
  value       = module.s3.log_archive_bucket_name
}

output "ecr_repository_url" {
  description = "ECR repository URL for pushing container images"
  value       = module.ecs.ecr_repository_url
}

output "request_log_table_name" {
  description = "DynamoDB request log table name (used by the FinOps cost intelligence dashboard)"
  value       = module.dynamodb.request_log_table_name
}

output "request_log_table_arn" {
  description = "DynamoDB request log table ARN"
  value       = module.dynamodb.request_log_table_arn
}