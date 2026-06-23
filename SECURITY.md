# Security Policy

## Supported versions

AgentReplay is pre-1.0; security fixes are applied to the latest `main`.

## Reporting a vulnerability

Please **do not** open a public issue for security vulnerabilities.

Instead, report privately via [GitHub Security Advisories](https://github.com/Zwc-11/agentreplay/security/advisories/new), or email **caesar.zwc.0611@gmail.com** with:

- a description of the issue and its impact,
- steps to reproduce, and
- any suggested remediation.

You can expect an acknowledgement within a few days. Please allow reasonable time for a fix before any public disclosure.

## Handling secrets

- Never commit API keys. `.env` is git-ignored; use `.env.example` as the template.
- `DEEPSEEK_API_KEY` and database credentials must be provided via environment variables, never hard-coded.
- The bundled demo runs fully offline with an in-memory store and seeded data — no secrets required.
