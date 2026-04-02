variable "name_prefix" { type = string }
variable "aws_region" { type = string }
variable "request_log_table_name" { type = string }
variable "request_log_table_arn" { type = string }
variable "log_archive_bucket" { type = string }
variable "log_archive_bucket_arn" { type = string }
variable "tags" { type = map(string) }