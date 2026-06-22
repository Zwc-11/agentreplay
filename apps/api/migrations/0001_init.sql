-- AgentReplay initial schema. Relational metadata + JSONB event payloads.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE users (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email      text UNIQUE NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE projects (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id   uuid REFERENCES users(id),
  name       text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE api_keys (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(id),
  key_hash   text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE sessions (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(id),
  name       text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE events (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id uuid NOT NULL REFERENCES sessions(id),
  step_index int  NOT NULL,
  event_type text NOT NULL,
  timestamp  timestamptz NOT NULL,
  url        text,
  target     jsonb,
  network    jsonb,
  payload    jsonb,
  UNIQUE (session_id, step_index)
);
CREATE INDEX idx_events_session ON events(session_id);
CREATE INDEX idx_events_target_gin ON events USING gin (target);

CREATE TABLE snapshots (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id   uuid REFERENCES events(id),
  kind       text NOT NULL,         -- 'screenshot' | 'dom' | 'a11y'
  storage_key text NOT NULL
);

CREATE TABLE workflow_graphs (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id uuid NOT NULL REFERENCES sessions(id),
  nodes      jsonb NOT NULL,
  edges      jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE agent_runs (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_id  uuid NOT NULL REFERENCES workflow_graphs(id),
  driver_name  text NOT NULL,
  status       text NOT NULL,
  success      boolean,
  started_at   timestamptz,
  completed_at timestamptz
);

CREATE TABLE agent_actions (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_run_id uuid NOT NULL REFERENCES agent_runs(id),
  step_index   int NOT NULL,
  command      jsonb NOT NULL,
  result_url   text
);

CREATE TABLE evaluation_metrics (
  id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_run_id      uuid NOT NULL REFERENCES agent_runs(id),
  task_success      boolean,
  step_accuracy     numeric,
  wrong_click_count int,
  divergence_step   int,
  replay_latency_ms int
);

CREATE TABLE failure_summaries (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_run_id uuid NOT NULL REFERENCES agent_runs(id),
  category     text,
  summary      text,
  created_at   timestamptz NOT NULL DEFAULT now()
);
