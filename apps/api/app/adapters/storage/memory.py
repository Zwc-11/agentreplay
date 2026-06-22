"""In-memory store so the API runs with zero external services (demo default).

Implements the same surface a Postgres repository would. Swap in the postgres
adapter for production without touching services or routes.
"""
from __future__ import annotations

from collections import defaultdict


class InMemoryStore:
    def __init__(self):
        self.sessions: dict = {}
        self.events: dict = defaultdict(list)
        self.graphs: dict = {}
        self.graph_session: dict = {}
        self.runs: dict = {}
        self.runs_by_workflow: dict = defaultdict(list)

    # --- events / sessions ---
    def save_session(self, session_id: str, name: str) -> None:
        self.sessions[session_id] = {"id": session_id, "name": name}

    def save_events(self, session_id: str, events: list) -> None:
        by_step = {e["stepIndex"]: e for e in self.events[session_id]}
        for event in events:
            by_step[event["stepIndex"]] = event
        self.events[session_id] = [by_step[i] for i in sorted(by_step)]

    def load_events(self, session_id: str) -> list:
        return list(self.events[session_id])

    # --- graphs ---
    def save_graph(self, graph, session_id: str) -> None:
        self.graphs[graph.id] = graph
        self.graph_session[graph.id] = session_id

    def get_graph(self, workflow_id: str):
        return self.graphs.get(workflow_id)

    def list_workflows(self) -> list:
        out = []
        for wid, g in self.graphs.items():
            sid = self.graph_session.get(wid)
            runs = self.list_runs(wid)
            successes = sum(1 for r in runs if r["success"])
            out.append({
                "id": wid,
                "name": self.sessions.get(sid, {}).get("name", "workflow"),
                "steps": len(g.human_commands()),
                "runs": len(runs),
                "successRate": round(successes / len(runs), 2) if runs else None,
            })
        return out

    # --- runs ---
    def save_run(self, run: dict) -> None:
        self.runs[run["id"]] = run
        self.runs_by_workflow[run["workflowId"]].append(run["id"])

    def get_run(self, run_id: str):
        return self.runs.get(run_id)

    def list_runs(self, workflow_id: str) -> list:
        return [self.runs[r] for r in self.runs_by_workflow.get(workflow_id, [])]
