# @agentreplay/recorder-sdk

Lightweight browser recorder. Captures clicks, input, navigation, network, console, accessibility snapshots, and element metadata as a structured `BrowserEvent` stream, batches them, and ships them to the ingestion API. See [../../docs/event-schema.md](../../docs/event-schema.md).

## Browser usage

```ts
import { Recorder } from "@agentreplay/recorder-sdk";

const recorder = new Recorder({
  sessionId: `checkout-${Date.now()}`,
  ingestUrl: "http://localhost:8000/v1/events:batch",
  batchSize: 10,
});

recorder.start();

// Later, before leaving the page or when the user finishes the workflow:
recorder.stop();
const recording = recorder.exportRecording("Checkout flow", "complete checkout");
```

The exported JSON can be imported from the dashboard with **Import Recording** or sent to `POST /v1/recordings:import`.
