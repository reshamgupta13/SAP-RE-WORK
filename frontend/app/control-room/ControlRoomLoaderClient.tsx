"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { executeProductCase, fetchControlRoom } from "../../lib/api";
import { AppHeader } from "../components/AppShell";
import { ControlRoomClient } from "./ControlRoomClient";
import type { ControlRoomData } from "../../lib/types";

const PIPELINE_STEPS = [
  "Reading SAP workforce records (USER, SKILL, JOB)",
  "Running candidate intelligence agent",
  "Decomposing role requirements",
  "Diagnosing capability gaps with Groq LLM",
  "Generating pathway and targeted learning",
  "Preparing Control Room view",
];

export function ControlRoomLoaderClient({ caseId }: { caseId: string }) {
  const [step, setStep] = useState(0);
  const [data, setData] = useState<ControlRoomData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const timers: ReturnType<typeof setInterval>[] = [];

    const advance = setInterval(() => {
      setStep((s) => Math.min(s + 1, PIPELINE_STEPS.length - 1));
    }, 8000);
    timers.push(advance);

    void (async () => {
      try {
        await executeProductCase(caseId);
        if (cancelled) return;
        const room = await fetchControlRoom(caseId);
        if (cancelled) return;
        setData(room);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Intelligence pipeline failed.");
        }
      }
    })();

    return () => {
      cancelled = true;
      timers.forEach(clearInterval);
    };
  }, [caseId]);

  if (data) {
    return <ControlRoomClient data={data} />;
  }

  if (error) {
    return (
      <div className="rework-atmosphere min-h-screen">
        <AppHeader badge="Control Room" activePath="/control-room" showCta={false} />
        <main className="rework-content mx-auto max-w-3xl px-6 py-12 text-center">
          <p className="text-muted">Diagnosis could not complete.</p>
          <p className="mt-2 text-sm text-amber">{error}</p>
          <p className="mt-4 text-sm text-muted">
            Ensure the backend is running on port 8000 and your Groq API key is set in backend/.env.
          </p>
          <Link href="/workspace" className="btn-primary mt-6 inline-flex">
            Back to workspace
          </Link>
        </main>
      </div>
    );
  }

  return (
    <div className="rework-atmosphere min-h-screen">
      <AppHeader badge="Control Room" activePath="/control-room" showCta={false} />
      <main className="rework-content mx-auto max-w-2xl px-6 py-16">
        <p className="kicker">SAP + Groq intelligence pipeline</p>
        <h1 className="section-heading mt-2">Diagnosing this pairing…</h1>
        <p className="mt-3 text-sm text-muted">
          RE:WORK is running the full LangGraph pipeline over SAP-shaped workforce data. This usually takes
          30–90 seconds while Groq agents analyze gaps, pathways, and learning needs.
        </p>

        <ol className="mt-8 space-y-3">
          {PIPELINE_STEPS.map((label, i) => {
            const done = i < step;
            const active = i === step;
            return (
              <li
                key={label}
                className={`flex items-start gap-3 rounded-lg border px-4 py-3 text-sm ${
                  active ? "border-accent bg-accent/5" : done ? "border-sage/30 bg-sage/5" : "border-border text-muted"
                }`}
              >
                <span className="mt-0.5 font-mono text-xs">{done ? "✓" : active ? "…" : "·"}</span>
                <span className={active ? "font-medium text-ink" : ""}>{label}</span>
              </li>
            );
          })}
        </ol>

        <p className="mt-6 text-center text-xs text-muted">Case {caseId}</p>
      </main>
    </div>
  );
}
