"""Unit tests for SavingsCalculator."""

from src.optimizers.base_optimizer import OptimizationFinding
from src.optimizers.savings_calculator import SavingsCalculator


def test_savings_calculator_aggregation():
    findings = [
        OptimizationFinding(
            finding_id="f1",
            category="UNATTACHED_EBS",
            resource_type="EBS_VOLUME",
            resource_id="vol-1",
            current_monthly_spend=80.0,
            projected_monthly_savings=80.0,
            recommended_action="DELETE",
            status="REMEDIATED",
        ),
        OptimizationFinding(
            finding_id="f2",
            category="IDLE_EC2",
            resource_type="EC2_INSTANCE",
            resource_id="i-1",
            current_monthly_spend=120.0,
            projected_monthly_savings=60.0,
            recommended_action="RIGHTSIZE",
            status="IDENTIFIED",
        ),
    ]

    summary = SavingsCalculator.calculate(findings)

    assert summary.total_scanned_monthly_spend == 200.0
    assert summary.total_projected_monthly_savings == 140.0
    assert summary.total_projected_annual_savings == 1680.0
    assert summary.waste_percentage == 70.0
    assert summary.category_breakdown["UNATTACHED_EBS"] == 80.0
    assert summary.category_breakdown["IDLE_EC2"] == 60.0
