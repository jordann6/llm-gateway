variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for resource naming and tagging"
  type        = string
  default     = "llm-gateway"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "container_image" {
  description = "Full ECR image URI for the gateway container"
  type        = string
}

variable "container_port" {
  description = "Port the FastAPI app listens on"
  type        = number
  default     = 8000
}

variable "task_cpu" {
  description = "Fargate task CPU units (256 = 0.25 vCPU)"
  type        = number
  default     = 256
}

variable "task_memory" {
  description = "Fargate task memory in MB"
  type        = number
  default     = 512
}

variable "enable_scheduling" {
  description = "Enable scale to zero scheduling for off hours"
  type        = bool
  default     = true
}

variable "schedule_scale_up_cron" {
  description = "Cron expression for scaling up (UTC). Default: 8 AM CT / 1 PM UTC weekdays"
  type        = string
  default     = "cron(0 13 ? * MON-FRI *)"
}

variable "schedule_scale_down_cron" {
  description = "Cron expression for scaling down (UTC). Default: 10 PM CT / 3 AM UTC next day"
  type        = string
  default     = "cron(0 3 ? * TUE-SAT *)"
}

variable "openai_api_key" {
  description = "OpenAI API key (stored in Secrets Manager)"
  type        = string
  sensitive   = true
}

variable "anthropic_api_key" {
  description = "Anthropic API key (stored in Secrets Manager)"
  type        = string
  sensitive   = true
}

variable "common_tags" {
  description = "Tags applied to all resources"
  type        = map(string)
  default     = {}
}

locals {
  name_prefix = "${var.project_name}-${var.environment}"

  default_tags = merge(var.common_tags, {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  })
}