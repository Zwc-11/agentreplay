"""Print the AgentReplay benchmark table.

Usage: python -m app.scripts.benchmark
"""
from __future__ import annotations

from app import state
from app.services.benchmark import run_benchmark


def main() -> None:
    state.seed()
    result = run_benchmark(state.store, goal_for=state.goal_for_workflow)

    bar = "=" * 76
    print(bar)
    print(f"AgentReplay benchmark — {result['workflows']} workflows x {len(result['drivers'])} drivers")
    print(bar)
    print(f"{'driver':12} {'success':>8} {'step_acc':>9} {'wrong':>6} {'mean_div':>9} {'net_caused':>11}")
    print("-" * 76)
    for d in result["drivers"].values():
        md = "-" if d["meanFirstDivergence"] is None else f"{d['meanFirstDivergence']}"
        print(
            f"{d['driver']:12} {d['taskSuccessRate']*100:7.0f}% {d['meanStepAccuracy']*100:8.0f}% "
            f"{d['totalWrongClicks']:6} {md:>9} {d['networkCausedFailures']:>11}"
        )
    print("\nFailure categories:", result["categories"] or "(none)")
    print(bar)


if __name__ == "__main__":
    main()
