# FinOps Foundation Alignment & Lifecycle Framework

This platform implements the core phases established by the **FinOps Foundation Framework**:

```
           ┌────────────────────────┐
           │        INFORM          │
           │ - Telemetry Ingestion  │
           │ - Tag Governance       │
           │ - Spend Attribution    │
           └───────────┬────────────┘
                       │
                       ▼
           ┌────────────────────────┐
           │        OPTIMIZE        │
           │ - Waste Identification │
           │ - Rightsizing Mapping  │
           │ - Rate/Volume Savings  │
           └───────────┬────────────┘
                       │
                       ▼
           ┌────────────────────────┐
           │        OPERATE         │
           │ - Autonomous Parking   │
           │ - Garbage Collection   │
           │ - Continuous Auditing  │
           └────────────────────────┘
```

---

## 1. Inform Phase: Full Allocation Visibility
- **Continuous Tag Auditing**: Ensures 100% of provisioned infrastructure carries mandatory cost-allocation tags (`Environment`, `CostCenter`, `Owner`, `Project`), eliminating "unallocated cloud spend".
- **Real-Time Anomaly Visibility**: Dispatches financial impact telemetry directly to DevOps and engineering leads via Slack Block Kit and Amazon SNS.

## 2. Optimize Phase: Opportunity Identification
- **Unit Economic Rightsizing**: Evaluates instances utilizing $<5\%$ CPU and maps them to right-sized compute classes (e.g. `m5.xlarge` $\rightarrow$ `t3.medium`, saving $78\%$).
- **Storage Lifecycle Compaction**: Identifies orphaned snapshots older than 90 days and unattached block storage.

## 3. Operate Phase: Autonomous Execution
- **Off-Hours Auto-Parking**: Enforces automated operational schedules (`cron(0 19 ? * MON-FRI *)`) for development environments, recovering up to $65\%$ of idle non-production cloud spend.
- **Pre-Deletion Safety Snapshots**: Eliminates operational risk by capturing safety recovery snapshots before permanently deleting unattached volumes.
