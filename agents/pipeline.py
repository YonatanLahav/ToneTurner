"""
Multi-agent code review pipeline for ToneTurner.

Pipeline:
  BugFinderAgent  →  BugValidatorAgent  →  BugFixerAgent  →  PRApproverAgent

Run:
    cd toneturner
    ANTHROPIC_API_KEY=<key> python -m agents.pipeline
"""

import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import anthropic

# ── Config ─────────────────────────────────────────────────────────────────────

MODEL = "claude-opus-4-7"
ROOT  = Path(__file__).parent.parent


def _client() -> anthropic.Anthropic:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise EnvironmentError("ANTHROPIC_API_KEY is not set.")
    return anthropic.Anthropic(api_key=key)


def _call(client: anthropic.Anthropic, system: str, user: str) -> str:
    """Single streaming call; returns full text response."""
    with client.messages.stream(
        model=MODEL,
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=system,
        messages=[{"role": "user", "content": user}],
    ) as stream:
        return stream.get_final_message().content[-1].text


# ── Shared context ──────────────────────────────────────────────────────────────

def _read_codebase() -> str:
    """Return all Python source files as a single annotated string."""
    parts = []
    for path in sorted(ROOT.rglob("*.py")):
        if any(skip in path.parts for skip in ("venv", "__pycache__", "agents")):
            continue
        rel = path.relative_to(ROOT)
        parts.append(f"# === {rel} ===\n{path.read_text()}")
    return "\n\n".join(parts)


def _git_diff() -> str:
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD~1", "HEAD", "--stat"],
            capture_output=True, text=True, cwd=ROOT
        )
        return result.stdout.strip() or "(no recent diff)"
    except Exception:
        return "(git diff unavailable)"


# ── Dataclasses ─────────────────────────────────────────────────────────────────

@dataclass
class Bug:
    file: str
    line_hint: str
    description: str
    severity: str      # critical | high | medium | low


@dataclass
class ValidationResult:
    confirmed_bugs: list[Bug]
    false_positives: list[Bug]
    reasoning: str


@dataclass
class Fix:
    bug: Bug
    patch: str         # description of the fix applied
    confidence: str    # high | medium | low


@dataclass
class PRDecision:
    approved: bool
    summary: str
    remaining_concerns: list[str]


# ── Agent 1: Bug Finder ─────────────────────────────────────────────────────────

def bug_finder_agent(client: anthropic.Anthropic, codebase: str) -> list[Bug]:
    print("\n🔍 [1/4] BugFinderAgent — scanning codebase...")

    system = """You are a senior Python security and quality engineer.
Your ONLY job is to find real, concrete bugs in the code provided.
Focus on: logic errors, missing error handling, state management issues,
type mismatches, dead code with side effects, and security issues.
Do NOT flag style issues or subjective preferences.

Respond in this exact format (repeat the block for each bug):
---BUG---
FILE: <relative file path>
LINE: <line number or range, e.g. "42" or "38-45">
SEVERITY: <critical|high|medium|low>
DESCRIPTION: <one clear sentence describing the bug and why it matters>
---END---
"""

    user = f"""Review this Python codebase and find all bugs:

{codebase}

Recent git changes:
{_git_diff()}
"""

    response = _call(client, system, user)
    bugs = []
    for block in response.split("---BUG---"):
        if "---END---" not in block:
            continue
        block = block.split("---END---")[0].strip()
        lines = {k.strip(): v.strip()
                 for line in block.splitlines() if ":" in line
                 for k, v in [line.split(":", 1)]}
        if all(k in lines for k in ("FILE", "LINE", "SEVERITY", "DESCRIPTION")):
            bugs.append(Bug(
                file=lines["FILE"],
                line_hint=lines["LINE"],
                description=lines["DESCRIPTION"],
                severity=lines["SEVERITY"].lower(),
            ))

    print(f"   Found {len(bugs)} potential bugs.")
    return bugs


# ── Agent 2: Bug Validator ──────────────────────────────────────────────────────

def bug_validator_agent(
    client: anthropic.Anthropic,
    bugs: list[Bug],
    codebase: str,
) -> ValidationResult:
    print("\n✅ [2/4] BugValidatorAgent — validating findings...")

    if not bugs:
        print("   No bugs to validate.")
        return ValidationResult(confirmed_bugs=[], false_positives=[], reasoning="No bugs were found.")

    bugs_text = "\n".join(
        f"BUG #{i+1}: [{b.severity.upper()}] {b.file}:{b.line_hint} — {b.description}"
        for i, b in enumerate(bugs)
    )

    system = """You are a second senior Python engineer doing a peer review.
You are given a list of alleged bugs and the full codebase.
For each bug: determine if it is REAL (confirmed) or a FALSE POSITIVE.
Be precise — cite the actual code that proves or disproves each claim.

Respond in this exact format:
---VALIDATION---
BUG_NUMBER: <number>
STATUS: <CONFIRMED|FALSE_POSITIVE>
REASON: <one sentence citing actual code>
---END---

After all bugs, add:
---SUMMARY---
<overall reasoning paragraph>
---END---
"""

    user = f"""Validate these reported bugs against the codebase:

REPORTED BUGS:
{bugs_text}

CODEBASE:
{codebase}
"""

    response = _call(client, system, user)

    confirmed, false_positives = [], []
    for block in response.split("---VALIDATION---"):
        if "---END---" not in block:
            continue
        block = block.split("---END---")[0].strip()
        lines = {k.strip(): v.strip()
                 for line in block.splitlines() if ":" in line
                 for k, v in [line.split(":", 1)]}
        if "BUG_NUMBER" not in lines or "STATUS" not in lines:
            continue
        try:
            idx = int(lines["BUG_NUMBER"]) - 1
            bug = bugs[idx]
            if lines["STATUS"] == "CONFIRMED":
                confirmed.append(bug)
            else:
                false_positives.append(bug)
        except (ValueError, IndexError):
            continue

    summary_match = response.split("---SUMMARY---")
    reasoning = (
        summary_match[1].split("---END---")[0].strip()
        if len(summary_match) > 1 else ""
    )

    print(f"   Confirmed: {len(confirmed)}, False positives: {len(false_positives)}")
    return ValidationResult(confirmed_bugs=confirmed, false_positives=false_positives, reasoning=reasoning)


# ── Agent 3: Bug Fixer ──────────────────────────────────────────────────────────

def bug_fixer_agent(
    client: anthropic.Anthropic,
    validation: ValidationResult,
    codebase: str,
) -> list[Fix]:
    print("\n🔧 [3/4] BugFixerAgent — generating fixes...")

    if not validation.confirmed_bugs:
        print("   No confirmed bugs to fix.")
        return []

    bugs_text = "\n".join(
        f"BUG #{i+1}: [{b.severity.upper()}] {b.file}:{b.line_hint} — {b.description}"
        for i, b in enumerate(validation.confirmed_bugs)
    )

    system = """You are a senior Python engineer responsible for fixing bugs.
For each confirmed bug, provide a concrete fix.
Be minimal — fix only what is broken, do not refactor surrounding code.

Respond in this exact format:
---FIX---
BUG_NUMBER: <number>
CONFIDENCE: <high|medium|low>
PATCH: <describe exactly what line(s) to change and what the replacement should be.
        Use before/after format if showing code. Be specific enough to apply without ambiguity.>
---END---
"""

    user = f"""Fix these confirmed bugs:

{bugs_text}

CODEBASE:
{codebase}
"""

    response = _call(client, system, user)

    fixes = []
    for block in response.split("---FIX---"):
        if "---END---" not in block:
            continue
        block = block.split("---END---")[0].strip()
        lines_dict: dict[str, str] = {}
        for line in block.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                lines_dict[k.strip()] = v.strip()

        # PATCH may span multiple lines — re-parse
        patch_start = block.find("PATCH:")
        patch = block[patch_start + 6:].strip() if patch_start != -1 else ""

        if "BUG_NUMBER" not in lines_dict:
            continue
        try:
            idx = int(lines_dict["BUG_NUMBER"]) - 1
            bug = validation.confirmed_bugs[idx]
            fixes.append(Fix(
                bug=bug,
                patch=patch,
                confidence=lines_dict.get("CONFIDENCE", "medium").lower(),
            ))
        except (ValueError, IndexError):
            continue

    print(f"   Generated {len(fixes)} fixes.")
    return fixes


# ── Agent 4: PR Approver ────────────────────────────────────────────────────────

def pr_approver_agent(
    client: anthropic.Anthropic,
    bugs: list[Bug],
    validation: ValidationResult,
    fixes: list[Fix],
) -> PRDecision:
    print("\n📋 [4/4] PRApproverAgent — reviewing PR readiness...")

    confirmed_text = "\n".join(
        f"  - [{b.severity.upper()}] {b.file}:{b.line_hint} — {b.description}"
        for b in validation.confirmed_bugs
    ) or "  None"

    fixes_text = "\n".join(
        f"  - BUG in {f.bug.file}:{f.bug.line_hint} (confidence: {f.confidence})\n    FIX: {f.patch[:200]}"
        for f in fixes
    ) or "  None"

    false_pos_text = "\n".join(
        f"  - {b.file}:{b.line_hint} — {b.description}"
        for b in validation.false_positives
    ) or "  None"

    system = """You are a senior engineering manager doing a final PR review.
You have a full picture: reported bugs, validation results, and proposed fixes.
Decide if this codebase is ready to merge, and list any remaining concerns.

Respond in this exact format:
---DECISION---
APPROVED: <YES|NO>
SUMMARY: <2-3 sentence executive summary>
CONCERNS:
- <concern 1 if any>
- <concern 2 if any>
---END---

If no concerns, write "CONCERNS:\n- None"
"""

    user = f"""Review this code quality report and make a PR merge decision:

CONFIRMED BUGS:
{confirmed_text}

VALIDATION REASONING:
{validation.reasoning}

PROPOSED FIXES:
{fixes_text}

FALSE POSITIVES (correctly dismissed):
{false_pos_text}
"""

    response = _call(client, system, user)

    approved = False
    summary = ""
    concerns: list[str] = []

    block = response.split("---DECISION---")[-1].split("---END---")[0].strip()
    for line in block.splitlines():
        line = line.strip()
        if line.startswith("APPROVED:"):
            approved = "YES" in line.upper()
        elif line.startswith("SUMMARY:"):
            summary = line[8:].strip()
        elif line.startswith("- ") and "CONCERNS" not in line:
            concern = line[2:].strip()
            if concern.lower() != "none":
                concerns.append(concern)

    return PRDecision(approved=approved, summary=summary, remaining_concerns=concerns)


# ── Orchestrator ────────────────────────────────────────────────────────────────

def run_pipeline():
    print("=" * 60)
    print("  ToneTurner — Multi-Agent Code Review Pipeline")
    print("=" * 60)

    client   = _client()
    codebase = _read_codebase()

    bugs       = bug_finder_agent(client, codebase)
    validation = bug_validator_agent(client, bugs, codebase)
    fixes      = bug_fixer_agent(client, validation, codebase)
    decision   = pr_approver_agent(client, bugs, validation, fixes)

    # ── Final Report ──
    print("\n" + "=" * 60)
    print("  PIPELINE REPORT")
    print("=" * 60)

    print(f"\n📊 Summary")
    print(f"   Bugs found:       {len(bugs)}")
    print(f"   Confirmed:        {len(validation.confirmed_bugs)}")
    print(f"   False positives:  {len(validation.false_positives)}")
    print(f"   Fixes generated:  {len(fixes)}")

    if validation.confirmed_bugs:
        print("\n🐛 Confirmed Bugs")
        for b in validation.confirmed_bugs:
            print(f"   [{b.severity.upper()}] {b.file}:{b.line_hint}")
            print(f"   → {b.description}")

    if fixes:
        print("\n🔧 Fixes")
        for f in fixes:
            print(f"   {f.bug.file}:{f.bug.line_hint} (confidence: {f.confidence})")
            print(f"   → {f.patch[:300]}")
            print()

    print(f"\n{'✅ PR APPROVED' if decision.approved else '❌ PR REJECTED'}")
    print(f"   {decision.summary}")
    if decision.remaining_concerns:
        print("\n⚠️  Remaining Concerns")
        for c in decision.remaining_concerns:
            print(f"   - {c}")

    print("\n" + "=" * 60)
    return decision


if __name__ == "__main__":
    run_pipeline()
