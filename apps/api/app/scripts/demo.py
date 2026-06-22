"""Run the full AgentReplay pipeline against the seeded checkout workflow and
print a readable report. Usage: python -m app.scripts.demo"""
from __future__ import annotations

from app import state
from app.services.pipeline import run_agent


def _fmt(c) -> str:
    target = c.name or c.text or c.selector or c.url or ""
    val = f' = "{c.value}"' if c.value else ""
    return f"{c.kind:13} {target}{val}"


def _fmtd(c: dict) -> str:
    target = c.get("name") or c.get("text") or c.get("selector") or c.get("url") or ""
    val = f' = "{c["value"]}"' if c.get("value") else ""
    return f"{c.get('kind',''):13} {target}{val}"


def main() -> None:
    graph = state.seed()
    human = graph.human_commands()
    run = run_agent(state.store, state.WORKFLOW_ID, "divergent", goal="complete a checkout")
    m, s = run["metrics"], run["summary"]

    bar = "=" * 72
    print(bar)
    print("AgentReplay — record → compile → run → compare → explain → export")
    print(bar)
    print(f"Workflow: {state.WORKFLOW_ID}   nodes={len(graph.nodes)}  human_actions={len(human)}")

    print("\nHuman path:")
    for i, c in enumerate(human):
        print(f"  {i + 1:2}. {_fmt(c)}")

    print("\nAgent path (driver = divergent):")
    div = m["divergence_step"]
    for i, c in enumerate(run["agentCommands"]):
        marker = "  <-- DIVERGES HERE" if i == div else ""
        print(f"  {i + 1:2}. {_fmtd(c)}{marker}")

    print(f"\nFirst divergence : step {div + 1} of {len(human)}")
    print(f"Failure category : {m['failure_category']}")
    print(
        "Metrics          : "
        f"success={m['task_success']}  step_accuracy={m['step_accuracy']}  "
        f"wrong_clicks={m['wrong_click_count']}  recovered={m['recovered']}  "
        f"replay_latency_ms={m['replay_latency_ms']}"
    )
    print(f"\nAI summary:\n  {s['summary']}")
    print(f"\nGenerated GitHub issue title:\n  {s['githubIssue']['title']}")
    print("\nGenerated Playwright test:\n")
    print(run["generatedTest"])
    print(bar)


if __name__ == "__main__":
    main()
