"""Unit tests for EbsVolumeAndSnapshotOptimizer."""

import boto3

from src.optimizers.ebs_optimizer import EbsVolumeAndSnapshotOptimizer


def test_ebs_unattached_cleanup_live(mocked_aws):
    ec2 = boto3.client("ec2", region_name="us-east-1")

    # Create unattached volume
    vol = ec2.create_volume(
        AvailabilityZone="us-east-1a",
        Size=100,
        VolumeType="gp3",
    )
    vol_id = vol["VolumeId"]

    optimizer = EbsVolumeAndSnapshotOptimizer(dry_run=False, region="us-east-1")
    findings = optimizer.evaluate_and_optimize()

    assert len(findings) >= 1
    unattached_findings = [f for f in findings if f.resource_id == vol_id]
    assert len(unattached_findings) == 1

    f = unattached_findings[0]
    assert f.category == "UNATTACHED_EBS"
    assert f.projected_monthly_savings == 8.0  # 100GB * 0.08
    assert f.status == "REMEDIATED"

    # Verify backup snapshot was created before deletion
    snaps = ec2.describe_snapshots(OwnerIds=["self"])["Snapshots"]
    assert len(snaps) >= 1

    # Verify volume was deleted
    vols = ec2.describe_volumes()["Volumes"]
    assert vol_id not in [v["VolumeId"] for v in vols]


def test_ebs_unattached_dry_run(mocked_aws):
    ec2 = boto3.client("ec2", region_name="us-east-1")
    vol = ec2.create_volume(AvailabilityZone="us-east-1a", Size=50)
    vol_id = vol["VolumeId"]

    optimizer = EbsVolumeAndSnapshotOptimizer(dry_run=True, region="us-east-1")
    findings = optimizer.evaluate_and_optimize()

    unattached = [f for f in findings if f.resource_id == vol_id]
    assert len(unattached) == 1
    assert unattached[0].status == "DRY_RUN_REMEDIATED"

    # Verify volume was NOT deleted in dry-run
    vols = ec2.describe_volumes()["Volumes"]
    assert vol_id in [v["VolumeId"] for v in vols]
