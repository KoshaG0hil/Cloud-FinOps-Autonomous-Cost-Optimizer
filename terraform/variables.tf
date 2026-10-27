variable "aws_region" {
  description = "Target AWS region for FinOps deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment name (e.g. production, dev)"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Resource prefix identifier"
  type        = string
  default     = "cloud-finops"
}

variable "dry_run_mode" {
  description = "If true, simulates savings without deleting or stopping active assets"
  type        = bool
  default     = true
}

variable "enable_slack_alerts" {
  description = "Flag to enable Slack cost optimization notifications"
  type        = bool
  default     = false
}

variable "slack_webhook_url" {
  description = "Incoming Webhook URL for FinOps notifications"
  type        = string
  default     = ""
  sensitive   = true
}

variable "off_hours_stop_cron" {
  description = "EventBridge cron schedule to auto-park non-prod dev instances"
  type        = string
  default     = "cron(0 19 ? * MON-FRI *)" # 7:00 PM Mon-Fri UTC
}

variable "on_hours_start_cron" {
  description = "EventBridge cron schedule to wake up auto-parked dev instances"
  type        = string
  default     = "cron(0 7 ? * MON-FRI *)"  # 7:00 AM Mon-Fri UTC
}
