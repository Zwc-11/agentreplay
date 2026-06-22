import type { Command, EvaluationMetrics } from "@agentreplay/shared-types";

export function commandKey(c: Command): string {
  const label = (c.name || c.text || "").trim().toLowerCase();
  return JSON.stringify([c.kind, c.role ?? null, label, c.selector ?? null]);
}

export function detectDivergence(human: Command[], agent: Command[]): number | null {
  for (let i = 0; i < human.length; i++) {
    const a = agent[i];
    if (a == null || commandKey(human[i]) !== commandKey(a)) return i;
  }
  return null;
}

function classifyFailure(human: Command[], agent: Command[], div: number | null, network?: { status: number }[]): string | null {
  if (div === null) return null;
  if ((network ?? []).some((n) => (n?.status ?? 0) >= 400)) return "network-caused";
  if (div >= agent.length) return "missing-recovery";
  const expected = div < human.length ? human[div] : null;
  if (expected && expected.kind === "assertVisible") return "assertion-failed";
  if (div > 0 && commandKey(agent[div]) === commandKey(agent[div - 1])) return "stale-state";
  return "wrong-element";
}

export function computeMetrics(
  human: Command[],
  agent: Command[],
  success: boolean,
  network?: { status: number }[],
  replayLatencyMs = 0,
): EvaluationMetrics {
  const div = detectDivergence(human, agent);
  const matched = div ?? Math.min(human.length, agent.length);
  const stepAccuracy = human.length ? Math.round((matched / human.length) * 10000) / 10000 : 0;
  const wrongClickCount = Math.max(0, agent.length - matched);
  const recovered = div !== null && agent.length > 0 && human.length > 0 && commandKey(agent[agent.length - 1]) === commandKey(human[human.length - 1]);
  const category = classifyFailure(human, agent, div, network);
  return {
    taskSuccess: success,
    stepAccuracy,
    wrongClickCount,
    divergenceStep: div,
    recovered,
    networkCausedFailure: category === "network-caused",
    failureCategory: category,
    replayLatencyMs,
  };
}

