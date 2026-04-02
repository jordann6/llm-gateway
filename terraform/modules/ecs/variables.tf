variable "name_prefix" { type = string }
variable "aws_region" { type = string }
variable "container_image" { type = string }
variable "container_port" { type = number }
variable "task_cpu" { type = number }
variable "task_memory" { type = number }
variable "subnet_ids" { type = list(string) }
variable "security_group_id" { type = string }
variable "vpc_id" { type = string }

variable "openai_secret_arn" { type = string }
variable "anthropic_secret_arn" { type = string }
variable "secrets_kms_key_arn" { type = string }

variable "request_log_table_name" { type = string }
variable "cache_table_name" { type = string }
variable "eval_table_name" { type = string }
variable "log_archive_bucket" { type = string }

variable "request_log_table_arn" { type = string }
variable "cache_table_arn" { type = string }
variable "eval_table_arn" { type = string }
variable "log_archive_bucket_arn" { type = string }

variable "tags" { type = map(string) }