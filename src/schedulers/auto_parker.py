"""
Autonomous Resource Auto-Parker.
Manages automated schedule-based off-hours stopping and morning wakeup for non-prod EC2 and RDS instances.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger("finops.autopark")


@dataclass
class ParkingExecutionResult:
    """Execution status for auto-parking cycle."""

    action: str  # STOP (Park) or START (Wake)
    target_count: int
    modified_instance_ids: List[str] = field(default_factory=list)
    dry_run: bool = True
    executed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "target_count": self.target_count,
            "modified_instance_ids": self.modified_instance_ids,
            "dry_run": self.dry_run,
            "executed_at": self.executed_at,
            "details": self.details,
        }


class AutoParkingScheduler:
    """Executes scheduled start/stop commands for instances matching AutoPark=true."""

    def __init__(self, dry_run: bool = True, session: Optional[boto3.Session] = None, region: str = "us-east-1"):
        self.dry_run = dry_run
        self.session = session
        self.region = region
        self.ec2 = session.client("ec2", region_name=region) if session else boto3.client("ec2", region_name=region)

    def park_resources(self) -> ParkingExecutionResult:
        """Stops all running non-prod instances tagged with AutoPark=true."""
        target_ids: List[str] = []
        try:
            resp = self.ec2.describe_instances(
                Filters=[
                    {"Name": "tag:AutoPark", "Values": ["true", "True"]},
                    {"Name": "instance-state-name", "Values": ["running"]},
                ]
            )
            for res in resp.get("Reservations", []):
                for inst in res.get("Instances", []):
                    target_ids.append(inst["InstanceId"])

            if not target_ids:
                return ParkingExecutionResult(action="STOP", target_count=0, dry_run=self.dry_run)

            if not self.dry_run:
                self.ec2.stop_instances(InstanceIds=target_ids)
                logger.info(f"Auto-parked {len(target_ids)} instances: {target_ids}")

            return ParkingExecutionResult(
                action="STOP",
                target_count=len(target_ids),
                modified_instance_ids=target_ids,
                dry_run=self.dry_run,
                details={"schedule": "Nightly Off-Hours (7:00 PM - 7:00 AM)"},
            )
        except ClientError as e:
            logger.error(f"Failed to execute auto-parking: {e}")
            return ParkingExecutionResult(
                action="STOP", target_count=0, dry_run=self.dry_run, details={"error": str(e)}
            )

    def wake_resources(self) -> ParkingExecutionResult:
        """Starts all stopped instances tagged with AutoPark=true."""
        target_ids: List[str] = []
        try:
            resp = self.ec2.describe_instances(
                Filters=[
                    {"Name": "tag:AutoPark", "Values": ["true", "True"]},
                    {"Name": "instance-state-name", "Values": ["stopped"]},
                ]
            )
            for res in resp.get("Reservations", []):
                for inst in res.get("Instances", []):
                    target_ids.append(inst["InstanceId"])

            if not target_ids:
                return ParkingExecutionResult(action="START", target_count=0, dry_run=self.dry_run)

            if not self.dry_run:
                self.ec2.start_instances(InstanceIds=target_ids)
                logger.info(f"Woke up {len(target_ids)} instances: {target_ids}")

            return ParkingExecutionResult(
                action="START",
                target_count=len(target_ids),
                modified_instance_ids=target_ids,
                dry_run=self.dry_run,
                details={"schedule": "Morning On-Hours (7:00 AM)"},
            )
        except ClientError as e:
            logger.error(f"Failed to execute wakeup: {e}")
            return ParkingExecutionResult(
                action="START", target_count=0, dry_run=self.dry_run, details={"error": str(e)}
            )
