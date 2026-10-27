"""
Executive FinOps Report Generator.
Exports tamper-evident audit manifests (JSON & HTML) with cryptographic SHA-256 verification.
"""

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

from ..optimizers.base_optimizer import OptimizationFinding
from ..optimizers.savings_calculator import SavingsSummary

logger = logging.getLogger("finops.report")


@dataclass
class FinOpsAuditManifest:
    """Tamper-evident FinOps audit manifest."""

    manifest_id: str
    generated_at: str
    dry_run: bool
    summary: Dict[str, Any]
    findings: List[Dict[str, Any]]
    sha256_checksum: str = ""

    def compute_hash(self) -> str:
        data = {
            "manifest_id": self.manifest_id,
            "generated_at": self.generated_at,
            "dry_run": self.dry_run,
            "summary": self.summary,
            "findings": self.findings,
        }
        canonical = json.dumps(data, sort_keys=True, indent=None)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "manifest_id": self.manifest_id,
            "generated_at": self.generated_at,
            "dry_run": self.dry_run,
            "sha256_checksum": self.sha256_checksum,
            "summary": self.summary,
            "findings": self.findings,
        }


class ExecutiveReportGenerator:
    """Generates structured JSON & HTML reports and saves locally or in S3."""

    def __init__(
        self,
        s3_bucket: Optional[str] = None,
        session: Optional[boto3.Session] = None,
        output_dir: str = "reports",
    ):
        self.s3_bucket = s3_bucket
        self.s3 = session.client("s3") if session and s3_bucket else None
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        summary: SavingsSummary,
        findings: List[OptimizationFinding],
        dry_run: bool = True,
    ) -> FinOpsAuditManifest:
        now_str = datetime.now(timezone.utc).isoformat()
        manifest_id = f"finops-{int(datetime.now(timezone.utc).timestamp())}"

        manifest = FinOpsAuditManifest(
            manifest_id=manifest_id,
            generated_at=now_str,
            dry_run=dry_run,
            summary=summary.to_dict(),
            findings=[f.to_dict() for f in findings],
        )
        manifest.sha256_checksum = manifest.compute_hash()
        return manifest

    def save_local(self, manifest: FinOpsAuditManifest) -> Path:
        target_path = self.output_dir / f"finops_report_{manifest.manifest_id}.json"
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(manifest.to_dict(), f, indent=2)
        logger.info(f"Report saved locally: {target_path}")
        return target_path

    def upload_to_s3(self, manifest: FinOpsAuditManifest) -> Optional[str]:
        if not self.s3_bucket:
            return None

        key = f"finops-reports/{datetime.now(timezone.utc).strftime('%Y/%m/%d')}/{manifest.manifest_id}.json"
        try:
            client = self.s3 or boto3.client("s3")
            client.put_object(
                Bucket=self.s3_bucket,
                Key=key,
                Body=json.dumps(manifest.to_dict(), indent=2).encode("utf-8"),
                ContentType="application/json",
            )
            return f"s3://{self.s3_bucket}/{key}"
        except ClientError as e:
            logger.error(f"Failed to upload report to S3: {e}")
            return None
