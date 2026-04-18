"""
Simulates the 4-agent pipeline with realistic mock data
based on the actual ToneTurner codebase.

Run:
    python -m agents.simulate
"""

import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).parent.parent


@dataclass
class Bug:
    file: str
    line_hint: str
    description: str
    severity: str


@dataclass
class ValidationResult:
    confirmed_bugs: list[Bug]
    false_positives: list[Bug]
    reasoning: str


@dataclass
class Fix:
    bug: Bug
    patch: str
    confidence: str


@dataclass
class PRDecision:
    approved: bool
    summary: str
    remaining_concerns: list[str]


def _read_codebase() -> str:
    parts = []
    for path in sorted(ROOT.rglob("*.py")):
        if any(skip in path.parts for skip in ("venv", "__pycache__", "agents")):
            continue
        rel = path.relative_to(ROOT)
        parts.append(f"# === {rel} ===")
    return "\n".join(parts)

def _print_typing(text: str, delay: float = 0.01):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()


def _divider():
    print("=" * 60)


def simulate_bug_finder(codebase: str) -> list[Bug]:
    print("\n🔍 [1/4] BugFinderAgent — scanning codebase...")
    time.sleep(1)
    _print_typing("   Analyzing src/components/ui_components.py...", 0.005)
    _print_typing("   Analyzing src/services/groq_service.py...", 0.005)
    _print_typing("   Analyzing src/repositories/history_repo.py...", 0.005)
    _print_typing("   Analyzing app.py...", 0.005)
    time.sleep(0.5)

    bugs = [
        Bug(
            file="src/services/groq_service.py",
            line_hint="50-55",
            severity="high",
            description="response_text variable referenced in the JSONDecodeError except block "
                        "but may be undefined if the API raises before assignment, causing NameError.",
        ),
        Bug(
            file="src/components/ui_components.py",
            line_hint="108-120",
            severity="medium",
            description="_render_translation uses st.button inside an st.expander which re-renders "
                        "on every Streamlit rerun, causing copy button state to reset unexpectedly.",
        ),
        Bug(
            file="src/repositories/history_repo.py",
            line_hint="28",
            severity="low",
            description="HistoryRepository._load returns a mutable list from session_state directly; "
                        "callers mutating the returned list corrupt session state silently.",
        ),
        Bug(
            file="app.py",
            line_hint="18-22",
            severity="low",
            description="Session state keys 'results' and 'dark_mode' are initialised on every "
                        "render but ai_service is not re-initialised if the API key changes at runtime.",
        ),
    ]

    print(f"   Found {len(bugs)} potential bugs.")
    return bugs


def simulate_bug_validator(bugs: list[Bug], codebase: str) -> ValidationResult:
    print("\n✅ [2/4] BugValidatorAgent — validating findings...")
    time.sleep(1)

    for i, b in enumerate(bugs):
        _print_typing(f"   Checking BUG #{i+1}: {b.file}:{b.line_hint}...", 0.004)
        time.sleep(0.3)

    confirmed = bugs[:3]    # first 3 are real
    false_positives = bugs[3:]  # last one is debatable, dismissed

    reasoning = (
        "BUG #1 is confirmed: line 162 in groq_service.py catches json.JSONDecodeError and "
        "references `response_text` in the error message, but `response_text` is only assigned "
        "inside the try block after the API call — if the API raises before that assignment "
        "(e.g. network error), the except block itself will raise NameError. "
        "BUG #2 is confirmed: the copy button in _render_translation is rendered inside a "
        "conditional expander block; Streamlit's re-render cycle resets widget state correctly "
        "but the st.code() call appears unconditionally after the button click, which is misleading. "
        "BUG #3 is confirmed: history_repo._load() returns `st.session_state.get(self._KEY, [])` "
        "directly — callers receive the same list object stored in state, so any in-place mutation "
        "bypasses the add() method logic. "
        "BUG #4 is a false positive: ai_service is intentionally a cached singleton; "
        "the API key is resolved at construction time and the design does not support hot-swapping."
    )

    print(f"   Confirmed: {len(confirmed)}, False positives: {len(false_positives)}")
    return ValidationResult(
        confirmed_bugs=confirmed,
        false_positives=false_positives,
        reasoning=reasoning,
    )


def simulate_bug_fixer(validation: ValidationResult, codebase: str) -> list[Fix]:
    print("\n🔧 [3/4] BugFixerAgent — generating fixes...")
    time.sleep(1)

    fixes_data = [
        (
            "high",
            """In groq_service.py, initialise response_text before the try block:

BEFORE:
    try:
        ...
        response_text = response.choices[0].message.content.strip()

AFTER:
    response_text = ""
    try:
        ...
        response_text = response.choices[0].message.content.strip()

This ensures the JSONDecodeError handler can always reference response_text safely.""",
        ),
        (
            "medium",
            """In ui_components.py _render_translation, move the copy button outside the
expander so its state is not tied to expander open/close cycles:

BEFORE:
    with st.expander("📖 View English Translation", expanded=True):
        st.text_area(...)
        if st.button("📋 Copy Translation", key="copy_translation"):
            st.code(result.translation, language=None)

AFTER:
    with st.expander("📖 View English Translation", expanded=True):
        st.text_area(...)
    _copy_button(result.translation, key="copy_translation")""",
        ),
        (
            "high",
            """In history_repo.py, return a shallow copy from _load() to prevent
callers from mutating session state directly:

BEFORE:
    def _load(self) -> list[HistoryEntry]:
        return st.session_state.get(self._KEY, [])

AFTER:
    def _load(self) -> list[HistoryEntry]:
        return list(st.session_state.get(self._KEY, []))""",
        ),
    ]

    fixes = []
    for i, (confidence, patch) in enumerate(fixes_data):
        bug = validation.confirmed_bugs[i]
        _print_typing(f"   Fixing [{bug.severity.upper()}] {bug.file}:{bug.line_hint}...", 0.004)
        time.sleep(0.4)
        fixes.append(Fix(bug=bug, patch=patch, confidence=confidence))

    print(f"   Generated {len(fixes)} fixes.")
    return fixes


def simulate_pr_approver(
    bugs: list[Bug],
    validation: ValidationResult,
    fixes: list[Fix],
) -> PRDecision:
    print("\n📋 [4/4] PRApproverAgent — reviewing PR readiness...")
    time.sleep(1)
    _print_typing("   Reviewing confirmed bugs...", 0.005)
    _print_typing("   Reviewing proposed fixes...", 0.005)
    _print_typing("   Checking for critical/unresolved issues...", 0.005)
    time.sleep(0.5)

    return PRDecision(
        approved=False,
        summary=(
            "The codebase is well-structured with clear separation of concerns, "
            "but 3 confirmed bugs must be addressed before merging. "
            "The NameError risk in groq_service.py is the most critical — "
            "it can cause a silent crash in production that masks the original API error."
        ),
        remaining_concerns=[
            "groq_service.py:50-55 — NameError on response_text must be fixed before deploy",
            "history_repo.py:28 — mutable list leak from _load() should be patched to prevent silent state corruption",
            "Consider adding a basic smoke test for the rephrase pipeline to catch regressions",
        ],
    )


def run_simulation():
    _divider()
    print("  ToneTurner — Multi-Agent Code Review Pipeline (SIMULATION)")
    _divider()

    codebase = _read_codebase()
    print(f"   Loaded {len(codebase.splitlines())} lines across {codebase.count('# ===')} files.")

    bugs       = simulate_bug_finder(codebase)
    validation = simulate_bug_validator(bugs, codebase)
    fixes      = simulate_bug_fixer(validation, codebase)
    decision   = simulate_pr_approver(bugs, validation, fixes)

    # ── Final Report ──────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  PIPELINE REPORT")
    print("=" * 60)

    print(f"\n📊 Summary")
    print(f"   Bugs found:       {len(bugs)}")
    print(f"   Confirmed:        {len(validation.confirmed_bugs)}")
    print(f"   False positives:  {len(validation.false_positives)}")
    print(f"   Fixes generated:  {len(fixes)}")

    print("\n🐛 Confirmed Bugs")
    for b in validation.confirmed_bugs:
        print(f"   [{b.severity.upper()}] {b.file}:{b.line_hint}")
        print(f"   → {b.description}")
        print()

    print("🔧 Proposed Fixes")
    for f in fixes:
        print(f"   {f.bug.file}:{f.bug.line_hint} (confidence: {f.confidence})")
        first_line = f.patch.split("\n")[0]
        print(f"   → {first_line}")
        print()

    if validation.false_positives:
        print("🚫 False Positives (dismissed)")
        for b in validation.false_positives:
            print(f"   {b.file}:{b.line_hint} — {b.description[:80]}...")
        print()

    status = "✅ PR APPROVED" if decision.approved else "❌ PR NOT READY — fixes required"
    print(f"{status}")
    print(f"   {decision.summary}")

    if decision.remaining_concerns:
        print("\n⚠️  Remaining Concerns")
        for c in decision.remaining_concerns:
            print(f"   - {c}")

    _divider()


if __name__ == "__main__":
    run_simulation()
