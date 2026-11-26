#!/usr/bin/env python3
"""Fail fast when the committed non-functional evidence is incomplete or inconsistent."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "tests" / "team" / "evidence"
WORKFLOWS = ROOT / "tests" / "team" / "browser" / "workflows.spec.cjs"


def load_json(name: str):
    with (EVIDENCE / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    results = load_json("playwright-results.json")
    stats = results["stats"]
    require(stats["expected"] == 33, "Playwright evidence must contain 33 passing tests")
    require(stats["unexpected"] == 0, "Playwright evidence contains unexpected failures")
    require(stats["skipped"] == 0, "Playwright evidence contains skipped tests")

    workflow_text = WORKFLOWS.read_text(encoding="utf-8")
    missing_use_cases = [f"UC{number}" for number in range(1, 7) if f"UC{number}" not in workflow_text]
    require(not missing_use_cases, f"Missing use-case coverage: {', '.join(missing_use_cases)}")
    for role_case in (
        "SEC role matrix: librarian allowed issue and return screens",
        "SEC role matrix: student denied issue and return actions",
    ):
        require(role_case in workflow_text, f"Missing authorization test: {role_case}")

    axe_before = load_json("axe-before.json")
    axe_after = load_json("axe-after.json")
    require(len(axe_before["violations"]) > 0, "Baseline axe evidence must demonstrate violations")
    require(len(axe_after["violations"]) == 0, "Final axe evidence has accessibility violations")

    k6_runs = load_json("k6-run-status.json")
    run_matrix = {(run["vus"], run["run"]) for run in k6_runs if run["exitCode"] == 0}
    require(run_matrix == {(1, 1), (1, 2), (5, 1), (5, 2)}, "k6 evidence must contain four successful runs")

    lighthouse = {}
    for screen in ("issue", "return"):
        before = load_json(f"lighthouse-{screen}-before.json")["categories"]
        after = load_json(f"lighthouse-{screen}-after.json")["categories"]
        before_accessibility = before["accessibility"]["score"]
        after_accessibility = after["accessibility"]["score"]
        require(after_accessibility == 1, f"{screen} final accessibility score must be 1.0")
        require(after_accessibility > before_accessibility, f"{screen} accessibility score did not improve")
        for category in ("best-practices", "seo"):
            require(isinstance(after[category]["score"], (int, float)), f"Missing {screen} {category} score")
        lighthouse[screen] = {"before": before_accessibility, "after": after_accessibility}

    summary = {
        "playwright": {"passed": stats["expected"], "failed": stats["unexpected"]},
        "useCases": 6,
        "roleDecisions": 4,
        "axeViolations": {"before": len(axe_before["violations"]), "after": len(axe_after["violations"])},
        "k6SuccessfulRuns": len(run_matrix),
        "lighthouseAccessibility": lighthouse,
    }
    print(json.dumps(summary, indent=2))
    print("Non-functional evidence validation passed.")


if __name__ == "__main__":
    main()
