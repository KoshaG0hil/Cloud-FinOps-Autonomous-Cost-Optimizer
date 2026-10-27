# ------------------------------------------------------------------------------
# Immutable S3 FinOps Report & Audit Archive Bucket
# ------------------------------------------------------------------------------
resource "aws_s3_bucket" "finops_reports" {
  bucket        = "${local.name_prefix}-reports-${local.account_id}"
  force_destroy = false
}

resource "aws_s3_bucket_versioning" "finops_reports_versioning" {
  bucket = aws_s3_bucket.finops_reports.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "finops_reports_encryption" {
  bucket = aws_s3_bucket.finops_reports.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "finops_reports_pab" {
  bucket = aws_s3_bucket.finops_reports.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "finops_reports_lifecycle" {
  bucket = aws_s3_bucket.finops_reports.id

  rule {
    id     = "archive-and-expire-finops-reports"
    status = "Enabled"

    filter {}

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 365
    }
  }
}

resource "aws_s3_bucket_policy" "finops_reports_tls_only" {
  bucket = aws_s3_bucket.finops_reports.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "EnforceTLSRequestsOnly"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.finops_reports.arn,
          "${aws_s3_bucket.finops_reports.arn}/*"
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      }
    ]
  })
}
