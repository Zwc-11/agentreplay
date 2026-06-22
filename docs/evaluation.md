# Evaluation & metrics

AgentReplay produces **measurable, step-level outcomes** for every agent run. The evaluator aligns the agent's action path against the recorded human path, finds the first point they diverge, and computes the metrics below.

## Divergence detection

Given the human path `H = [h0, h1, …]` and the agent path `A = [a0, a1, …]`, the evaluator walks both in step order and compares each agent action against the expected human action at the same state.

- A step **matches** when the agent's `BrowserCommand` targets the same logical element/action as the human's (compared by role + accessible name + normalized selector, not raw pixel position).
- The **first divergence step** is the lowest index where the agent's action does not match the expected action.
- After divergence, the evaluator keeps scoring to measure whether the agent **recovered** (returned to an on-path state).

The first divergence node is the one the graph pulses red in Mode 2.

## Metrics

| Metric | Definition |
| --- | --- |
| **Task success rate** | Did the run reach the goal state? (boolean per run; rate across runs) |
| **Step accuracy** | matched steps / total expected steps |
| **Wrong-click count** | number of off-path actions taken |
| **First divergence step** | index of the first non-matching action (null if none) |
| **Replay reconstruction success** | could the workflow be fully rebuilt from the event log? |
| **Agent recovery rate** | runs that returned to the human path after diverging / runs that diverged |
| **Network-caused failure rate** | failures attributable to a bad network response / total failures |
| **Average replay latency** | mean ms to reconstruct and render a replay |
| **Generated test pass rate** | exported Playwright tests that pass / tests generated |

Per-run metrics are persisted to `evaluation_metrics`:

```sql
evaluation_metrics (
  id                uuid PRIMARY KEY,
  agent_run_id      uuid,
  task_success      boolean,
  step_accuracy     numeric,
  wrong_click_count int,
  divergence_step   int,
  replay_latency_ms int
)
```

## Failure categories

Each failed run is tagged with a category so the benchmark page can aggregate them:

- `wrong-element` — clicked a lookalike/ad/incorrect control
- `stale-state` — acted before a route/DOM update settled
- `network-caused` — a failed request disabled the intended path
- `missing-recovery` — diverged and never returned to the path
- `assertion-failed` — reached a state that failed an expected assertion

## Benchmark page

The benchmark screen aggregates 20–50 workflows and reports task success rate, step accuracy, divergence step, wrong-click rate, and failure-category breakdown across drivers.

## On reporting numbers

Design the pipeline so every metric above is computable from day one, but **only publish real numbers after measuring them**. Example of the *shape* of results to aim for (placeholders until measured):

- Recorded N browser workflows across M demo apps.
- Generated Playwright tests for X/N workflows.
- Detected the first agent divergence with P% agreement against manual labels.

Replace N/M/X/P with measured values before putting them in the README or a resume bullet.
