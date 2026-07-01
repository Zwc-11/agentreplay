# Issue: Implement XHR and WebSocket capture

Label: `enhancement`

## Summary

The recorder currently captures network calls made via `fetch` only. `XMLHttpRequest` and WebSocket traffic are not intercepted, so recordings can miss network evidence for apps that do not use `fetch`.

## Current Behavior

- `packages/recorder-sdk/src/index.ts` patches `window.fetch` in `patchFetch()`.
- `stopListening()` restores `window.fetch`.
- No `XMLHttpRequest` or WebSocket patch is present in the recorder SDK.

## Desired Behavior

- Capture XHR request method, path, status, and timing into the existing `network` event shape.
- Capture WebSocket lifecycle and message metadata only after the event schema is explicitly extended for it.
- Keep restore behavior symmetric so `stop()` removes every browser patch installed by `start()`.

## Notes

Do not claim XHR or WebSocket support in user-facing docs until this is implemented and tested.
