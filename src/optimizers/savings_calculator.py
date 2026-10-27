"""
FinOps Savings & ROI Calculator.
Computes projected monthly and annual financial savings, category breakdowns, and waste reduction percentages.
"""

from dataclasses import dataclass, field
from typing import Dict, List

from .base_optimizer import OptimizationFinding


@dataclass
class SavingsSummary:
    """Consolidated financial savings portfolio summary."""

    total_scanned_monthly_spend: float
    total_projected_monthly_savings: float
    total_projected_annual_savings: float
    waste_percentage: float
    category_breakdown: Dict[str, float] = field(default_factory=dict)
    findings_count_by_status: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "total_scanned_monthly_spend": self.total_scanned_monthly_spend,
            "total_projected_monthly_savings": self.total_projected_monthly_savings,
            "total_projected_annual_savings": self.total_projected_annual_savings,
            "waste_percentage": self.waste_percentage,
            "category_breakdown": self.category_breakdown,
            "findings_count_by_status": self.findings_count_by_status,
        }


class SavingsCalculator:
    """Calculates ROI and financial impact across FinOps optimization findings."""

    @staticmethod
    def calculate(findings: List[OptimizationFinding]) -> SavingsSummary:
        total_spend = sum(f.current_monthly_spend for f in findings)
        total_monthly_savings = sum(f.projected_monthly_savings for f in findings)
        total_annual_savings = total_monthly_savings * 12.0

        waste_pct = round((total_monthly_savings / total_spend) * 100.0, 1) if total_spend > 0 else 0.0

        cat_breakdown: Dict[str, float] = {}
        for f in findings:
            cat_breakdown[f.category] = round(cat_breakdown.get(f.category, 0.0) + f.projected_monthly_savings, 2)

        status_counts: Dict[str, int] = {}
        for f in findings:
            status_counts[f.status] = status_counts.get(f.status, 0) + 1

        return SavingsSummary(
            total_scanned_monthly_spend=round(total_spend, 2),
            total_projected_monthly_savings=round(total_monthly_savings, 2),
            total_projected_annual_savings=round(total_annual_savings, 2),
            waste_percentage=waste_pct,
            category_breakdown=cat_breakdown,
            findings_count_by_status=status_counts,
        )
