"""PostgreSQL-backed store (production). Same surface as InMemoryStore.

Creates its own JSONB-backed tables on first use, so it works against any empty
Postgres database. psycopg is imported lazily so importing this module never
requires the driver to be installed.
"""
from __future__ import annotations

import json

from app.core.graph.model import graph_from_dict

_SCHEMA = """
CREATE TABLE IF NOT EXISTS ar_sessions (id text PRIMARY KEY, name text);
CREATE TABLE IF NOT EXISTS ar_events (
  session_id text NOT NULL, step_index int NOT NULL, payload jsonb NOT NULL,
  PRIMARY KEY (session_id, step_index)
);
CREATE TABLE IF NOT EXISTS ar_graphs (
  workflow_id text PRIMARY KEY, session_id text NOT NULL, graph jsonb NOT NULL
);
CREATE TABLE IF NOT EXISTS ar_runs (
  id text PRIMARY KEY, workflow_id text NOT NULL, run jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
"""


class PostgresStore:
    def __init__(self, dsn: str):
        import psycopg  # lazy: only needed when STORE_BACKEND=postgres

        self._conn = psycopg.connect(dsn, autocommit=True)
        with self._conn.cursor() as cur:
            cur.execute(_SCHEMA)

    def save_session(self, session_id: str, name: str) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                "INSERT INTO ar_sessions (id, name) VALUES (%s, %s) "
                "ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name",
                (session_id, name),
            )

    def save_events(self, session_id: str, events: list) -> None:
        with self._conn.cursor() as cur:
            for e in events:
                cur.execute(
                    "INSERT INTO ar_events (session_id, step_index, payload) VALUES (%s, %s, %s) "
                    "ON CONFLICT (session_id, step_index) DO UPDATE SET payload = EXCLUDED.payload",
                    (session_id, e["stepIndex"], json.dumps(e)),
                )

    def load_events(self, session_id: str) -> list:
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT payload FROM ar_events WHERE session_id = %s ORDER BY step_index", (session_id,)
            )
            return [row[0] for row in cur.fetchall()]

    def save_graph(self, graph, session_id: str) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                "INSERT INTO ar_graphs (workflow_id, session_id, graph) VALUES (%s, %s, %s) "
                "ON CONFLICT (workflow_id) DO UPDATE SET graph = EXCLUDED.graph, session_id = EXCLUDED.session_id",
                (graph.id, session_id, json.dumps(graph.to_dict())),
            )

    def get_graph(self, workflow_id: str):
        with self._conn.cursor() as cur:
            cur.execute("SELECT graph FROM ar_graphs WHERE workflow_id = %s", (workflow_id,))
            row = cur.fetchone()
        return graph_from_dict(row[0]) if row else None

    def session_for(self, workflow_id: str) -> str:
        with self._conn.cursor() as cur:
            cur.execute("SELECT session_id FROM ar_graphs WHERE workflow_id = %s", (workflow_id,))
            row = cur.fetchone()
        if not row:
            raise KeyError(workflow_id)
        return row[0]

    def list_workflows(self) -> list:
        with self._conn.cursor() as cur:
            cur.execute("SELECT g.workflow_id, g.session_id, g.graph, s.name FROM ar_graphs g "
                        "LEFT JOIN ar_sessions s ON s.id = g.session_id")
            graphs = cur.fetchall()
        out = []
        for wid, _sid, graph_json, name in graphs:
            with self._conn.cursor() as cur:
                cur.execute("SELECT run FROM ar_runs WHERE workflow_id = %s", (wid,))
                runs = [r[0] for r in cur.fetchall()]
            successes = sum(1 for r in runs if r.get("success"))
            out.append({
                "id": wid,
                "name": name or "workflow",
                "steps": len(graph_from_dict(graph_json).human_commands()),
                "runs": len(runs),
                "successRate": round(successes / len(runs), 2) if runs else None,
            })
        return out

    def save_run(self, run: dict) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                "INSERT INTO ar_runs (id, workflow_id, run) VALUES (%s, %s, %s) "
                "ON CONFLICT (id) DO UPDATE SET run = EXCLUDED.run",
                (run["id"], run["workflowId"], json.dumps(run)),
            )

    def get_run(self, run_id: str):
        with self._conn.cursor() as cur:
            cur.execute("SELECT run FROM ar_runs WHERE id = %s", (run_id,))
            row = cur.fetchone()
        return row[0] if row else None

    def list_runs(self, workflow_id: str) -> list:
        with self._conn.cursor() as cur:
            cur.execute("SELECT run FROM ar_runs WHERE workflow_id = %s ORDER BY created_at", (workflow_id,))
            return [r[0] for r in cur.fetchall()]
