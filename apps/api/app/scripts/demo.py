"""Run the full AgentReplay pipeline against the seeded checkout workflow and
print a readable report.

Usage:
    python -m app.scripts.demo               # divergent agent (default)
    python -m app.scripts.demo scripted      # always-correct baseline
    python -m app.scripts.demo llm           # DeepSeek v4 Pro (needs DEEPSEEK_API_KEY)
"""

from __future__ import annotations

import os
import sys

from app import state
from app.services.pipeline import run_agent


def _fmt(c) -> str:
    target = c.name or c.text or c.selector or c.url or ""
    val = f' = "{c.value}"' if c.value else ""
    return f"{c.kind:13} {target}{val}"


def _fmtd(c: dict) -> str:
    target = c.get("name") or c.get("text") or c.get("selector") or c.get("url") or ""
    val = f' = "{c["value"]}"' if c.get("value") else ""
    return f"{c.get('kind', ''):13} {target}{val}"


def main() -> None:
    graph = state.seed()
    human = graph.human_commands()
    driver = sys.argv[1] if len(sys.argv) > 1 else os.getenv("DRIVER", "divergent")
    run = run_agent(state.store, state.WORKFLOW_ID, driver, goal="complete a checkout")
    m, s = run["metrics"], run["summary"]
    div = m["divergence_step"]

    bar = "=" * 72
    print(bar)
    print("AgentReplay - record -> compile -> run -> compare -> explain -> export")
    print(bar)
    print(f"Workflow: {state.WORKFLOW_ID}   nodes={len(graph.nodes)}  human_actions={len(human)}")
    print(f"Driver: {driver}   DeepSeek enabled: {run.get('llmEnabled', False)}")

    print("\nHuman path:")
    for i, c in enumerate(human):
        print(f"  {i + 1:2}. {_fmt(c)}")

    print(f"\nAgent path (driver = {driver}):")
    for i, c in enumerate(run["agentCommands"]):
        marker = "  <-- DIVERGES HERE" if div is not None and i == div else ""
        print(f"  {i + 1:2}. {_fmtd(c)}{marker}")

    if div is None:
        print(f"\nResult           : SUCCESS - matched the human path on all {len(human)} steps")
    else:
        print(f"\nFirst divergence : step {div + 1} of {len(human)}")
        print(f"Failure category : {m['failure_category']}")
    print(
        "Metrics          : "
        f"success={m['task_success']}  step_accuracy={m['step_accuracy']}  "
        f"wrong_clicks={m['wrong_click_count']}  recovered={m['recovered']}  "
        f"replay_latency_ms={m['replay_latency_ms']}"
    )
    print(f"\nAI summary{' (DeepSeek)' if s.get('model') == 'deepseek' else ''}:\n  {s['summary']}")
    if s.get("githubIssue"):
        print(f"\nGenerated GitHub issue title:\n  {s['githubIssue']['title']}")
    print("\nGenerated Playwright test:\n")
    print(run["generatedTest"])
    print(bar)


if __name__ == "__main__":
    main()
