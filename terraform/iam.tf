# ------------------------------------------------------------------------------
# IAM Execution Role for FinOps Lambda Function
# ------------------------------------------------------------------------------
resource "aws_iam_role" "finops_lambda_role" {
  name = "${local.name_prefix}-lambda-exec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# ------------------------------------------------------------------------------
# Scoped FinOps Least-Privilege Execution Policy
# ------------------------------------------------------------------------------
resource "aws_iam_policy" "finops_execution_policy" {
  name        = "${local.name_prefix}-execution-permissions"
  description = "Scoped permissions for autonomous EBS deletion, EC2 auto-parking, tagging, and reporting"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # CloudWatch Logging
      {
        Sid    = "CloudWatchLogging"
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.finops_logs.arn}:*"
      },
      # EC2 Telemetry & Parking
      {
        Sid    = "EC2TelemetryAndParking"
        Effect = "Allow"
        Action = [
          "ec2:DescribeInstances",
          "ec2:DescribeInstanceStatus",
          "ec2:StartInstances",
          "ec2:StopInstances",
          "ec2:CreateTags"
        ]
        Resource = "*"
      },
      # EBS Volume & Snapshot Waste Cleanup
      {
        Sid    = "EBSOptimization"
        Effect = "Allow"
        Action = [
          "ec2:DescribeVolumes",
          "ec2:DescribeSnapshots",
          "ec2:CreateSnapshot",
          "ec2:DeleteVolume",
          "ec2:DeleteSnapshot",
          "ec2:CreateTags"
        ]
        Resource = "*"
      },
      # S3 FinOps Report Storage
      {
        Sid    = "S3ReportArchive"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject"
        ]
        Resource = "${aws_s3_bucket.finops_reports.arn}/*"
      },
      # SNS Alert Broadcasting
      {
        Sid    = "SNSSavingsDispatch"
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = aws_sns_topic.finops_alerts.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "finops_lambda_attach" {
  role       = aws_iam_role.finops_lambda_role.name
  policy_arn = aws_iam_policy.finops_execution_policy.arn
}
