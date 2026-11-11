"""Deterministic rule engine: no AI call (FR-L7). Required sections and the
abstract word cap come from rules.yaml (FR-L6); claim structure (FR-L3) is
checked in code since it isn't a simple threshold."""
import re
from functools import lru_cache
from pathlib import Path

import yaml

from app.schemas import Finding

RULES_PATH = Path(__file__).with_name("rules.yaml")


@lru_cache
def load_rules() -> dict:
    return yaml.safe_load(RULES_PATH.read_text())


def _section_index(lines: list[str], sections: list[str]) -> dict[str, int]:
    wanted = {s.lower() for s in sections}
    idx: dict[str, int] = {}
    for i, line in enumerate(lines):
        key = line.rstrip(":").lower()
        if key in wanted and key not in idx:
            idx[key] = i
    return idx


def lint(lines: list[str], rules: dict | None = None) -> list[Finding]:
    rules = rules or load_rules()
    sections: list[str] = rules["sections"]
    idx = _section_index(lines, sections)
    findings = [Finding(severity="error", rule="missing-section", message=f"Missing section: {s}", location=s)
                for s in sections if s.lower() not in idx]

    present = [idx[s.lower()] for s in sections if s.lower() in idx]
    if present != sorted(present):
        findings.append(Finding(severity="error", rule="section-order",
                                 message="Sections are out of order; expected: " + ", ".join(sections)))

    if "abstract" in idx:
        end = min([i for i in present if i > idx["abstract"]], default=len(lines))
        words = len(" ".join(lines[idx["abstract"] + 1:end]).split())
        limit = rules.get("abstract_max_words", 150)
        if words > limit:
            findings.append(Finding(severity="warning", rule="abstract-length",
                                     message=f"Abstract is {words} words (max {limit})", location="Abstract"))

    if "claims" in idx:
        findings += _lint_claims(lines[idx["claims"] + 1:])
    return findings


_CLAIM_START = re.compile(r"^(\d+)\.\s")
_CLAIM_REF = re.compile(r"claims?\s+(\d+)")


def _lint_claims(claim_lines: list[str]) -> list[Finding]:
    claims = [(int(m.group(1)), c) for c in claim_lines if (m := _CLAIM_START.match(c))]
    if not claims:
        return [Finding(severity="error", rule="no-claims", message="Claims section has no numbered claims", location="Claims")]

    findings = []
    nums = [n for n, _ in claims]
    if nums != list(range(1, len(nums) + 1)):
        findings.append(Finding(severity="error", rule="claim-numbering",
                                 message=f"Claims not numbered consecutively from 1: {nums}", location="Claims"))

    for num, text in claims:
        if not text.rstrip().endswith("."):
            findings.append(Finding(severity="error", rule="claim-period",
                                     message=f"Claim {num} does not end with a period", location=f"Claim {num}"))
        for ref in (int(r) for r in _CLAIM_REF.findall(text)):
            if ref >= num or ref not in nums:
                findings.append(Finding(severity="error", rule="invalid-claim-reference",
                                         message=f"Claim {num} references claim {ref}, which doesn't precede it",
                                         location=f"Claim {num}"))
    return findings
