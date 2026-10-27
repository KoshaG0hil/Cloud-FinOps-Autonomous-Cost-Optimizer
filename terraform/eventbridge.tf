# ------------------------------------------------------------------------------
# EventBridge Rule 1: Daily Waste & Rightsizing Sweep (6:00 AM UTC)
# ------------------------------------------------------------------------------
resource "aws_cloudwatch_event_rule" "daily_finops_sweep" {
  name                = "${local.name_prefix}-daily-sweep"
  description         = "Daily scheduled audit of unattached EBS, aged snapshots, and idle compute"
  schedule_expression = "cron(0 6 * * ? *)"
}

resource "aws_cloudwatch_event_target" "target_daily_sweep" {
  rule      = aws_cloudwatch_event_rule.daily_finops_sweep.name
  target_id = "TriggerFinOpsDailySweep"
  arn       = aws_lambda_function.finops_engine.arn
  input     = jsonencode({ action = "SWEEP" })
}

resource "aws_lambda_permission" "allow_eventbridge_sweep" {
  statement_id  = "AllowEventBridgeDailySweep"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.finops_engine.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_finops_sweep.arn
}

# ------------------------------------------------------------------------------
# EventBridge Rule 2: Nightly Auto-Park (Stop Non-Prod Dev Instances at 7:00 PM)
# ------------------------------------------------------------------------------
resource "aws_cloudwatch_event_rule" "evening_autopark" {
  name                = "${local.name_prefix}-evening-autopark"
  description         = "Stops non-prod dev instances tagged with AutoPark=true on weekday evenings"
  schedule_expression = var.off_hours_stop_cron
}

resource "aws_cloudwatch_event_target" "target_evening_autopark" {
  rule      = aws_cloudwatch_event_rule.evening_autopark.name
  target_id = "TriggerFinOpsEveningPark"
  arn       = aws_lambda_function.finops_engine.arn
  input     = jsonencode({ action = "PARK_STOP" })
}

resource "aws_lambda_permission" "allow_eventbridge_park" {
  statement_id  = "AllowEventBridgeEveningPark"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.finops_engine.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.evening_autopark.arn
}

# ------------------------------------------------------------------------------
# EventBridge Rule 3: Morning Wakeup (Start Dev Instances at 7:00 AM)
# ------------------------------------------------------------------------------
resource "aws_cloudwatch_event_rule" "morning_wakeup" {
  name                = "${local.name_prefix}-morning-wakeup"
  description         = "Starts non-prod dev instances tagged with AutoPark=true on weekday mornings"
  schedule_expression = var.on_hours_start_cron
}

resource "aws_cloudwatch_event_target" "target_morning_wakeup" {
  rule      = aws_cloudwatch_event_rule.morning_wakeup.name
  target_id = "TriggerFinOpsMorningWake"
  arn       = aws_lambda_function.finops_engine.arn
  input     = jsonencode({ action = "PARK_START" })
}

resource "aws_lambda_permission" "allow_eventbridge_wake" {
  statement_id  = "AllowEventBridgeMorningWake"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.finops_engine.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.morning_wakeup.arn
}
