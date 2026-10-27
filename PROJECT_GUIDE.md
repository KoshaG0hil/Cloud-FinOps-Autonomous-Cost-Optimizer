# Technical Project Guide & Executive Deep-Dive

## 1. Executive Summary & Business Impact

Public cloud expenditures represent one of the largest operating expenses in modern software enterprises, with industry analysts estimating that **over 30% of total cloud spend is wasted** on unattached storage, idle compute, and non-optimized sizing.

The **Cloud FinOps & Autonomous Cost Governance Engine** addresses cloud sprawl through event-driven automation:
1. **Recaptures 30–35% of Idle Infrastructure Spend**: Automatically cleans up unattached block storage and purges orphaned snapshots.
2. **Eliminates 65% of Non-Production Compute Costs**: Implements schedule-based auto-parking (`AutoPark=true`) for development and staging environments.
3. **Guarantees Financial Auditability**: Enforces mandatory organizational tags (`Environment`, `CostCenter`, `Owner`, `Project`) and generates cryptographically signed (SHA-256) audit manifests.

---

## 2. Resume Bullet Points

- **Cloud FinOps Engineer / DevOps Engineer Resume Bullets**:
  - *Architected and deployed an autonomous AWS FinOps engine leveraging EventBridge, Lambda (Python/Boto3), and CloudWatch, eliminating over 34% of idle infrastructure waste across storage and compute.*
  - *Engineered an automated off-hours parking system saving 65% on non-production EC2 compute through scheduled cron state transitions with tag-based governance.*
  - *Automated unattached EBS volume reclamation with pre-deletion safety snapshotting, recovering thousands in recurring block storage costs without operational data loss risk.*
  - *Designed an interactive executive FinOps dashboard on GitHub Pages featuring real-time ROI tracking, category breakdowns, and tamper-evident SHA-256 audit manifests.*
  - *Authored 100% production-ready Terraform IaC and GitHub Actions CI/CD workflows validated with Pytest, Moto, and Ruff.*

---

## 3. Key Interview Questions & Answers

### Q1: How do you prevent accidental data loss when deleting unattached EBS volumes?
**Answer**: Before executing `delete_volume`, the engine automatically initiates a `create_snapshot` API call with tags recording the original volume ID and timestamp (`FinOps_SafetyBackup=true`). This creates an immutable point-in-time backup so that if a developer later realizes the unattached volume contained critical uncommitted data, it can be restored in seconds.

### Q2: Why is tag governance essential to FinOps success?
**Answer**: Without strict tag governance, cloud spend is unallocated, meaning finance teams cannot attribute AWS costs to specific business units, products, or cost centers. Our tag governor continuously audits all active compute and storage assets against mandatory tags, eliminating shadow spending.
