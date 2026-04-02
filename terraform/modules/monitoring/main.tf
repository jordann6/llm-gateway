locals {
  namespace = "LLMGateway"
}

# CloudWatch Dashboard

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.name_prefix}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "text"
        x      = 0
        y      = 0
        width  = 24
        height = 1
        properties = {
          markdown = "# LLM Gateway Dashboard"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 1
        width  = 8
        height = 6
        properties = {
          title   = "Request Latency (p50 / p90 / p99)"
          region  = var.aws_region
          metrics = [
            [local.namespace, "RequestLatencyMs", "Stat", "p50", { stat = "p50" }],
            ["...", { stat = "p90" }],
            ["...", { stat = "p99" }]
          ]
          period = 300
          view   = "timeSeries"
        }
      },
      {
        type   = "metric"
        x      = 8
        y      = 1
        width  = 8
        height = 6
        properties = {
          title   = "Token Usage by Provider"
          region  = var.aws_region
          metrics = [
            [local.namespace, "InputTokens", "Provider", "openai"],
            [local.namespace, "OutputTokens", "Provider", "openai"],
            [local.namespace, "InputTokens", "Provider", "anthropic"],
            [local.namespace, "OutputTokens", "Provider", "anthropic"]
          ]
          period = 300
          stat   = "Sum"
          view   = "timeSeries"
        }
      },
      {
        type   = "metric"
        x      = 16
        y      = 1
        width  = 8
        height = 6
        properties = {
          title   = "Estimated Cost (cents)"
          region  = var.aws_region
          metrics = [
            [local.namespace, "EstimatedCostCents", "Provider", "openai"],
            [local.namespace, "EstimatedCostCents", "Provider", "anthropic"]
          ]
          period = 3600
          stat   = "Sum"
          view   = "timeSeries"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 7
        width  = 8
        height = 6
        properties = {
          title   = "Cache Hit Rate"
          region  = var.aws_region
          metrics = [
            [local.namespace, "CacheHit"],
            [local.namespace, "CacheMiss"]
          ]
          period = 300
          stat   = "Sum"
          view   = "timeSeries"
        }
      },
      {
        type   = "metric"
        x      = 8
        y      = 7
        width  = 8
        height = 6
        properties = {
          title   = "Error Rate by Provider"
          region  = var.aws_region
          metrics = [
            [local.namespace, "ProviderError", "Provider", "openai"],
            [local.namespace, "ProviderError", "Provider", "anthropic"]
          ]
          period = 300
          stat   = "Sum"
          view   = "timeSeries"
        }
      },
      {
        type   = "metric"
        x      = 16
        y      = 7
        width  = 8
        height = 6
        properties = {
          title   = "Eval Quality Score (rolling avg)"
          region  = var.aws_region
          metrics = [
            [local.namespace, "EvalScore", "Provider", "openai", { stat = "Average" }],
            [local.namespace, "EvalScore", "Provider", "anthropic", { stat = "Average" }]
          ]
          period = 3600
          view   = "timeSeries"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 13
        width  = 12
        height = 6
        properties = {
          title   = "Feedback Signals"
          region  = var.aws_region
          metrics = [
            [local.namespace, "FeedbackPositive"],
            [local.namespace, "FeedbackNegative"]
          ]
          period = 3600
          stat   = "Sum"
          view   = "bar"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 13
        width  = 12
        height = 6
        properties = {
          title   = "ECS Task Count & CPU"
          region  = var.aws_region
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ClusterName", var.ecs_cluster_name, "ServiceName", var.ecs_service_name, { stat = "Average" }],
            ["AWS/ECS", "MemoryUtilization", "ClusterName", var.ecs_cluster_name, "ServiceName", var.ecs_service_name, { stat = "Average" }]
          ]
          period = 300
          view   = "timeSeries"
        }
      }
    ]
  })
}

# Alarm: high error rate

resource "aws_cloudwatch_metric_alarm" "high_error_rate" {
  alarm_name          = "${var.name_prefix}-high-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  threshold           = 10
  alarm_description   = "More than 10 provider errors in 5 minutes"
  treat_missing_data  = "notBreaching"

  metric_name = "ProviderError"
  namespace   = local.namespace
  period      = 300
  statistic   = "Sum"

  tags = var.tags
}

# Alarm: eval quality drift

resource "aws_cloudwatch_metric_alarm" "eval_quality_drift" {
  alarm_name          = "${var.name_prefix}-eval-quality-drift"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  threshold           = 3.5
  alarm_description   = "Average eval score dropped below 3.5/5 over 2 consecutive hours"
  treat_missing_data  = "notBreaching"

  metric_name = "EvalScore"
  namespace   = local.namespace
  period      = 3600
  statistic   = "Average"

  tags = var.tags
}

# Alarm: daily cost spike

resource "aws_cloudwatch_metric_alarm" "cost_spike" {
  alarm_name          = "${var.name_prefix}-daily-cost-spike"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  threshold           = 100
  alarm_description   = "Estimated daily LLM cost exceeded 100 cents ($1)"
  treat_missing_data  = "notBreaching"

  metric_name = "EstimatedCostCents"
  namespace   = local.namespace
  period      = 86400
  statistic   = "Sum"

  tags = var.tags
}