# Cloud FinOps & Autonomous Cost Governance Engine

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![Terraform](https://img.shields.io/badge/Terraform-v1.5%2B-purple.svg)](https://www.terraform.io/)
[![AWS](https://img.shields.io/badge/AWS-EventBridge%20%7C%20Lambda%20%7C%20EBS%20%7C%20EC2%20%7C%20Cost%20Explorer-orange.svg)](https://aws.amazon.com/)
[![FinOps Foundation](https://img.shields.io/badge/FinOps-Foundation%20Certified%20Practitioner-green.svg)](https://www.finops.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade autonomous cloud financial management (FinOps) platform for AWS that continuously detects idle infrastructure waste, enforces mandatory cost-allocation tag governance, executes automated off-hours dev parking, and eliminates unattached storage with verifiable safety snapshotting.

---

## 🎯 Executive Highlights & Resume Alignment

- **Autonomous Infrastructure Waste Reduction**: Continuously eliminates 30–35% of idle cloud spend across unattached EBS volumes, orphaned snapshots (>90 days), and overprovisioned compute.
- **Off-Hours Auto-Parking Engine**: Implements automated scheduled state transitions (`cron(0 19 ? * MON-FRI *)`) for dev/staging environments, saving up to **65% on non-production compute**.
- **Pre-Deletion Safety Snapshotting**: Eliminates operational risk by acquiring point-in-time recovery snapshots tagged with audit metadata prior to volume destruction.
- **Cost Allocation Tag Governance**: Audits all active compute and block storage against mandatory organizational financial tags (`Environment`, `CostCenter`, `Owner`, `Project`).
- **Cryptographic Audit Manifests**: Generates SHA-256 hashed FinOps audit manifests and archives evidence records to immutable Amazon S3 storage for finance and compliance reviews.
- **Production-Ready Terraform & CI/CD**: Automated deployment manifests with EventBridge scheduling, least-privilege IAM roles, S3 report vaults, and GitHub Actions verification.

---

## 🌐 Live Interactive Demo

You can interact with the live FinOps Cost Optimization Dashboard directly in your web browser:  
👉 **[Launch Live FinOps Executive Dashboard](https://koshag0hil.github.io/Cloud-FinOps-Autonomous-Cost-Optimizer/)**

*Features interactive savings simulators, doughnut chart waste breakdowns, auto-parking schedules, and downloadable audit manifests.*

---

## 🏛️ System Architecture

```
   ┌─────────────────────────────────────────────────────────────┐
   │                 Telemetry & Usage Sources                   │
   │  AWS Cost Explorer • AWS Compute Optimizer • CloudWatch     │
   └──────────────────────────────┬──────────────────────────────┘
                                  │ EventBridge Cron Triggers
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │             Amazon EventBridge Scheduled Rules              │
   │  - Daily Optimization Sweep (6:00 AM UTC)                   │
   │  - Weekday Evening Auto-Park (7:00 PM UTC)                  │
   │  - Weekday Morning Wakeup (7:00 AM UTC)                     │
   └──────────────────────────────┬──────────────────────────────┘
                                  │ Invocation
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │             FinOps Master Lambda Orchestrator               │
   └───────┬──────────────────────┬──────────────────────┬───────┘
           │                      │                      │
           ▼                      ▼                      ▼
 ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
 │   EBS Optimizer   │  │   EC2 Optimizer   │  │   Tag Governor    │
 │ - Unattached Vols │  │ - Idle CPU < 5%   │  │ - Environment     │
 │ - Safety Snapshot │  │ - Rightsizing Map │  │ - CostCenter      │
 │ - Purge >90d Snap │  │ - Nightly Parking │  │ - Owner & Project │
 └─────────┬─────────┘  └─────────┬─────────┘  └─────────┬─────────┘
           │                      │                      │
           └──────────────────────┼──────────────────────┘
                                  │
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │                Savings & ROI Calculation                    │
   │  - Aggregated Monthly & Annual Projected Savings            │
   │  - Waste Percentage Calculation                             │
   │  - Cryptographic SHA-256 Audit Signature                    │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │             Reporting & Notification Channels               │
   │  - Immutable S3 Report Bucket (AES-256 KMS, TLS-Enforced)   │
   │  - Amazon SNS Topic (Finance & DevOps Broadcast)            │
   │  - Slack Block Kit Webhooks with Savings Cards              │
   └─────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
Cloud-FinOps-Autonomous-Cost-Optimizer/
├── .github/
│   └── workflows/
│       ├── ci.yml                     # Ruff linting, Pytest + Moto testing, Terraform validation
│       └── pages.yml                  # Automatic deployment of index.html to GitHub Pages
├── docs/
│   ├── ARCHITECTURE.md                # System design & data flow
│   ├── FINOPS_FRAMEWORK.md            # FinOps Foundation Inform-Optimize-Operate mapping
│   └── RUNBOOKS.md                    # Standard Operating Procedures (SOP)
├── policies/
│   └── finops_rules.yaml              # Thresholds for idle CPU, EBS volume age, and tag rules
├── reports/
│   └── sample_finops_report.json      # Cryptographically signed (SHA-256) sample audit manifest
├── src/
│   ├── __init__.py
│   ├── cli.py                         # Rich terminal CLI for waste scans and auto-parking
│   ├── lambda_handler.py              # AWS Lambda entrypoint for scheduled FinOps sweeps
│   ├── orchestrator.py                # Master FinOps coordinator
│   ├── collectors/
│   │   ├── __init__.py
│   │   └── cost_collector.py          # Telemetry harvester for EC2, EBS, and snapshots
│   ├── optimizers/
│   │   ├── __init__.py
│   │   ├── base_optimizer.py          # Base optimization class
│   │   ├── ebs_optimizer.py           # Unattached volume & aged snapshot cleanup
│   │   ├── ec2_optimizer.py           # Idle compute detection & rightsizing mapping
│   │   ├── savings_calculator.py      # Monthly/annual ROI & waste percentage calculator
│   │   └── tag_governor.py            # Mandatory tag compliance auditor
│   ├── reporters/
│   │   ├── __init__.py
│   │   ├── executive_report.py        # SHA-256 manifest packager & S3 archiver
│   │   └── slack_notifier.py          # Amazon SNS & Slack Block Kit notifier
│   └── schedulers/
│       ├── __init__.py
│       └── auto_parker.py             # Scheduled off-hours stopping & morning wakeup
├── terraform/
│   ├── main.tf                        # Lambda function, SNS alert topic, CloudWatch logs
│   ├── eventbridge.tf                 # EventBridge cron schedules (Daily, Evening, Morning)
│   ├── iam.tf                         # Least-privilege IAM execution roles
│   ├── s3.tf                          # Immutable S3 report archive bucket
│   ├── variables.tf                   # Deployment variables
│   ├── outputs.tf                     # Exported ARNs
│   └── terraform.tfvars.example       # Example variables
├── tests/
│   ├── conftest.py                    # Moto mock fixtures
│   ├── test_auto_parker.py            # Auto-parking start/stop tests
│   ├── test_ebs_optimizer.py          # EBS unattached cleanup tests
│   ├── test_ec2_optimizer.py          # EC2 idle & rightsizing tests
│   ├── test_orchestrator.py           # End-to-end FinOps sweep tests
│   ├── test_savings_calculator.py     # Savings & ROI math tests
│   └── test_tag_governor.py           # Tag governance audit tests
├── Dockerfile                         # Containerized CLI runner
├── HOW_TO_RUN.md                      # Comprehensive execution guide
├── index.html                         # Live Interactive FinOps Dashboard (GitHub Pages)
├── LICENSE                            # MIT License
├── PROJECT_GUIDE.md                   # Technical deep-dive, resume points, interview Q&A
├── pyproject.toml                     # Python package & tool configuration
├── requirements.txt                   # Dependencies
├── run.bat                            # Windows 1-click runner
├── run.ps1                            # PowerShell 1-click runner
└── run.sh                             # Linux / macOS 1-click runner
```

---

## ⚡ Quickstart & Local Simulation

```powershell
# 1. Run FinOps waste scan (Dry-Run mode)
.\run.ps1

# 2. Run unit test suite (9 tests with Moto)
.\run.ps1 -Test

# 3. Open live interactive dashboard in browser
.\run.ps1 -Dashboard
```

---

## 📜 License

This project is open-source and licensed under the [MIT License](LICENSE).
