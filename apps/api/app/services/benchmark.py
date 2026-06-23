"""Run every driver across every workflow and aggregate the metrics.

This is what turns AgentReplay's per-run numbers into a benchmark table:
task success rate, mean step accuracy, divergence distribution, wrong-click
rate and failure-category breakdown per driver.
"""
from __future__ import annotations

from collections import Counter

from app.services.pipeline import run_agent

DEFAULT_DRIVERS = ["scripted", "divergent", "random"]


def _aggregate(driver: str, runs: list[dict]) -> dict:
    n = len(runs)
    successes = sum(1 for r in runs if r["success"])
    accuracies = [r["metrics"]["step_accuracy"] for r in runs]
    wrong = sum(r["metrics"]["wrong_click_count"] for r in runs)
    divs = [r["metrics"]["divergence_step"] for r in runs if r["metrics"]["divergence_step"] is not None]
    net = sum(1 for r in runs if r["metrics"]["network_caused_failure"])
    return {
        "driver": driver,
        "workflows": n,
        "taskSuccessRate": round(successes / n, 3) if n else 0.0,
        "meanStepAccuracy": round(sum(accuracies) / n, 3) if n else 0.0,
        "totalWrongClicks": wrong,
        "meanFirstDivergence": round(sum(divs) / len(divs), 2) if divs else None,
        "networkCausedFailures": net,
    }


def run_benchmark(store, drivers: list[str] | None = None, goal_for=None) -> dict:
    drivers = drivers or DEFAULT_DRIVERS
    goal_for = goal_for or (lambda wid: "the workflow")
    workflow_ids = [w["id"] for w in store.list_workflows()]

    per_driver: dict[str, dict] = {}
    rows: list[dict] = []
    for driver in drivers:
        runs = []
        for wid in workflow_ids:
            run = run_agent(store, wid, driver, goal=goal_for(wid), client=None)  # no LLM in benchmark
            runs.append(run)
            rows.append({
                "workflow": wid,
                "driver": driver,
                "success": run["success"],
                "stepAccuracy": run["metrics"]["step_accuracy"],
                "divergenceStep": run["metrics"]["divergence_step"],
                "category": run["metrics"]["failure_category"],
            })
        per_driver[driver] = _aggregate(driver, runs)

    categories = dict(Counter(r["category"] for r in rows if r["category"]))
    return {"workflows": len(workflow_ids), "drivers": per_driver, "rows": rows, "categories": categories}
