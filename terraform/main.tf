terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = ">= 2.4.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "Cloud-FinOps-Autonomous-Cost-Optimizer"
      ManagedBy   = "Terraform"
      Environment = var.environment
      Repository  = "https://github.com/KoshaG0hil/Cloud-FinOps-Autonomous-Cost-Optimizer"
    }
  }
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  account_id  = data.aws_caller_identity.current.account_id
}

# ------------------------------------------------------------------------------
# Amazon SNS FinOps Alert & Savings Topic
# ------------------------------------------------------------------------------
resource "aws_sns_topic" "finops_alerts" {
  name              = "${local.name_prefix}-alerts"
  kms_master_key_id = "alias/aws/sns"
}

# ------------------------------------------------------------------------------
# CloudWatch Log Group for Lambda
# ------------------------------------------------------------------------------
resource "aws_cloudwatch_log_group" "finops_logs" {
  name              = "/aws/lambda/${local.name_prefix}-optimizer"
  retention_in_days = 90
}

# ------------------------------------------------------------------------------
# Lambda Deployment Archive
# ------------------------------------------------------------------------------
data "archive_file" "finops_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src"
  output_path = "${path.module}/finops_lambda_payload.zip"
}

# ------------------------------------------------------------------------------
# FinOps Master Lambda Function
# ------------------------------------------------------------------------------
resource "aws_lambda_function" "finops_engine" {
  filename         = data.archive_file.finops_lambda_zip.output_path
  function_name    = "${local.name_prefix}-optimizer"
  role             = aws_iam_role.finops_lambda_role.arn
  handler          = "lambda_handler.lambda_handler"
  runtime          = "python3.12"
  timeout          = 300
  memory_size      = 512
  source_code_hash = data.archive_file.finops_lambda_zip.output_base64sha256

  environment {
    variables = {
      FINOPS_DRY_RUN           = tostring(var.dry_run_mode)
      FINOPS_REPORT_S3_BUCKET  = aws_s3_bucket.finops_reports.id
      FINOPS_SNS_TOPIC_ARN     = aws_sns_topic.finops_alerts.arn
      SLACK_WEBHOOK_URL        = var.slack_webhook_url
      ENVIRONMENT              = var.environment
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.finops_logs,
    aws_iam_role_policy_attachment.finops_lambda_attach
  ]
}
