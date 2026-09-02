"use client";

import { useCallback, useEffect, useState } from "react";
import {
  fetchCatalogHealth,
  studentCreateSkill,
  studentDeleteSkill,
  studentGetAllSkills,
  studentGetSkill,
  studentUpdateSkill,
} from "../../lib/api";
import { AppHeader } from "../components/AppShell";

type SkillRecord = {
  SkillId: string;
  SkillName: string;
  Description: string;
};

type LogLine = { text: string; cls: string };

export function StudentSkillClient() {
  const [health, setHealth] = useState<Awaited<ReturnType<typeof fetchCatalogHealth>> | null>(null);
  const [skillId, setSkillId] = useState("SKILL0001");
  const [skillName, setSkillName] = useState("");
  const [description, setDescription] = useState("JAVA");
  const [records, setRecords] = useState<SkillRecord[]>([]);
  const [logs, setLogs] = useState<LogLine[]>([]);
  const [busy, setBusy] = useState(false);

  const sapMode = health?.source_mode ?? "NOT_CONNECTED";
  const liveVerified = Boolean(health?.live_verified);

  const appendLogs = useCallback((lines: string[], ok: boolean) => {
    setLogs((prev) => [
      ...prev,
      ...lines.map((text) => ({
        text,
        cls: text.startsWith("Step") ? "log-step" : ok ? "log-success" : "log-error",
      })),
    ]);
  }, []);

  useEffect(() => {
    void fetchCatalogHealth().then(setHealth).catch(() => null);
  }, []);

  function buildPayload() {
    return { SkillId: skillId, SkillName: skillName, Description: description };
  }

  function resetSample() {
    setSkillId("SKILL0001");
    setSkillName("");
    setDescription("JAVA");
  }

  function loadRecord(rec: SkillRecord) {
    setSkillId(rec.SkillId ?? "");
    setSkillName(rec.SkillName ?? "");
    setDescription(rec.Description ?? "");
    appendLogs([`Loaded skill ${rec.SkillId} into the form.`], true);
  }

  async function runAction(
    label: string,
    fn: () => Promise<{ ok: boolean; log?: string[]; detail?: string; item?: Record<string, unknown> }>,
    onSuccess?: (result: { ok: boolean; item?: Record<string, unknown> }) => void,
  ) {
    setBusy(true);
    try {
      const result = await fn();
      appendLogs(result.log ?? [], result.ok);
      if (result.ok) {
        appendLogs([`${label} succeeded.`], true);
        onSuccess?.(result);
      } else {
        appendLogs([`${label} failed.`], false);
        const sapMsg = (result as { sap_message?: string }).sap_message;
        if (sapMsg) appendLogs([`SAP: ${sapMsg}`], false);
        else if (result.detail) appendLogs([result.detail.slice(0, 500)], false);
      }
    } catch (err) {
      appendLogs([err instanceof Error ? err.message : "Request failed."], false);
    }
    setBusy(false);
  }

  return (
    <div className="rework-atmosphere min-h-screen">
      <AppHeader badge="Student" activePath="/student" sapMode={sapMode} liveVerified={liveVerified} />

      <main className="rework-content mx-auto max-w-6xl px-6 py-8">
        <div className="mb-6">
          <p className="kicker">SAP Gateway OData</p>
          <h1 className="font-display text-2xl font-semibold text-ink">Skill CRUD — ZREWORK_SKILL_SRV</h1>
          <p className="mt-2 text-sm text-muted">
            Student workspace for reading, creating, updating, and deleting skills. SAP credentials stay on the backend.
          </p>
        </div>

        <div className="mb-6 rounded-lg border border-amber/30 bg-amber/10 px-4 py-3 text-sm text-amber">
          <strong className="text-ink">Create tips:</strong> Click <strong>Get all</strong> first, then use a{" "}
          <strong>new SkillId</strong> (e.g. SKILL0010) that is not already in the table. SkillName and Description are
          required. Max 100 characters each.
        </div>

        <div className="grid gap-6 lg:grid-cols-[minmax(0,400px)_1fr]">
          <div className="panel space-y-4">
            <h2 className="text-xs font-semibold uppercase tracking-wide text-accent">Skill record</h2>
            <label className="flex flex-col gap-1 text-xs font-medium text-muted">
              <span>Skill ID (SkillId)</span>
              <input
                className="w-full rounded-md border border-border bg-surface px-3 py-2 font-mono text-sm text-ink shadow-sm focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
                value={skillId}
                onChange={(e) => setSkillId(e.target.value)}
              />
            </label>
            <label className="flex flex-col gap-1 text-xs font-medium text-muted">
              <span>Skill Name (SkillName)</span>
              <input
                className="w-full rounded-md border border-border bg-surface px-3 py-2 font-mono text-sm text-ink shadow-sm focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
                value={skillName}
                onChange={(e) => setSkillName(e.target.value)}
              />
            </label>
            <label className="flex flex-col gap-1 text-xs font-medium text-muted">
              <span>Description</span>
              <input
                className="w-full rounded-md border border-border bg-surface px-3 py-2 font-mono text-sm text-ink shadow-sm focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </label>

            <button type="button" className="btn-secondary w-full text-sm" onClick={resetSample} disabled={busy}>
              Reset to sample data
            </button>

            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                className="btn-secondary text-sm"
                disabled={busy}
                onClick={() =>
                  void runAction("Get by ID", () => studentGetSkill(skillId), (r) => {
                    const rec = r.item as SkillRecord | undefined;
                    if (rec?.SkillId) loadRecord(rec);
                  })
                }
              >
                Get by ID
              </button>
              <button
                type="button"
                className="btn-secondary text-sm"
                disabled={busy}
                onClick={() =>
                  void runAction("Get all", () => studentGetAllSkills(), (r) => {
                    const rows = (r.item?.records as SkillRecord[] | undefined) ?? [];
                    setRecords(rows);
                  })
                }
              >
                Get all
              </button>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                className="btn-primary text-sm"
                disabled={busy}
                onClick={() => void runAction("Create", () => studentCreateSkill(buildPayload()))}
              >
                Create
              </button>
              <button
                type="button"
                className="btn-secondary border-amber/40 bg-amber/15 text-ink text-sm hover:bg-amber/25"
                disabled={busy}
                onClick={() => void runAction("Update", () => studentUpdateSkill(buildPayload()))}
              >
                Update
              </button>
            </div>
            <button
              type="button"
              className="w-full rounded-md border border-red-300 px-3 py-2 text-sm font-semibold text-red-700 hover:bg-red-50"
              disabled={busy}
              onClick={() => {
                if (!confirm(`Delete skill ${skillId}? This cannot be undone.`)) return;
                void runAction("Delete", () => studentDeleteSkill(skillId));
              }}
            >
              Delete skill by ID above
            </button>
          </div>

          <div>
            <div className="mb-2 flex items-center justify-between">
              <h2 className="text-xs font-semibold uppercase tracking-wide text-muted">Request log</h2>
              <button type="button" className="text-xs text-muted hover:text-ink" onClick={() => setLogs([])}>
                Clear
              </button>
            </div>
            <div className="student-terminal min-h-[420px] rounded-lg p-4 font-mono text-xs leading-relaxed">
              {logs.length === 0 ? (
                <p className="text-muted italic">No requests sent yet. Fill in the form, then Get, Create, Update, or Delete.</p>
              ) : (
                logs.map((line, i) => (
                  <div key={i} className={`student-log-${line.cls} mb-1 whitespace-pre-wrap break-words`}>
                    {line.text}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {records.length > 0 && (
          <section className="panel mt-8">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-xs font-semibold uppercase tracking-wide text-accent">Skill records</h2>
              <span className="text-xs text-muted">{records.length} record(s) — click a row to load into the form</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left font-mono text-xs">
                <thead>
                  <tr className="border-b border-border text-[10px] uppercase tracking-wide text-muted">
                    <th className="py-2 pr-4">ID</th>
                    <th className="py-2 pr-4">Name</th>
                    <th className="py-2">Description</th>
                  </tr>
                </thead>
                <tbody>
                  {records.map((rec) => (
                    <tr
                      key={rec.SkillId}
                      className="cursor-pointer border-b border-border/60 hover:bg-parchment/60"
                      onClick={() => loadRecord(rec)}
                    >
                      <td className="py-2 pr-4">{rec.SkillId}</td>
                      <td className="py-2 pr-4">{rec.SkillName}</td>
                      <td className="py-2">{rec.Description}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
