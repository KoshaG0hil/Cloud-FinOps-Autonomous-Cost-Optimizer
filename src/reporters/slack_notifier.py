"""
FinOps Alert & Notification Dispatcher.
Broadcasts cost optimization summaries, waste alerts, and auto-parking logs to Slack and Amazon SNS.
"""

import json
import logging
import urllib.request
from typing import Dict, Optional

import boto3
from botocore.exceptions import ClientError

from ..optimizers.savings_calculator import SavingsSummary

logger = logging.getLogger("finops.alerts")


class FinOpsAlertNotifier:
    """Dispatches executive summaries to Slack channels and SNS topics."""

    def __init__(
        self,
        sns_topic_arn: Optional[str] = None,
        slack_webhook_url: Optional[str] = None,
        session: Optional[boto3.Session] = None,
    ):
        self.sns_topic_arn = sns_topic_arn
        self.slack_webhook_url = slack_webhook_url
        self.sns = session.client("sns") if session and sns_topic_arn else None

    def dispatch_summary(self, summary: SavingsSummary, finding_count: int, dry_run: bool = True) -> Dict[str, bool]:
        results = {"console": True, "sns": False, "slack": False}
        mode_str = "[DRY-RUN]" if dry_run else "[ACTIVE]"

        logger.info(
            f"FinOps Summary {mode_str}: Projected Monthly Savings: ${summary.total_projected_monthly_savings:,.2f} "
            f"(${summary.total_projected_annual_savings:,.2f}/yr) | Waste: {summary.waste_percentage}%"
        )

        if self.sns_topic_arn:
            results["sns"] = self._send_sns(summary, finding_count, dry_run)

        if self.slack_webhook_url:
            results["slack"] = self._send_slack(summary, finding_count, dry_run)

        return results

    def _send_sns(self, summary: SavingsSummary, finding_count: int, dry_run: bool) -> bool:
        try:
            client = self.sns or boto3.client("sns")
            subject = f"AWS FinOps Optimization Report: ${summary.total_projected_monthly_savings:,.0f}/mo Saved"[:100]
            body = (
                f"=== AWS CLOUD FINOPS SAVINGS REPORT ===\n\n"
                f"Mode                     : {'DRY-RUN (Simulated)' if dry_run else 'ACTIVE REMEDIATION'}\n"
                f"Total Scanned Spend      : ${summary.total_scanned_monthly_spend:,.2f}/mo\n"
                f"Projected Monthly Savings: ${summary.total_projected_monthly_savings:,.2f}/mo\n"
                f"Projected Annual ROI     : ${summary.total_projected_annual_savings:,.2f}/year\n"
                f"Infrastructure Waste     : {summary.waste_percentage}%\n"
                f"Actionable Findings      : {finding_count}\n\n"
                f"Category Breakdown:\n"
                + "\n".join(f" - {k}: ${v:,.2f}/mo" for k, v in summary.category_breakdown.items())
            )
            client.publish(TopicArn=self.sns_topic_arn, Subject=subject, Message=body)
            return True
        except ClientError as e:
            logger.error(f"Failed to publish to SNS: {e}")
            return False

    def _send_slack(self, summary: SavingsSummary, finding_count: int, dry_run: bool) -> bool:
        try:
            mode_badge = "🟡 DRY-RUN" if dry_run else "🟢 ACTIVE REMEDIATION"
            payload = {
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"💰 AWS FinOps Savings Report ({mode_badge})",
                            "emoji": True,
                        },
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Monthly Savings:*\n`${summary.total_projected_monthly_savings:,.2f}`",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Annual ROI:*\n`${summary.total_projected_annual_savings:,.2f}`",
                            },
                            {"type": "mrkdwn", "text": f"*Waste Percentage:*\n`{summary.waste_percentage}%`"},
                            {"type": "mrkdwn", "text": f"*Scanned Assets:*\n`{finding_count} resources`"},
                        ],
                    },
                ]
            }
            req = urllib.request.Request(
                self.slack_webhook_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except Exception as e:
            logger.warning(f"Failed to send Slack alert: {e}")
            return False
