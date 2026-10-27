"""Unit tests for AutoParkingScheduler."""

import boto3

from src.schedulers.auto_parker import AutoParkingScheduler


def test_auto_parker_stop_and_start(mocked_aws):
    ec2 = boto3.client("ec2", region_name="us-east-1")

    # Create instance tagged AutoPark=true
    inst = ec2.run_instances(
        ImageId="ami-12345678",
        MinCount=1,
        MaxCount=1,
        InstanceType="t3.small",
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [{"Key": "AutoPark", "Value": "true"}],
            }
        ],
    )["Instances"][0]
    inst_id = inst["InstanceId"]

    scheduler = AutoParkingScheduler(dry_run=False, region="us-east-1")

    # 1. Evening Cycle: Park (Stop)
    park_res = scheduler.park_resources()
    assert park_res.action == "STOP"
    assert park_res.target_count == 1
    assert inst_id in park_res.modified_instance_ids

    state = ec2.describe_instances(InstanceIds=[inst_id])["Reservations"][0]["Instances"][0]["State"]["Name"]
    assert state == "stopped"

    # 2. Morning Cycle: Wake (Start)
    wake_res = scheduler.wake_resources()
    assert wake_res.action == "START"
    assert wake_res.target_count == 1

    state = ec2.describe_instances(InstanceIds=[inst_id])["Reservations"][0]["Instances"][0]["State"]["Name"]
    assert state == "running"
