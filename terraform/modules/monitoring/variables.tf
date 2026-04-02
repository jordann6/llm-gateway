variable "name_prefix" { type = string }
variable "aws_region" { type = string }
variable "ecs_cluster_name" { type = string }
variable "ecs_service_name" { type = string }
variable "api_gateway_id" { type = string }
variable "tags" { type = map(string) }