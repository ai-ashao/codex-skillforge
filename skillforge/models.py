"""Structured validation result models."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


SEVERITIES = ("error", "warning", "info")


@dataclass(frozen=True)
class Finding:
    """One evidence-backed package validation finding."""

    code: str
    severity: str
    path: str
    message: str
    evidence: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "code": self.code,
            "severity": self.severity,
            "path": self.path,
            "message": self.message,
        }
        if self.evidence is not None:
            result["evidence"] = self.evidence
        return result


@dataclass
class ValidationResult:
    """Machine-readable result for one Skill package."""

    skill_path: Path
    findings: List[Finding] = field(default_factory=list)
    name: Optional[str] = None
    description: Optional[str] = None
    has_agents_metadata: bool = False
    has_skillforge_metadata: bool = False
    files_checked: int = 0

    @property
    def valid(self) -> bool:
        return not any(finding.severity == "error" for finding in self.findings)

    def add(
        self,
        code: str,
        severity: str,
        path: str,
        message: str,
        evidence: Optional[str] = None,
    ) -> None:
        if severity not in SEVERITIES:
            raise ValueError("unsupported finding severity: {}".format(severity))
        self.findings.append(Finding(code, severity, path, message, evidence))

    def summary(self) -> Dict[str, int]:
        counts = {severity + "s": 0 for severity in SEVERITIES}
        for finding in self.findings:
            counts[finding.severity + "s"] += 1
        return counts

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": "skill-package.v1",
            "valid": self.valid,
            "skill": {
                "path": str(self.skill_path),
                "name": self.name,
                "description": self.description,
                "has_agents_metadata": self.has_agents_metadata,
                "has_skillforge_metadata": self.has_skillforge_metadata,
                "files_checked": self.files_checked,
            },
            "summary": self.summary(),
            "findings": [finding.to_dict() for finding in self.findings],
        }
