"""Unit tests for TagGovernanceAuditor."""

import boto3

from src.optimizers.tag_governor import TagGovernanceAuditor


def test_tag_governance_missing_tags(mocked_aws):
    ec2 = boto3.client("ec2", region_name="us-east-1")

    # Instance missing CostCenter and Project
    inst = ec2.run_instances(
        ImageId="ami-12345678",
        MinCount=1,
        MaxCount=1,
        InstanceType="t3.micro",
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [{"Key": "Environment", "Value": "prod"}, {"Key": "Owner", "Value": "DevOps"}],
            }
        ],
    )["Instances"][0]
    inst_id = inst["InstanceId"]

    auditor = TagGovernanceAuditor(dry_run=True, region="us-east-1")
    findings = auditor.evaluate_and_optimize()

    untagged = [f for f in findings if f.resource_id == inst_id]
    assert len(untagged) == 1
    f = untagged[0]
    assert f.category == "UNTAGGED_RESOURCE"
    assert "CostCenter" in f.details["missing_tags"]
    assert "Project" in f.details["missing_tags"]
