"""Unit tests for FinOpsMasterOrchestrator and Lambda handler."""

import json

import boto3

from src.lambda_handler import lambda_handler
from src.orchestrator import FinOpsMasterOrchestrator


def test_orchestrator_full_sweep(mocked_aws):
    ec2 = boto3.client("ec2", region_name="us-east-1")

    # Create dummy unattached volume and idle dev instance
    ec2.create_volume(AvailabilityZone="us-east-1a", Size=50)
    ec2.run_instances(
        ImageId="ami-12345678",
        MinCount=1,
        MaxCount=1,
        InstanceType="t3.small",
        TagSpecifications=[{"ResourceType": "instance", "Tags": [{"Key": "Environment", "Value": "dev"}]}],
    )

    orchestrator = FinOpsMasterOrchestrator(dry_run=True, region="us-east-1")
    result = orchestrator.run_sweep()

    assert len(result.findings) >= 2
    assert result.summary.total_projected_monthly_savings > 0.0
    assert result.manifest.sha256_checksum != ""
    assert len(result.manifest.sha256_checksum) == 64


def test_lambda_handler_sweep_and_parking(mocked_aws):
    event_sweep = {"action": "SWEEP"}
    resp = lambda_handler(event_sweep, None)
    assert resp["statusCode"] == 200
    body = json.loads(resp["body"])
    assert "monthly_savings" in body

    event_parking = {"action": "PARK_STOP"}
    resp_park = lambda_handler(event_parking, None)
    assert resp_park["statusCode"] == 200
