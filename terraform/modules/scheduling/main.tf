# Application Auto Scaling target for the ECS service

resource "aws_appautoscaling_target" "ecs" {
  max_capacity       = 2
  min_capacity       = 0
  resource_id        = "service/${var.ecs_cluster_name}/${var.ecs_service_name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"

  tags = var.tags
}

# Scale UP: weekday mornings (default 8 AM CT)

resource "aws_appautoscaling_scheduled_action" "scale_up" {
  name               = "${var.name_prefix}-scale-up"
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  schedule           = var.scale_up_cron
  timezone           = "America/Chicago"

  scalable_target_action {
    min_capacity = 1
    max_capacity = 2
  }
}

# Scale DOWN to zero: weekday evenings (default 10 PM CT)

resource "aws_appautoscaling_scheduled_action" "scale_down" {
  name               = "${var.name_prefix}-scale-down"
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  schedule           = var.scale_down_cron
  timezone           = "America/Chicago"

  scalable_target_action {
    min_capacity = 0
    max_capacity = 0
  }
}

# Scale DOWN all weekend

resource "aws_appautoscaling_scheduled_action" "weekend_down" {
  name               = "${var.name_prefix}-weekend-down"
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  schedule           = "cron(0 0 ? * SAT *)"
  timezone           = "America/Chicago"

  scalable_target_action {
    min_capacity = 0
    max_capacity = 0
  }
}

resource "aws_appautoscaling_scheduled_action" "weekend_up" {
  name               = "${var.name_prefix}-weekend-up"
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  schedule           = "cron(0 8 ? * MON *)"
  timezone           = "America/Chicago"

  scalable_target_action {
    min_capacity = 1
    max_capacity = 2
  }
}