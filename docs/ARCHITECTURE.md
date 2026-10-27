# Cloud FinOps Architecture & Technical Specifications

## 1. System Overview

The **Cloud FinOps & Autonomous Cost Governance Engine** operates on continuous telemetry ingestion, automated waste identification, and schedule-based workload parking to maintain maximum financial efficiency across AWS environments.

---

## 2. Event-Driven & Scheduled Data Flow

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

## 3. Financial Waste Reduction Vectors

1. **Unattached EBS Volumes**: Discovers volumes in `available` state. Executes pre-deletion safety snapshot and removes volume, recapturing \$0.08–\$0.125 per GB/month.
2. **Orphaned EBS Snapshots**: Automatically identifies account-owned snapshots older than 90 days with no active AMI attachment, eliminating \$0.05 per GB/month storage waste.
3. **Autonomous Off-Hours Parking**: Automatically stops non-prod development and staging instances overnight (7:00 PM to 7:00 AM) and during weekends, eliminating up to **65% of compute spend**.
4. **Compute Rightsizing**: Analyzes CloudWatch CPU metrics (<5%) and maps overprovisioned `m5`/`c5` instances to cost-efficient `t3` burstable families.
5. **Cost Allocation Tag Governance**: Continuously audits compliance against organizational financial tagging standards (`Environment`, `CostCenter`, `Owner`, `Project`).
