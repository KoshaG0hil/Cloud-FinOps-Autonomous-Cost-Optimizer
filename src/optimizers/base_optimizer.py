"""
Base Optimizer Interface.
Abstract structure for FinOps waste evaluators and remediation actions.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger("finops.optimizer")


@dataclass
class OptimizationFinding:
    """Individual cost anomaly, waste detection, or rightsizing opportunity."""

    finding_id: str
    category: str  # UNATTACHED_EBS, AGED_SNAPSHOT, IDLE_EC2, UNTAGGED_RESOURCE
    resource_type: str
    resource_id: str
    current_monthly_spend: float
    projected_monthly_savings: float
    recommended_action: str
    status: str  # IDENTIFIED, DRY_RUN_REMEDIATED, REMEDIATED, SKIPPED
    details: Dict[str, Any] = field(default_factory=dict)
    detected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "category": self.category,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "current_monthly_spend": self.current_monthly_spend,
            "projected_monthly_savings": self.projected_monthly_savings,
            "recommended_action": self.recommended_action,
            "status": self.status,
            "details": self.details,
            "detected_at": self.detected_at,
        }


class BaseFinOpsOptimizer(ABC):
    """Abstract base class for AWS cost optimization scanners."""

    def __init__(self, dry_run: bool = True, session: Optional[Any] = None, region: str = "us-east-1"):
        self.dry_run = dry_run
        self.session = session
        self.region = region
        self.logger = logging.getLogger(f"finops.{self.__class__.__name__}")

    @abstractmethod
    def evaluate_and_optimize(self) -> List[OptimizationFinding]:
        """Scans for waste and executes safe remediation or generates recommendations."""
        pass
