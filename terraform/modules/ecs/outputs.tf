output "cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "cluster_arn" {
  value = aws_ecs_cluster.main.arn
}

output "service_name" {
  value = aws_ecs_service.gateway.name
}

output "ecr_repository_url" {
  value = aws_ecr_repository.gateway.repository_url
}

output "service_discovery_endpoint" {
  value = "gateway.${aws_service_discovery_private_dns_namespace.main.name}"
}

output "task_execution_role_arn" {
  value = aws_iam_role.task_execution.arn
}

output "task_role_arn" {
  value = aws_iam_role.task.arn
}
output "service_discovery_arn" {
  value = aws_service_discovery_service.gateway.arn
}
