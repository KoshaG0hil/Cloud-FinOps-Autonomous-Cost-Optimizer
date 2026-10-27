"""Pytest fixtures for FinOps engine tests."""

import os

import boto3
import pytest
from moto import mock_aws


@pytest.fixture(autouse=True)
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["AWS_REGION"] = "us-east-1"


@pytest.fixture
def mocked_aws():
    with mock_aws():
        yield


@pytest.fixture
def ec2_client(mocked_aws):
    return boto3.client("ec2", region_name="us-east-1")


@pytest.fixture
def s3_client(mocked_aws):
    return boto3.client("s3", region_name="us-east-1")


@pytest.fixture
def sns_client(mocked_aws):
    return boto3.client("sns", region_name="us-east-1")
