"""
EBS Volume & Snapshot Optimizer.
Identifies unattached EBS storage and orphaned snapshots, creates safety backups, and cleans up idle assets.
"""

from datetime import datetime, timezone
from typing import List, Optional

import boto3
from botocore.exceptions import ClientError

from ..collectors.cost_collector import FinOpsTelemetryCollector
from .base_optimizer import BaseFinOpsOptimizer, OptimizationFinding


class EbsVolumeAndSnapshotOptimizer(BaseFinOpsOptimizer):
    """Detects and cleans unattached EBS volumes and aged snapshots."""

    def __init__(self, dry_run: bool = True, session: Optional[boto3.Session] = None, region: str = "us-east-1"):
        super().__init__(dry_run=dry_run, session=session, region=region)
        self.collector = FinOpsTelemetryCollector(session=session, region=region)
        self.ec2 = session.client("ec2", region_name=region) if session else boto3.client("ec2", region_name=region)

    def evaluate_and_optimize(self) -> List[OptimizationFinding]:
        findings: List[OptimizationFinding] = []

        # ----------------------------------------------------------------------
        # 1. Unattached EBS Volumes
        # ----------------------------------------------------------------------
        unattached_vols = self.collector.collect_ebs_volumes()
        for vol in unattached_vols:
            vol_id = vol.resource_id
            savings = vol.estimated_monthly_cost
            finding_id = f"finops-ebs-{vol_id[-8:]}"

            if self.dry_run:
                findings.append(
                    OptimizationFinding(
                        finding_id=finding_id,
                        category="UNATTACHED_EBS",
                        resource_type="EBS_VOLUME",
                        resource_id=vol_id,
                        current_monthly_spend=savings,
                        projected_monthly_savings=savings,
                        recommended_action="SNAPSHOT_AND_DELETE",
                        status="DRY_RUN_REMEDIATED",
                        details={
                            "size_gb": vol.size_gb,
                            "simulated_backup_snapshot": f"snap-safety-{vol_id[-8:]}",
                            "action": "Simulated safety backup snapshot then volume deletion",
                        },
                    )
                )
            else:
                try:
                    # Create safety recovery snapshot first
                    now_str = datetime.now(timezone.utc).isoformat()
                    snap_resp = self.ec2.create_snapshot(
                        VolumeId=vol_id,
                        Description=f"FinOps pre-deletion safety snapshot for unattached volume {vol_id}",
                    )
                    created_snap_id = snap_resp.get("SnapshotId", "unknown")

                    try:
                        self.ec2.create_tags(
                            Resources=[created_snap_id],
                            Tags=[
                                {"Key": "FinOps_SafetyBackup", "Value": "true"},
                                {"Key": "SourceVolumeId", "Value": vol_id},
                                {"Key": "DeletedAt", "Value": now_str},
                            ],
                        )
                    except ClientError:
                        pass

                    # Delete the unattached volume
                    self.ec2.delete_volume(VolumeId=vol_id)

                    findings.append(
                        OptimizationFinding(
                            finding_id=finding_id,
                            category="UNATTACHED_EBS",
                            resource_type="EBS_VOLUME",
                            resource_id=vol_id,
                            current_monthly_spend=savings,
                            projected_monthly_savings=savings,
                            recommended_action="SNAPSHOT_AND_DELETE",
                            status="REMEDIATED",
                            details={
                                "size_gb": vol.size_gb,
                                "created_backup_snapshot": created_snap_id,
                            },
                        )
                    )
                except ClientError as e:
                    self.logger.error(f"Failed to optimize volume {vol_id}: {e}")
                    findings.append(
                        OptimizationFinding(
                            finding_id=finding_id,
                            category="UNATTACHED_EBS",
                            resource_type="EBS_VOLUME",
                            resource_id=vol_id,
                            current_monthly_spend=savings,
                            projected_monthly_savings=0.0,
                            recommended_action="SNAPSHOT_AND_DELETE",
                            status="SKIPPED",
                            details={"error": str(e)},
                        )
                    )

        # ----------------------------------------------------------------------
        # 2. Aged / Orphaned Snapshots (>90 days)
        # ----------------------------------------------------------------------
        aged_snaps = self.collector.collect_orphaned_snapshots(max_age_days=90)
        for snap in aged_snaps:
            snap_id = snap.resource_id
            savings = snap.estimated_monthly_cost
            finding_id = f"finops-snap-{snap_id[-8:]}"

            # Check exemptions
            if any(k in ["RetainIndefinitely", "ComplianceArchive"] for k in snap.tags):
                continue

            if self.dry_run:
                findings.append(
                    OptimizationFinding(
                        finding_id=finding_id,
                        category="AGED_SNAPSHOT",
                        resource_type="EBS_SNAPSHOT",
                        resource_id=snap_id,
                        current_monthly_spend=savings,
                        projected_monthly_savings=savings,
                        recommended_action="PURGE_OBSOLETE_SNAPSHOT",
                        status="DRY_RUN_REMEDIATED",
                        details={"size_gb": snap.size_gb, "age_days": snap.raw_metadata.get("age_days", 90)},
                    )
                )
            else:
                try:
                    self.ec2.delete_snapshot(SnapshotId=snap_id)
                    findings.append(
                        OptimizationFinding(
                            finding_id=finding_id,
                            category="AGED_SNAPSHOT",
                            resource_type="EBS_SNAPSHOT",
                            resource_id=snap_id,
                            current_monthly_spend=savings,
                            projected_monthly_savings=savings,
                            recommended_action="PURGE_OBSOLETE_SNAPSHOT",
                            status="REMEDIATED",
                            details={"size_gb": snap.size_gb},
                        )
                    )
                except ClientError as e:
                    self.logger.error(f"Failed to delete snapshot {snap_id}: {e}")

        return findings
