output "lambda_function_arn" {
  description = "ARN of the FinOps Optimizer Lambda function"
  value       = aws_lambda_function.finops_engine.arn
}

output "lambda_function_name" {
  description = "Name of the FinOps Optimizer Lambda function"
  value       = aws_lambda_function.finops_engine.function_name
}

output "finops_reports_s3_bucket" {
  description = "Name of the S3 bucket archiving FinOps audit manifests"
  value       = aws_s3_bucket.finops_reports.id
}

output "sns_alerts_topic_arn" {
  description = "ARN of the SNS topic broadcasting FinOps savings notifications"
  value       = aws_sns_topic.finops_alerts.arn
}

output "daily_sweep_eventbridge_rule_arn" {
  description = "ARN of the EventBridge rule for daily waste discovery"
  value       = aws_cloudwatch_event_rule.daily_finops_sweep.arn
}

output "evening_autopark_eventbridge_rule_arn" {
  description = "ARN of the EventBridge rule for evening instance auto-parking"
  value       = aws_cloudwatch_event_rule.evening_autopark.arn
}
