"""
Cost Allocation Tag Governance Auditor.
Audits AWS resources against mandatory organizational FinOps tags (Environment, Owner, CostCenter, Project).
"""

from typing import List, Optional

import boto3

from ..collectors.cost_collector import FinOpsTelemetryCollector
from .base_optimizer import BaseFinOpsOptimizer, OptimizationFinding


class TagGovernanceAuditor(BaseFinOpsOptimizer):
    """Enforces cost-allocation tag compliance across cloud resources."""

    MANDATORY_TAGS = ["Environment", "Owner", "CostCenter", "Project"]

    def __init__(self, dry_run: bool = True, session: Optional[boto3.Session] = None, region: str = "us-east-1"):
        super().__init__(dry_run=dry_run, session=session, region=region)
        self.collector = FinOpsTelemetryCollector(session=session, region=region)

    def evaluate_and_optimize(self) -> List[OptimizationFinding]:
        findings: List[OptimizationFinding] = []

        # Audit EC2 instances
        instances = self.collector.collect_ec2_instances()
        for inst in instances:
            missing_tags = [t for t in self.MANDATORY_TAGS if t not in inst.tags]
            if missing_tags:
                findings.append(
                    OptimizationFinding(
                        finding_id=f"finops-tag-ec2-{inst.resource_id[-8:]}",
                        category="UNTAGGED_RESOURCE",
                        resource_type="EC2_INSTANCE",
                        resource_id=inst.resource_id,
                        current_monthly_spend=inst.estimated_monthly_cost,
                        projected_monthly_savings=0.0,
                        recommended_action="APPLY_MANDATORY_COST_TAGS",
                        status="IDENTIFIED",
                        details={
                            "missing_tags": missing_tags,
                            "existing_tags": list(inst.tags.keys()),
                            "impact": "Unallocated cloud spend / untracked departmental cost",
                        },
                    )
                )

        # Audit EBS volumes
        volumes = self.collector.collect_ebs_volumes()
        for vol in volumes:
            missing_tags = [t for t in self.MANDATORY_TAGS if t not in vol.tags]
            if missing_tags:
                findings.append(
                    OptimizationFinding(
                        finding_id=f"finops-tag-ebs-{vol.resource_id[-8:]}",
                        category="UNTAGGED_RESOURCE",
                        resource_type="EBS_VOLUME",
                        resource_id=vol.resource_id,
                        current_monthly_spend=vol.estimated_monthly_cost,
                        projected_monthly_savings=0.0,
                        recommended_action="APPLY_MANDATORY_COST_TAGS",
                        status="IDENTIFIED",
                        details={
                            "missing_tags": missing_tags,
                            "existing_tags": list(vol.tags.keys()),
                        },
                    )
                )

        return findings
