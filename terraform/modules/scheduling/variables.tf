variable "name_prefix" { type = string }
variable "ecs_cluster_name" { type = string }
variable "ecs_service_name" { type = string }
variable "scale_up_cron" { type = string }
variable "scale_down_cron" { type = string }
variable "tags" { type = map(string) }