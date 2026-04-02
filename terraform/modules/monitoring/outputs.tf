output "dashboard_url" {
  value = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}

output "error_alarm_arn" {
  value = aws_cloudwatch_metric_alarm.high_error_rate.arn
}

output "eval_drift_alarm_arn" {
  value = aws_cloudwatch_metric_alarm.eval_quality_drift.arn
}