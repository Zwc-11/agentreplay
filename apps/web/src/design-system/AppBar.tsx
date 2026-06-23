import { useEffect, useState } from "react";
import { pingApi } from "../lib/api";
import { Logo } from "./Logo";
import { Tabs, type Tab } from "./Tabs";

const REPO = "https://github.com/Zwc-11/agentreplay";

function ConnectionStatus() {
  const [live, setLive] = useState<boolean | null>(null);
  useEffect(() => {
    let alive = true;
    pingApi().then((ok) => alive && setLive(ok));
    return () => {
      alive = false;
    };
  }, []);
  if (live === null) return null;
  return (
    <span
      className="hidden sm:inline-flex items-center gap-1.5 text-[11px] text-gray-400"
      title={live ? "Connected to the AgentReplay API" : "API not reachable — showing bundled demo data"}
    >
      <span className="w-1.5 h-1.5 rounded-full" style={{ background: live ? "#34d399" : "#fbbf24" }} />
      {live ? "Live API" : "Demo mode"}
    </span>
  );
}

export function AppBar({ nav, active, onNav }: { nav: Tab[]; active: string; onNav: (id: string) => void }) {
  return (
    <header className="sticky top-0 z-20 border-b border-white/5 bg-ink/80 backdrop-blur">
      <div className="max-w-[1400px] mx-auto px-4 h-14 flex items-center gap-4">
        <div className="flex items-center gap-2">
          <Logo />
          <span className="font-semibold tracking-tight text-gray-100">AgentReplay</span>
          <span className="hidden md:inline text-[11px] text-gray-500 border-l border-white/10 pl-2.5 ml-1">
            browser workflow flight recorder
          </span>
        </div>
        <nav className="ml-1">
          <Tabs tabs={nav} active={active} onChange={onNav} />
        </nav>
        <div className="ml-auto flex items-center gap-4">
          <ConnectionStatus />
          <a href={REPO} target="_blank" rel="noreferrer" className="text-xs text-gray-400 hover:text-gray-200 transition-colors">
            GitHub&nbsp;↗
          </a>
        </div>
      </div>
    </header>
  );
}
