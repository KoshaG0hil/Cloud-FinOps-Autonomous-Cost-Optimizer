"""
FinOps Master Orchestrator.
Coordinates waste discovery, automated remediation, rightsizing analysis, and financial reporting.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import boto3

from .optimizers.base_optimizer import OptimizationFinding
from .optimizers.ebs_optimizer import EbsVolumeAndSnapshotOptimizer
from .optimizers.ec2_optimizer import Ec2IdleAndRightsizingOptimizer
from .optimizers.savings_calculator import SavingsCalculator, SavingsSummary
from .optimizers.tag_governor import TagGovernanceAuditor
from .reporters.executive_report import ExecutiveReportGenerator, FinOpsAuditManifest
from .reporters.slack_notifier import FinOpsAlertNotifier
from .schedulers.auto_parker import AutoParkingScheduler, ParkingExecutionResult

logger = logging.getLogger("finops.orchestrator")


@dataclass
class FinOpsExecutionResult:
    """Consolidated outcome of FinOps optimization run."""

    summary: SavingsSummary
    findings: List[OptimizationFinding]
    manifest: FinOpsAuditManifest
    local_report_path: Optional[str] = None
    s3_report_uri: Optional[str] = None
    notification_status: Dict[str, bool] = None
    parking_result: Optional[ParkingExecutionResult] = None
    duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary.to_dict(),
            "findings_count": len(self.findings),
            "manifest_sha256": self.manifest.sha256_checksum,
            "local_report_path": self.local_report_path,
            "s3_report_uri": self.s3_report_uri,
            "duration_ms": self.duration_ms,
        }


class FinOpsMasterOrchestrator:
    """The central engine coordinating all cost governance and autonomous parking sweeps."""

    def __init__(
        self,
        dry_run: bool = True,
        s3_report_bucket: Optional[str] = None,
        sns_topic_arn: Optional[str] = None,
        slack_webhook_url: Optional[str] = None,
        session: Optional[boto3.Session] = None,
        region: str = "us-east-1",
    ):
        self.dry_run = dry_run
        self.session = session
        self.region = region

        # Initialise Sub-Engines
        self.ebs_engine = EbsVolumeAndSnapshotOptimizer(dry_run=dry_run, session=session, region=region)
        self.ec2_engine = Ec2IdleAndRightsizingOptimizer(dry_run=dry_run, session=session, region=region)
        self.tag_engine = TagGovernanceAuditor(dry_run=dry_run, session=session, region=region)
        self.parker = AutoParkingScheduler(dry_run=dry_run, session=session, region=region)

        self.reporter = ExecutiveReportGenerator(s3_bucket=s3_report_bucket, session=session)
        self.notifier = FinOpsAlertNotifier(
            sns_topic_arn=sns_topic_arn,
            slack_webhook_url=slack_webhook_url,
            session=session,
        )

    def run_sweep(self) -> FinOpsExecutionResult:
        """Executes full optimization discovery and remediation sweep."""
        start_time = datetime.now(timezone.utc)
        all_findings: List[OptimizationFinding] = []

        # 1. EBS Volumes & Snapshots
        all_findings.extend(self.ebs_engine.evaluate_and_optimize())

        # 2. EC2 Idle & Rightsizing
        all_findings.extend(self.ec2_engine.evaluate_and_optimize())

        # 3. Tag Governance
        all_findings.extend(self.tag_engine.evaluate_and_optimize())

        # 4. Financial Calculations
        savings_summary = SavingsCalculator.calculate(all_findings)

        # 5. Report Packaging & SHA-256 Hashing
        manifest = self.reporter.generate(savings_summary, all_findings, dry_run=self.dry_run)
        local_path = str(self.reporter.save_local(manifest))
        s3_uri = self.reporter.upload_to_s3(manifest)

        # 6. Notifications
        dispatch_status = self.notifier.dispatch_summary(
            savings_summary, finding_count=len(all_findings), dry_run=self.dry_run
        )

        duration = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000.0

        return FinOpsExecutionResult(
            summary=savings_summary,
            findings=all_findings,
            manifest=manifest,
            local_report_path=local_path,
            s3_report_uri=s3_uri,
            notification_status=dispatch_status,
            duration_ms=round(duration, 2),
        )

    def run_parking(self, action: str = "STOP") -> ParkingExecutionResult:
        """Executes scheduled off-hours parking or morning wake cycle."""
        if action.upper() == "START":
            return self.parker.wake_resources()
        return self.parker.park_resources()
