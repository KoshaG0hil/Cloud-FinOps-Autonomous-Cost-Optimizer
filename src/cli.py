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

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .orchestrator import FinOpsMasterOrchestrator

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


def cmd_scan(args):
    """Execute FinOps sweep across compute and storage assets."""
    orchestrator = FinOpsMasterOrchestrator(
        dry_run=args.dry_run,
        s3_report_bucket=args.s3_bucket,
        sns_topic_arn=args.sns_topic,
        slack_webhook_url=args.slack_webhook,
    )

    console.print(
        Panel(
            f"[bold yellow]Initiating Infrastructure FinOps Sweep[/bold yellow]\n"
            f"[dim]Mode: {'DRY-RUN (Safe Opportunity Modeling)' if args.dry_run else 'ACTIVE AUTONOMOUS REMEDIATION'}[/dim]",
            title="[FinOps Engine]",
            border_style="green",
        )
    )

    result = orchestrator.run_sweep()
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
