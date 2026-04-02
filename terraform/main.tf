module "networking" {
  source = "./modules/networking"

  name_prefix    = local.name_prefix
  container_port = var.container_port
  tags           = local.default_tags
}

module "secrets" {
  source = "./modules/secrets"

  name_prefix     = local.name_prefix
  openai_api_key  = var.openai_api_key
  anthropic_api_key = var.anthropic_api_key
  tags            = local.default_tags
}

module "dynamodb" {
  source = "./modules/dynamodb"

  name_prefix = local.name_prefix
  tags        = local.default_tags
}

module "s3" {
  source = "./modules/s3"

  name_prefix = local.name_prefix
  tags        = local.default_tags
}

module "ecs" {
  source = "./modules/ecs"

  name_prefix     = local.name_prefix
  aws_region      = var.aws_region
  container_image = var.container_image
  container_port  = var.container_port
  task_cpu        = var.task_cpu
  task_memory     = var.task_memory
  subnet_ids      = module.networking.private_subnet_ids
  security_group_id = module.networking.ecs_security_group_id
  vpc_id          = module.networking.vpc_id

  openai_secret_arn    = module.secrets.openai_secret_arn
  anthropic_secret_arn = module.secrets.anthropic_secret_arn
  secrets_kms_key_arn  = module.secrets.secrets_kms_key_arn

  request_log_table_name = module.dynamodb.request_log_table_name
  cache_table_name       = module.dynamodb.cache_table_name
  eval_table_name        = module.dynamodb.eval_table_name
  log_archive_bucket     = module.s3.log_archive_bucket_name

  request_log_table_arn = module.dynamodb.request_log_table_arn
  cache_table_arn       = module.dynamodb.cache_table_arn
  eval_table_arn        = module.dynamodb.eval_table_arn
  log_archive_bucket_arn = module.s3.log_archive_bucket_arn

  tags = local.default_tags
}

module "scheduling" {
  source = "./modules/scheduling"
  count  = var.enable_scheduling ? 1 : 0

  name_prefix          = local.name_prefix
  ecs_cluster_name     = module.ecs.cluster_name
  ecs_service_name     = module.ecs.service_name
  scale_up_cron        = var.schedule_scale_up_cron
  scale_down_cron      = var.schedule_scale_down_cron
  tags                 = local.default_tags
}

module "api_gateway" {
  source = "./modules/api_gateway"

  name_prefix    = local.name_prefix
  container_port = var.container_port
  vpc_link_subnet_ids   = module.networking.private_subnet_ids
  vpc_link_security_group_id = module.networking.api_gw_vpc_link_security_group_id
  ecs_service_discovery_arn = module.ecs.service_discovery_arn
  tags           = local.default_tags
}

module "lambda" {
  source = "./modules/lambda"

  name_prefix            = local.name_prefix
  aws_region             = var.aws_region
  request_log_table_name = module.dynamodb.request_log_table_name
  request_log_table_arn  = module.dynamodb.request_log_table_arn
  log_archive_bucket     = module.s3.log_archive_bucket_name
  log_archive_bucket_arn = module.s3.log_archive_bucket_arn
  tags                   = local.default_tags
}

module "monitoring" {
  source = "./modules/monitoring"

  name_prefix      = local.name_prefix
  aws_region       = var.aws_region
  ecs_cluster_name = module.ecs.cluster_name
  ecs_service_name = module.ecs.service_name
  api_gateway_id   = module.api_gateway.api_id
  tags             = local.default_tags
}