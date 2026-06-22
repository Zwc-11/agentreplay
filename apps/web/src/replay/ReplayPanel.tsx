import type { ReactNode } from "react";
import { Card } from "../design-system";
import { reconstructAt } from "../lib/replay";
import type { BrowserEvent } from "../lib/types";

function valueFor(events: BrowserEvent[], step: number, selector: string) {
  const event = [...events]
    .filter((e) => e.stepIndex <= step && e.eventType === "input" && e.target?.selector === selector)
    .sort((a, b) => b.stepIndex - a.stepIndex)[0];
  return event?.payload?.value ?? "";
}

function hasEvent(events: BrowserEvent[], step: number, predicate: (event: BrowserEvent) => boolean) {
  return events.some((event) => event.stepIndex <= step && predicate(event));
}

function lastTarget(events: BrowserEvent[], step: number) {
  return events.find((e) => e.stepIndex === step)?.target?.selector;
}

function Shell({ url, children }: { url?: string; children: ReactNode }) {
  return (
    <div className="w-full h-full bg-[#f8fafc] text-slate-900 flex flex-col">
      <div className="h-8 px-3 flex items-center gap-2 bg-slate-200 border-b border-slate-300 text-[11px] font-mono text-slate-600">
        <span className="flex gap-1">
          <span className="h-2.5 w-2.5 rounded-full bg-red-400" />
          <span className="h-2.5 w-2.5 rounded-full bg-amber-400" />
          <span className="h-2.5 w-2.5 rounded-full bg-emerald-400" />
        </span>
        <span className="truncate">{url ?? "about:blank"}</span>
      </div>
      <div className="flex-1 overflow-hidden relative">{children}</div>
    </div>
  );
}

function Field({ label, value, active }: { label: string; value?: string; active?: boolean }) {
  return (
    <div
      className={`rounded border bg-white px-3 py-2 ${
        active ? "border-emerald-500 ring-2 ring-emerald-100" : "border-slate-200"
      }`}
    >
      <div className="text-[10px] uppercase tracking-wide text-slate-500">{label}</div>
      <div className="text-sm font-medium text-slate-900 truncate">{value || " "}</div>
    </div>
  );
}

function Action({
  children,
  active,
  tone = "primary",
}: {
  children: ReactNode;
  active?: boolean;
  tone?: "primary" | "soft" | "danger";
}) {
  const toneClass =
    tone === "danger"
      ? "bg-rose-100 text-rose-700 border-rose-200"
      : tone === "soft"
        ? "bg-slate-100 text-slate-700 border-slate-200"
        : "bg-slate-950 text-white border-slate-950";
  return (
    <div
      className={`inline-flex items-center justify-center rounded-md border px-3 py-2 text-xs font-semibold ${toneClass} ${
        active ? "ring-2 ring-emerald-400" : ""
      }`}
    >
      {children}
    </div>
  );
}

function ShopReplay({ events, step, url }: { events: BrowserEvent[]; step: number; url?: string }) {
  const path = new URL(url ?? "https://demo-shop.local/login").pathname;
  const email = valueFor(events, step, "#email");
  const password = valueFor(events, step, "#password") ? "*******" : "";
  const search = valueFor(events, step, "#search");
  const lastSelector = lastTarget(events, step);
  const checkoutFailed = hasEvent(
    events,
    step,
    (e) => e.eventType === "network" && e.network?.path === "/api/checkout" && e.network?.status >= 500,
  );
  const added = hasEvent(events, step, (e) => e.target?.selector?.includes("aurora-1"));

  if (path.includes("success")) {
    return (
      <Shell url={url}>
        <div className="h-full grid place-items-center bg-emerald-50">
          <div className="text-center space-y-3">
            <div className="text-5xl text-emerald-600">OK</div>
            <h2 className="text-2xl font-bold">Order confirmed</h2>
            <p className="text-sm text-slate-600">Aurora wireless headphones will ship today.</p>
          </div>
        </div>
      </Shell>
    );
  }

  if (path.includes("checkout")) {
    return (
      <Shell url={url}>
        <div className="h-full p-6 bg-slate-50">
          <div className="mx-auto max-w-xl space-y-4">
            <h2 className="text-xl font-bold">Checkout</h2>
            {checkoutFailed && (
              <div className="rounded-md bg-rose-100 border border-rose-200 px-3 py-2 text-sm text-rose-700">
                Checkout failed. Retry is available.
              </div>
            )}
            <div className="rounded-lg border border-slate-200 bg-white p-4 flex items-center justify-between">
              <div>
                <div className="font-semibold">Aurora headphones</div>
                <div className="text-sm text-slate-500">Noise cancelling, midnight black</div>
              </div>
              <div className="font-bold">$199</div>
            </div>
            <div className="flex gap-3">
              <Action active={lastSelector === "#place-order"}>Place order</Action>
              <Action tone="danger" active={lastSelector === ".promo-ad"}>Special offer</Action>
            </div>
          </div>
        </div>
      </Shell>
    );
  }

  if (path.includes("search")) {
    return (
      <Shell url={url}>
        <div className="h-full p-6 bg-slate-50">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">Search results</h2>
            <Action tone="soft" active={lastSelector === "#checkout"}>
              Checkout {added ? "(1)" : ""}
            </Action>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="rounded-lg border border-slate-200 bg-white p-4 space-y-3">
              <div className="h-20 rounded bg-slate-200" />
              <div className="font-semibold">Aurora headphones</div>
              <div className="text-xs text-slate-500">Wireless headphones</div>
              <Action active={lastSelector?.includes("aurora-1")}>Add to cart</Action>
            </div>
            <div className="rounded-lg border border-slate-200 bg-white p-4 space-y-3 opacity-70">
              <div className="h-20 rounded bg-slate-200" />
              <div className="font-semibold">Desk speaker</div>
              <div className="text-xs text-slate-500">Portable audio</div>
              <Action tone="soft">View</Action>
            </div>
          </div>
        </div>
      </Shell>
    );
  }

  if (path.includes("dashboard")) {
    return (
      <Shell url={url}>
        <div className="h-full p-6 bg-slate-50">
          <h2 className="text-xl font-bold mb-4">Dashboard</h2>
          <div className="flex gap-2">
            <div className="flex-1">
              <Field label="Search products" value={search} active={lastSelector === "#search"} />
            </div>
            <Action active={lastSelector === "#search-btn"}>Search</Action>
          </div>
          <div className="mt-6 grid grid-cols-3 gap-3 text-sm">
            {["Headphones", "Speakers", "Adapters"].map((item) => (
              <div key={item} className="rounded-lg border border-slate-200 bg-white p-4">
                {item}
              </div>
            ))}
          </div>
        </div>
      </Shell>
    );
  }

  return (
    <Shell url={url}>
      <div className="h-full grid place-items-center bg-slate-50">
        <div className="w-80 space-y-3 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-xl font-bold">Demo Shop</h2>
          <Field label="Email" value={email} active={lastSelector === "#email"} />
          <Field label="Password" value={password} active={lastSelector === "#password"} />
          <Action active={lastSelector === "button[type=submit]"}>Sign in</Action>
        </div>
      </div>
    </Shell>
  );
}

function CrmReplay({ events, step, url }: { events: BrowserEvent[]; step: number; url?: string }) {
  const path = new URL(url ?? "https://demo-crm.local/leads").pathname;
  const name = valueFor(events, step, "#name");
  const company = valueFor(events, step, "#company");
  const lastSelector = lastTarget(events, step);

  if (path.includes("/deals")) {
    return (
      <Shell url={url}>
        <div className="h-full p-6 bg-indigo-50">
          <div className="rounded-lg bg-white border border-indigo-100 p-5">
            <div className="text-xs uppercase text-indigo-500">Deal created</div>
            <h2 className="text-2xl font-bold">{company || "Acme Inc"}</h2>
            <p className="text-sm text-slate-600">Owner: {name || "Dana Lee"}</p>
          </div>
        </div>
      </Shell>
    );
  }

  if (path.includes("/leads/new")) {
    return (
      <Shell url={url}>
        <div className="h-full p-6 bg-slate-50">
          <div className="mx-auto max-w-md space-y-3 rounded-xl border border-slate-200 bg-white p-5">
            <h2 className="text-xl font-bold">New lead</h2>
            <Field label="Full name" value={name} active={lastSelector === "#name"} />
            <Field label="Company" value={company} active={lastSelector === "#company"} />
            <Action active={lastSelector === "#save"}>Save lead</Action>
          </div>
        </div>
      </Shell>
    );
  }

  if (path.includes("/leads/42")) {
    return (
      <Shell url={url}>
        <div className="h-full p-6 bg-slate-50">
          <div className="rounded-lg bg-white border border-slate-200 p-5 space-y-3">
            <div className="text-xs uppercase text-slate-500">Qualified lead</div>
            <h2 className="text-2xl font-bold">{name || "Dana Lee"}</h2>
            <p className="text-sm text-slate-600">{company || "Acme Inc"}</p>
            <Action active={lastSelector === "#convert"}>Convert to deal</Action>
          </div>
        </div>
      </Shell>
    );
  }

  return (
    <Shell url={url}>
      <div className="h-full p-6 bg-slate-50">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold">Leads</h2>
          <Action active={lastSelector === "#new-lead"}>New lead</Action>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white divide-y">
          {["Northstar Supply", "Helio Labs", "Riverside Co"].map((lead) => (
            <div key={lead} className="p-3 text-sm">
              {lead}
            </div>
          ))}
        </div>
      </div>
    </Shell>
  );
}

function CalendarReplay({ events, step, url }: { events: BrowserEvent[]; step: number; url?: string }) {
  const title = valueFor(events, step, "#title");
  const time = valueFor(events, step, "#time");
  const formOpen = hasEvent(events, step, (e) => e.target?.selector === "#new-event");
  const saved = hasEvent(events, step, (e) => e.eventType === "assertion");
  const lastSelector = lastTarget(events, step);

  return (
    <Shell url={url}>
      <div className="h-full p-6 bg-slate-50">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold">Calendar</h2>
          <Action active={lastSelector === "#new-event"}>New event</Action>
        </div>
        <div className="grid grid-cols-5 gap-2 text-xs text-slate-500">
          {["Mon", "Tue", "Wed", "Thu", "Fri"].map((day) => (
            <div key={day} className="h-32 rounded-lg border border-slate-200 bg-white p-2">
              <div>{day}</div>
              {saved && day === "Wed" && (
                <div className="mt-3 rounded bg-emerald-100 text-emerald-700 p-2">
                  {title || "Design review"} at {time || "14:00"}
                </div>
              )}
            </div>
          ))}
        </div>
        {formOpen && !saved && (
          <div className="absolute inset-x-10 bottom-8 rounded-xl bg-white border border-slate-200 p-4 shadow-lg space-y-3">
            <h3 className="font-bold">New event</h3>
            <Field label="Event title" value={title} active={lastSelector === "#title"} />
            <Field label="Start time" value={time} active={lastSelector === "#time"} />
            <Action active={lastSelector === "#save"}>Save event</Action>
          </div>
        )}
        {saved && (
          <div className="absolute bottom-8 right-8 rounded-md bg-emerald-600 px-3 py-2 text-sm text-white">
            Event saved
          </div>
        )}
      </div>
    </Shell>
  );
}

function BrowserSurface({ events, step, url }: { events: BrowserEvent[]; step: number; url?: string }) {
  if (url?.includes("demo-crm")) return <CrmReplay events={events} step={step} url={url} />;
  if (url?.includes("demo-calendar")) return <CalendarReplay events={events} step={step} url={url} />;
  return <ShopReplay events={events} step={step} url={url} />;
}

export function ReplayPanel({
  events,
  step,
  maxStep,
  onStep,
}: {
  events: BrowserEvent[];
  step: number;
  maxStep: number;
  onStep: (n: number) => void;
}) {
  const snap = reconstructAt(events, step);
  return (
    <Card title="Browser Replay">
      <div className="aspect-video rounded-lg bg-black/40 border border-white/5 relative overflow-hidden">
        <BrowserSurface events={events} step={step} url={snap.url} />
      </div>

      <input
        type="range"
        min={0}
        max={maxStep}
        value={step}
        onChange={(e) => onStep(Number(e.target.value))}
        className="w-full mt-3 accent-emerald-400"
      />

      <div className="mt-2 grid grid-cols-3 gap-2 text-[11px] text-gray-400">
        <div>
          <div className="text-gray-500">Step</div>
          {step} / {maxStep}
        </div>
        <div>
          <div className="text-gray-500">Network</div>
          {snap.network.length} call(s)
        </div>
        <div>
          <div className="text-gray-500">Last action</div>
          {snap.lastAction?.eventType ?? "-"}
        </div>
      </div>

      {snap.network.length > 0 && (
        <div className="mt-2 text-[11px] font-mono space-y-0.5">
          {snap.network.slice(-3).map((n, i) => (
            <div key={i} className={n.status >= 400 ? "text-red-400" : "text-gray-400"}>
              {n.method} {n.path} -&gt; {n.status} ({n.latencyMs}ms)
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
