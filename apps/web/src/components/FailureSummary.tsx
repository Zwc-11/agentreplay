import { Card, StatusBadge } from "../design-system";
import type { Run } from "../lib/types";

const REPO = "https://github.com/Zwc-11/agentreplay";

export function FailureSummary({ run }: { run: Run }) {
  const s = run.summary;
  const status = run.success ? "success" : "failure";
  const issueUrl = s.githubIssue
    ? `${REPO}/issues/new?title=${encodeURIComponent(s.githubIssue.title)}&body=${encodeURIComponent(s.githubIssue.body)}`
    : null;

  return (
    <Card title="Failure Summary - root cause + AI">
      <div className="flex items-center gap-2 mb-2">
        <StatusBadge status={status} label={run.success ? "completed" : s.category ?? "failed"} />
        {run.metrics.divergence_step != null && (
          <span className="text-[11px] text-gray-500">first divergence: step {run.metrics.divergence_step + 1}</span>
        )}
      </div>
      <p className="text-sm text-gray-300 leading-relaxed">{s.summary}</p>
      {issueUrl && (
        <a
          href={issueUrl}
          target="_blank"
          rel="noreferrer"
          className="inline-block mt-3 text-xs px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-gray-200 hover:bg-white/10"
        >
          Open GitHub issue
        </a>
      )}
    </Card>
  );
}
