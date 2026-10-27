# FinOps Standard Operating Procedures (SOP) & Runbooks

## SOP-01: Unattached EBS Volume Disposal & Recovery

### Purpose
To eliminate waste from unattached block storage while preserving a verifiable safety recovery path.

### Execution Policy
- Volumes in `available` state for $\ge 7$ days are candidates for automated reclamation.
- Before executing `delete_volume`, the engine automatically triggers `create_snapshot` with tags:
  - `FinOps_SafetyBackup=true`
  - `SourceVolumeId=<VOL_ID>`
  - `DeletedAt=<TIMESTAMP>`

### Recovery Procedure
If a deleted volume is requested by an engineering team:
1. Locate the safety snapshot:
   ```bash
   aws ec2 describe-snapshots --filters "Name=tag:SourceVolumeId,Values=<VOL_ID>"
   ```
2. Recreate the volume from the snapshot:
   ```bash
   aws ec2 create-volume --snapshot-id <SNAPSHOT_ID> --availability-zone us-east-1a --volume-type gp3
   ```

---

## SOP-02: Configuring Auto-Parking for Non-Prod Workloads

### Purpose
To automatically stop non-production instances during off-hours (evenings and weekends) and wake them up during business hours.

### Enabling Auto-Parking on an EC2 Instance
Apply the `AutoPark=true` tag via AWS CLI:
```bash
aws ec2 create-tags --resources <INSTANCE_ID> --tags Key=AutoPark,Value=true
```

### Excluding an Instance from Auto-Parking
Remove or set the tag to false:
```bash
aws ec2 create-tags --resources <INSTANCE_ID> --tags Key=AutoPark,Value=false
```
