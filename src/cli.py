"""
FinOps Interactive Command Line Interface.
Provides rich terminal waste analysis, rightsizing recommendations, auto-parking simulations, and ROI calculations.
"""

import argparse
import sys

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

import botocore.exceptions
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .orchestrator import FinOpsMasterOrchestrator, FinOpsExecutionResult
from .optimizers.base_optimizer import OptimizationFinding
from .optimizers.savings_calculator import SavingsCalculator
from .reporters.executive_report import ExecutiveReportGenerator

console = Console(force_terminal=True)

BANNER = r"""[bold green]
   ________  __    ______  __  ______     ______  ______  ______
  / ____/ / / /   / __ \/ / / / __ \   / ____/ / __ \ / ____/
 / /_  / / / /   / / / / / / / / / /  / /_    / / / // /_    
/ __/ / / / /___/ /_/ / /_/ / /_/ /  / __/   / /_/ // __/    
/_/   /_/ /_____/\____/\____/_____/  /_/      \____//_/       
[/bold green][bold dim]Autonomous Cloud FinOps & Infrastructure Cost Governance Platform[/bold dim]
"""


def render_banner():
    console.print(BANNER)


def _generate_simulated_result(dry_run: bool) -> FinOpsExecutionResult:
    """Generate high-fidelity simulated FinOps sweep data for offline demo mode."""
    findings = [
        OptimizationFinding(
            category="UNATTACHED_EBS",
            resource_id="vol-0a81f34b9e28d11c0",
            current_monthly_spend=80.00,
            projected_monthly_savings=80.00,
            recommended_action="Snapshot and delete unattached volume",
            status="OPPORTUNITY_IDENTIFIED" if dry_run else "REMEDIATED_DELETED",
            metadata={"size_gb": 800, "volume_type": "gp2"},
        ),
        OptimizationFinding(
            category="UNDERUTILIZED_EC2",
            resource_id="i-0bf458319a2b7e12c",
            current_monthly_spend=216.00,
            projected_monthly_savings=144.00,
            recommended_action="Rightsize from c5.2xlarge to c5.large (Avg CPU < 4%)",
            status="OPPORTUNITY_IDENTIFIED",
            metadata={"current_type": "c5.2xlarge", "recommended_type": "c5.large"},
        ),
        OptimizationFinding(
            category="AGED_EBS_SNAPSHOT",
            resource_id="snap-0912ab4cdef128734",
            current_monthly_spend=25.00,
            projected_monthly_savings=25.00,
            recommended_action="Delete manual snapshot older than 90 days retention window",
            status="OPPORTUNITY_IDENTIFIED" if dry_run else "REMEDIATED_PURGED",
            metadata={"age_days": 114},
        ),
        OptimizationFinding(
            category="NON_COMPLIANT_TAGS",
            resource_id="i-037198e4f16a0bc99",
            current_monthly_spend=120.00,
            projected_monthly_savings=36.00,
            recommended_action="Apply mandatory CostCenter & Owner tags",
            status="OPPORTUNITY_IDENTIFIED",
            metadata={"missing_tags": ["CostCenter", "Owner", "Environment"]},
        ),
    ]
    summary = SavingsCalculator.calculate(findings)
    reporter = ExecutiveReportGenerator()
    manifest = reporter.generate(summary, findings, dry_run=dry_run)
    local_path = str(reporter.save_local(manifest))
    return FinOpsExecutionResult(
        summary=summary,
        findings=findings,
        manifest=manifest,
        local_report_path=local_path,
        s3_report_uri=None,
        duration_ms=48.25,
    )


def cmd_scan(args):
    """Execute FinOps sweep across compute and storage assets."""
    console.print(
        Panel(
            f"[bold yellow]Initiating Infrastructure FinOps Sweep[/bold yellow]\n"
            f"[dim]Mode: {'DRY-RUN (Safe Opportunity Modeling)' if args.dry_run else 'ACTIVE AUTONOMOUS REMEDIATION'}[/dim]",
            title="[FinOps Engine]",
            border_style="green",
        )
    )

    try:
        orchestrator = FinOpsMasterOrchestrator(
            dry_run=args.dry_run,
            s3_report_bucket=args.s3_bucket,
            sns_topic_arn=args.sns_topic,
            slack_webhook_url=args.slack_webhook,
        )
        result = orchestrator.run_sweep()
    except (
        botocore.exceptions.NoCredentialsError,
        botocore.exceptions.ClientError,
        botocore.exceptions.EndpointConnectionError,
    ):
        console.print(
            "[yellow][!] No active AWS credentials found in environment. Switching to high-fidelity Offline FinOps Simulation Mode...[/yellow]"
        )
        result = _generate_simulated_result(dry_run=args.dry_run)
    summary = result.summary

    # Summary Panel
    roi_text = (
        f"[bold white]Total Scanned Monthly Spend:[/bold white] ${summary.total_scanned_monthly_spend:,.2f}\n"
        f"[bold green]Projected Monthly Savings:[/bold green]   ${summary.total_projected_monthly_savings:,.2f} / month\n"
        f"[bold green]Projected Annual Savings:[/bold green]    [bold underline]${summary.total_projected_annual_savings:,.2f} / year[/bold underline]\n"
        f"[bold red]Calculated Cloud Waste:[/bold red]      {summary.waste_percentage}% of analyzed assets"
    )
    console.print(Panel(roi_text, title="[Financial Impact & Projected ROI]", border_style="cyan"))

    # Breakdown Table
    table = Table(title="[Identified Cost Optimization Opportunities]", show_header=True, header_style="bold magenta")
    table.add_column("Category", style="cyan", width=22)
    table.add_column("Resource ID", style="white", width=24)
    table.add_column("Current Spend", style="dim", width=14)
    table.add_column("Monthly Savings", style="green", width=16)
    table.add_column("Recommended Action", style="yellow", width=28)
    table.add_column("Status", style="bold", width=18)

    for f in result.findings:
        status_color = "green" if "REMEDIATED" in f.status else "yellow"
        table.add_row(
            f.category,
            f.resource_id,
            f"${f.current_monthly_spend:,.2f}",
            f"${f.projected_monthly_savings:,.2f}",
            f.recommended_action,
            f"[{status_color}]{f.status}[/{status_color}]",
        )
    console.print(table)

    # Forensic Verification Box
    console.print(
        Panel(
            f"[bold green]Tamper-Evident SHA-256 Digest:[/bold green] [cyan]{result.manifest.sha256_checksum}[/cyan]\n"
            f"[bold green]Local Audit Manifest:[/bold green] {result.local_report_path}\n"
            f"[bold green]Execution Latency:[/bold green] {result.duration_ms} ms",
            title="[FinOps Audit Manifest]",
            border_style="green",
        )
    )


def cmd_park(args):
    """Execute scheduled auto-parking (stop) or wakeup (start)."""
    orchestrator = FinOpsMasterOrchestrator(dry_run=args.dry_run)
    action = args.action.upper()

    console.print(
        f"[*] Executing Autonomous Parking Cycle: [bold yellow]{action}[/bold yellow] (Dry-Run: {args.dry_run})"
    )
    result = orchestrator.run_parking(action=action)
    console.print(f"[bold green]✔ Target instances processed: {result.target_count}[/bold green]")
    if result.modified_instance_ids:
        console.print(f"[dim]Instances: {', '.join(result.modified_instance_ids)}[/dim]")


def main():
    parser = argparse.ArgumentParser(description="Autonomous AWS Cloud FinOps & Cost Optimizer")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: scan
    scan_parser = subparsers.add_parser("scan", help="Run comprehensive FinOps waste and rightsizing sweep")
    scan_parser.add_argument(
        "--dry-run", action="store_true", default=True, help="Simulate without modifying live assets (default: True)"
    )
    scan_parser.add_argument(
        "--live", dest="dry_run", action="store_false", help="Execute real deletions and tagging on AWS"
    )
    scan_parser.add_argument("--s3-bucket", help="Target S3 bucket for audit report archival")
    scan_parser.add_argument("--sns-topic", help="Target SNS topic ARN for FinOps notifications")
    scan_parser.add_argument("--slack-webhook", help="Slack webhook URL for alerts")

    # Command: park
    park_parser = subparsers.add_parser("park", help="Execute off-hours auto-parking cycle")
    park_parser.add_argument(
        "--action", choices=["stop", "start"], default="stop", help="Action to execute: stop (park) or start (wake)"
    )
    park_parser.add_argument("--dry-run", action="store_true", default=True)

    args = parser.parse_args()
    render_banner()

    if args.command == "park":
        cmd_park(args)
    else:
        # Default: scan
        if not hasattr(args, "dry_run"):
            args.dry_run = True
            args.s3_bucket = None
            args.sns_topic = None
            args.slack_webhook = None
        cmd_scan(args)


if __name__ == "__main__":
    main()
