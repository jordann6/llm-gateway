variable "name_prefix" { type = string }
variable "container_port" { type = number }
variable "vpc_link_subnet_ids" { type = list(string) }
variable "vpc_link_security_group_id" { type = string }
variable "ecs_service_discovery_arn" { type = string }
variable "tags" { type = map(string) }