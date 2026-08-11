#!/usr/bin/env python3
"""Deterministic skill-registry evals (dummy/fixture checks).

Validates that Skills/, rubrics, and fixture artifacts exist with required
sections. Does not call Jira or LLMs.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "Skills"
EVALS = ROOT / "evals"
FIXTURES = EVALS / "fixtures"
RUBRICS = EVALS / "rubrics"

REQUIRED_SKILLS = [
    "sdlc-loop",
    "idea-refine",
    "spec-driven-development",
    "planning-and-task-breakdown",
    "incremental-implementation",
    "test-driven-development",
    "code-review-and-quality",
    "jira-phase-gate",
]

REQUIRED_RUBRICS = [
    "loop.md",
    "ideate.md",
    "spec.md",
    "plan.md",
    "implement.md",
    "test.md",
    "review.md",
]


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def require_file(path: Path, *needles: str) -> None:
    if not path.is_file():
        fail(f"missing file {path.relative_to(ROOT)}")
    text = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            fail(f"{path.relative_to(ROOT)} missing required text: {needle!r}")


def main() -> None:
    require_file(
        SKILLS / "REGISTRY.md",
        "sdlc-loop",
        "Supervised",
        "outer loop",
        "sdlc:ideate",
        "feature-agnostic",
    )
    require_file(
        ROOT / "docs" / "ai-sdlc" / "README.md",
        "outer loop",
        "Jira",
        "AGENTS.md",
    )
    require_file(ROOT / "docs" / "examples" / "merge" / "README.md", "Example only")
    require_file(SKILLS / "_templates" / "phase-comment.md", "SDLC phase")
    require_file(
        SKILLS / "_templates" / "dual-layer.md",
        "Deterministic layer",
        "ESCALATE",
    )
    require_file(
        ROOT / "docs" / "design" / "ai-sdlc-loop.md",
        "outer loop",
        "Inner",
        "PLAN GATE",
    )

    for name in REQUIRED_SKILLS:
        skill = SKILLS / name / "SKILL.md"
        require_file(skill, "name:", "description:")
        front = skill.read_text(encoding="utf-8")
        if not front.startswith("---"):
            fail(f"{name}/SKILL.md missing YAML frontmatter")
        if name == "sdlc-loop":
            require_file(skill, "OUTER LOOP", "PLAN GATE", "ESCALATE", "VERDICT")
        else:
            require_file(skill, "Deterministic")

    for rubric in REQUIRED_RUBRICS:
        require_file(RUBRICS / rubric, "Pass if", "Fail if")

    require_file(FIXTURES / "dummy-idea.md", "Problem Statement", "Not Doing")
    require_file(FIXTURES / "dummy-spec.md", "Objective", "Success Criteria")
    require_file(FIXTURES / "dummy-plan.md", "Overview")
    require_file(FIXTURES / "dummy-todo.md", "Acceptance", "Verify")
    require_file(FIXTURES / "dummy-escalate.md", "OUTER LOOP — ESCALATE")

    cursor_skills = ROOT / ".cursor" / "skills"
    if not cursor_skills.is_dir():
        fail(".cursor/skills missing")
    for name in REQUIRED_SKILLS:
        link = cursor_skills / name
        if not link.exists():
            fail(f".cursor/skills/{name} missing (expected symlink)")
        target = (SKILLS / name).resolve()
        if link.resolve() != target:
            fail(f".cursor/skills/{name} does not point at Skills/{name}")

    print("OK: skill registry evals passed")
    print(f"  skills={len(REQUIRED_SKILLS)} rubrics={len(REQUIRED_RUBRICS)}")


if __name__ == "__main__":
    main()
    sys.exit(0)
