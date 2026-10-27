# How to Run & Validate the Cloud FinOps Platform

## 1. Quickstart (Local Simulation Mode)

Run comprehensive waste scans and auto-parking simulations locally without modifying live AWS infrastructure.

### Windows (PowerShell)
```powershell
# Run full FinOps cost optimization scan (Dry-Run mode)
.\run.ps1

# Run auto-parking simulation (Evening Stop)
.\run.ps1 -Command park -Action stop

# Launch the live FinOps executive dashboard in your browser
.\run.ps1 -Dashboard
```

### macOS / Linux
```bash
chmod +x run.sh

# Run FinOps scan
./run.sh

# Run auto-parking simulation
./run.sh park stop

# Open dashboard
./run.sh dashboard
```

---

## 2. Automated Test Suite Execution

Run the 9 unit and integration tests powered by `moto` in-memory AWS mocks:

```powershell
.\run.ps1 -Test
```

Expected output:
```
tests/test_auto_parker.py::test_auto_parker_stop_and_start PASSED
tests/test_ebs_optimizer.py::test_ebs_unattached_cleanup_live PASSED
tests/test_ec2_optimizer.py::test_ec2_idle_dev_autopark PASSED
tests/test_orchestrator.py::test_orchestrator_full_sweep PASSED
tests/test_savings_calculator.py::test_savings_calculator_aggregation PASSED
tests/test_tag_governor.py::test_tag_governance_missing_tags PASSED
============================== 9 passed in 8.07s ==============================
```

---

## 3. Terraform Deployment to AWS

To deploy the automated schedule rules, Lambda functions, and S3 report vaults:

```bash
cd terraform
terraform init
terraform plan
terraform apply
```
