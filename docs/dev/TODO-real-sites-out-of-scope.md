# Issue: Real Public Sites Out Of Scope (Drifting DOMs/Auth/Anti-Automation)

Label: `documentation`

## Summary

AgentReplay v0.x supports the bundled demo sites and recordings only. Real public sites with drifting DOMs, authentication flows, changing network behavior, or anti-automation controls are out of scope until ownership decides whether to support them.

## Current Behavior

- The README scopes supported targets to `examples/demo-shop`, `examples/demo-crm`, and `examples/demo-calendar`.
- The bundled recordings are deterministic fixtures intended for local demos and CI.
- No real-site stabilization layer, authentication handling, or anti-automation strategy is implemented.

## Desired Behavior

- Keep public docs explicit that bundled demo targets are the supported scope.
- Do not present real public site replay as supported until there is implementation and test coverage for drifting DOMs, authentication, and anti-automation behavior.

## Notes

This issue tracks documentation and scope hygiene only. It should not be closed by implementing real-site support unless that ownership decision is made separately.
