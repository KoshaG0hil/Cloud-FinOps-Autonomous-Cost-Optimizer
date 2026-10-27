"""Unit tests for Ec2IdleAndRightsizingOptimizer."""

import boto3

from src.optimizers.ec2_optimizer import Ec2IdleAndRightsizingOptimizer


def test_ec2_idle_dev_autopark(mocked_aws):
    ec2 = boto3.client("ec2", region_name="us-east-1")

    # Launch dev instance
    inst = ec2.run_instances(
        ImageId="ami-12345678",
        MinCount=1,
        MaxCount=1,
        InstanceType="t3.medium",
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [{"Key": "Environment", "Value": "development"}],
            }
        ],
    )["Instances"][0]
    inst_id = inst["InstanceId"]

    optimizer = Ec2IdleAndRightsizingOptimizer(dry_run=False, region="us-east-1")
    findings = optimizer.evaluate_and_optimize()

    dev_findings = [f for f in findings if f.resource_id == inst_id]
    assert len(dev_findings) >= 1
    f = dev_findings[0]
    assert f.recommended_action == "SCHEDULE_NIGHTLY_PARKING"
    assert f.status == "REMEDIATED"

    # Verify AutoPark tag applied
    desc = ec2.describe_instances(InstanceIds=[inst_id])["Reservations"][0]["Instances"][0]
    tags = {t["Key"]: t["Value"] for t in desc.get("Tags", [])}
    assert tags.get("AutoPark") == "true"


def test_ec2_rightsizing_evaluation(mocked_aws):
    ec2 = boto3.client("ec2", region_name="us-east-1")

    # Launch overprovisioned m5.xlarge production instance
    inst = ec2.run_instances(
        ImageId="ami-12345678",
        MinCount=1,
        MaxCount=1,
        InstanceType="m5.xlarge",
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [{"Key": "Environment", "Value": "production"}],
            }
        ],
    )["Instances"][0]
    inst_id = inst["InstanceId"]

    optimizer = Ec2IdleAndRightsizingOptimizer(dry_run=True, region="us-east-1")
    findings = optimizer.evaluate_and_optimize()

    prod_findings = [f for f in findings if f.resource_id == inst_id]
    assert len(prod_findings) >= 1
    f = prod_findings[0]
    assert "RIGHTSIZE" in f.recommended_action
    assert f.projected_monthly_savings > 100.0
