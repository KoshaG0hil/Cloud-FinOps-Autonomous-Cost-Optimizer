"""
EC2 Idle & Rightsizing Optimizer.
Analyzes instance utilization, identifies idle compute, and computes rightsizing opportunities.
"""

from typing import List, Optional

import boto3
from botocore.exceptions import ClientError

from ..collectors.cost_collector import FinOpsTelemetryCollector
from .base_optimizer import BaseFinOpsOptimizer, OptimizationFinding


class Ec2IdleAndRightsizingOptimizer(BaseFinOpsOptimizer):
    """Detects underutilized compute instances and recommends rightsizing or auto-stopping."""

    def __init__(self, dry_run: bool = True, session: Optional[boto3.Session] = None, region: str = "us-east-1"):
        super().__init__(dry_run=dry_run, session=session, region=region)
        self.collector = FinOpsTelemetryCollector(session=session, region=region)
        self.ec2 = session.client("ec2", region_name=region) if session else boto3.client("ec2", region_name=region)

    def evaluate_and_optimize(self) -> List[OptimizationFinding]:
        findings: List[OptimizationFinding] = []
        instances = self.collector.collect_ec2_instances()

        # Rightsizing mapping table (overprovisioned -> recommended)
        rightsizing_map = {
            "m5.xlarge": {"target": "t3.medium", "savings_pct": 0.78},
            "m5.large": {"target": "t3.small", "savings_pct": 0.75},
            "c5.large": {"target": "t3.small", "savings_pct": 0.72},
            "t3.large": {"target": "t3.small", "savings_pct": 0.70},
            "t3.medium": {"target": "t3.micro", "savings_pct": 0.65},
        }

        for inst in instances:
            # Skip terminated or stopped instances
            if inst.status != "running":
                continue

            inst_id = inst.resource_id
            inst_type = inst.instance_type
            cpu = inst.average_cpu_utilization
            env = inst.tags.get("Environment", "development").lower()

            # Rule 1: Idle Instance (CPU < 5%) in Non-Prod -> Candidate for Nightly Parking
            if cpu < 5.0 and env in ["dev", "development", "staging", "test"]:
                # Parking dev instances overnight saves ~65% of monthly cost (12 hrs/weekday + weekends off)
                projected_savings = round(inst.estimated_monthly_cost * 0.65, 2)
                finding_id = f"finops-idle-park-{inst_id[-8:]}"

                if self.dry_run:
                    findings.append(
                        OptimizationFinding(
                            finding_id=finding_id,
                            category="IDLE_EC2",
                            resource_type="EC2_INSTANCE",
                            resource_id=inst_id,
                            current_monthly_spend=inst.estimated_monthly_cost,
                            projected_monthly_savings=projected_savings,
                            recommended_action="SCHEDULE_NIGHTLY_PARKING",
                            status="DRY_RUN_REMEDIATED",
                            details={
                                "cpu_utilization": cpu,
                                "environment": env,
                                "instance_type": inst_type,
                                "proposed_schedule": "Mon-Fri 7pm-7am + Weekends Off",
                            },
                        )
                    )
                else:
                    # Tag with AutoPark=true so the scheduler manages it
                    try:
                        self.ec2.create_tags(
                            Resources=[inst_id],
                            Tags=[{"Key": "AutoPark", "Value": "true"}],
                        )
                        findings.append(
                            OptimizationFinding(
                                finding_id=finding_id,
                                category="IDLE_EC2",
                                resource_type="EC2_INSTANCE",
                                resource_id=inst_id,
                                current_monthly_spend=inst.estimated_monthly_cost,
                                projected_monthly_savings=projected_savings,
                                recommended_action="SCHEDULE_NIGHTLY_PARKING",
                                status="REMEDIATED",
                                details={"tagged": "AutoPark=true"},
                            )
                        )
                    except ClientError as e:
                        self.logger.error(f"Failed to tag instance {inst_id}: {e}")

            # Rule 2: Overprovisioned Instance -> Rightsizing Recommendation
            elif inst_type in rightsizing_map:
                map_info = rightsizing_map[inst_type]
                target_type = map_info["target"]
                savings = round(inst.estimated_monthly_cost * map_info["savings_pct"], 2)
                finding_id = f"finops-rightsize-{inst_id[-8:]}"

                findings.append(
                    OptimizationFinding(
                        finding_id=finding_id,
                        category="IDLE_EC2",
                        resource_type="EC2_INSTANCE",
                        resource_id=inst_id,
                        current_monthly_spend=inst.estimated_monthly_cost,
                        projected_monthly_savings=savings,
                        recommended_action=f"RIGHTSIZE_TO_{target_type.upper()}",
                        status="IDENTIFIED",
                        details={
                            "current_type": inst_type,
                            "recommended_type": target_type,
                            "average_cpu": cpu,
                            "savings_percent": round(map_info["savings_pct"] * 100, 1),
                        },
                    )
                )

        return findings
