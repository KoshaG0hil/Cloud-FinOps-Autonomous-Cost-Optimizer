"""
AWS Lambda Entrypoint for Cloud FinOps Engine.
Handles scheduled sweeps, auto-parking triggers, and cost governance alerts.
"""

import json
import logging
import os
from typing import Any, Dict

from .orchestrator import FinOpsMasterOrchestrator

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda entrypoint.
    Triggered by scheduled EventBridge rules (Daily Cost Sweeps, Evening Park, Morning Wake).
    """
    logger.info(f"Received FinOps Event: {json.dumps(event, default=str)}")

    dry_run = os.environ.get("FINOPS_DRY_RUN", "true").lower() in ["true", "1", "yes"]
    s3_report_bucket = os.environ.get("FINOPS_REPORT_S3_BUCKET")
    sns_topic_arn = os.environ.get("FINOPS_SNS_TOPIC_ARN")
    slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    region = os.environ.get("AWS_REGION", "us-east-1")

    engine = FinOpsMasterOrchestrator(
        dry_run=dry_run,
        s3_report_bucket=s3_report_bucket,
        sns_topic_arn=sns_topic_arn,
        slack_webhook_url=slack_webhook_url,
        region=region,
    )

    action_type = event.get("action", "SWEEP").upper()

    try:
        if action_type == "PARK_STOP":
            result = engine.run_parking(action="STOP")
            return {
                "statusCode": 200,
                "body": json.dumps({"action": "PARK_STOP", "result": result.to_dict()}),
            }
        elif action_type == "PARK_START":
            result = engine.run_parking(action="START")
            return {
                "statusCode": 200,
                "body": json.dumps({"action": "PARK_START", "result": result.to_dict()}),
            }
        else:
            # Standard Daily Optimization Sweep
            sweep_result = engine.run_sweep()
            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "message": "FinOps sweep executed successfully",
                        "monthly_savings": sweep_result.summary.total_projected_monthly_savings,
                        "annual_savings": sweep_result.summary.total_projected_annual_savings,
                        "waste_pct": sweep_result.summary.waste_percentage,
                        "findings_count": len(sweep_result.findings),
                        "sha256": sweep_result.manifest.sha256_checksum,
                    }
                ),
            }
    except Exception as e:
        logger.error(f"Fatal error in FinOps Lambda handler: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }
