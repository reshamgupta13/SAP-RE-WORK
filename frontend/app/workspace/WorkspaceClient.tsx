"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import {
  createProductCase,
  fetchCandidates,
  fetchCatalogHealth,
  fetchJobs,
  mutateCatalog,
} from "../../lib/api";
import { AppHeader } from "../components/AppShell";
import { SourceBadge } from "../components/SourceBadge";

type Row = Record<string, unknown>;

export function WorkspaceClient() {
  const router = useRouter();
  const [health, setHealth] = useState<Awaited<ReturnType<typeof fetchCatalogHealth>> | null>(null);
  const [candidates, setCandidates] = useState<Row[]>([]);
  const [jobs, setJobs] = useState<Row[]>([]);
  const [candQuery, setCandQuery] = useState("");
  const [jobQuery, setJobQuery] = useState("");
  const [selectedUser, setSelectedUser] = useState<string | null>(null);
  const [selectedJob, setSelectedJob] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [creating, setCreating] = useState(false);
  const [diagnoseStep, setDiagnoseStep] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [newFirst, setNewFirst] = useState("");
  const [newLast, setNewLast] = useState("");
  const [newRole, setNewRole] = useState("");

  const sapMode = health?.source_mode ?? "NOT_CONNECTED";
  const writes = Boolean(health?.write_operations?.available);

  async function reload(qCand?: string, qJob?: string) {
    setBusy(true);
    try {
      const [h, c, j] = await Promise.all([
        fetchCatalogHealth(),
        fetchCandidates(qCand),
        fetchJobs(qJob),
      ]);
      setHealth(h);
      setCandidates(c.items ?? []);
      setJobs(j.items ?? []);
      const hasData = (c.items?.length ?? 0) > 0 || (j.items?.length ?? 0) > 0;
      if (h.prototype_demo || c.prototype_demo || j.prototype_demo) {
        setMessage(
          "SAP workforce data (ZREWORK OData model: USER, JOB, SKILL) with RE:WORK AI reasoning powered by Groq LLM. " +
            "Candidates and roles follow the SAP SuccessFactors integration pattern.",
        );
      } else if (hasData && (h.hybrid_mode || c.hybrid_mode || j.hybrid_mode)) {
        setMessage("SAP LIVE skills OData connected. Candidates and roles use the SAP-aligned prototype catalog.");
      } else if (hasData) {
        setMessage(null);
      } else {
        setMessage(c.message || j.message || h.message || null);
      }
    } catch (err) {
      const raw = err instanceof Error ? err.message : "Unable to reach RE:WORK API.";
      setMessage(
        raw.toLowerCase().includes("fetch") || raw.toLowerCase().includes("failed")
          ? "Cannot reach the RE:WORK API. Ensure NEXT_PUBLIC_API_BASE_URL is set on Vercel and the Render backend is running."
          : raw,
      );
    }
    setBusy(false);
  }

  useEffect(() => {
    void reload();
  }, []);

  const selectedCandidate = useMemo(
    () => candidates.find((c) => String(c.user_id) === selectedUser),
    [candidates, selectedUser],
  );
  const selectedJobRow = useMemo(
    () => jobs.find((j) => String(j.job_id) === selectedJob),
    [jobs, selectedJob],
  );

  async function runCase() {
    if (!selectedUser || !selectedJob) return;
    setCreating(true);
    setDiagnoseStep("Creating SAP workforce case…");
    try {
      const created = await createProductCase(selectedUser, selectedJob);
      setDiagnoseStep("Starting intelligence pipeline…");
      router.push(
        `/control-room?caseId=${encodeURIComponent(created.id)}&run=1&userId=${encodeURIComponent(selectedUser)}&jobId=${encodeURIComponent(selectedJob)}`,
      );
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Could not create the case.");
      setCreating(false);
      setDiagnoseStep(null);
    }
  }

  async function createCandidate() {
    setBusy(true);
    try {
      await mutateCatalog("/api/catalog/candidates", "POST", {
        FIRST_NAME: newFirst,
        LAST_NAME: newLast,
        CURRENT_ROLE: newRole,
      });
      setShowCreate(false);
      setNewFirst("");
      setNewLast("");
      setNewRole("");
      await reload(candQuery, jobQuery);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Create failed.");
    }
    setBusy(false);
  }

  return (
    <div className="rework-atmosphere min-h-screen">
      <AppHeader badge="Workspace" activePath="/workspace" showCta={false} sapMode={sapMode} liveVerified={health?.live_verified} />
      <main className="rework-content mx-auto max-w-6xl space-y-6 px-6 py-8">
        <div>
          <p className="kicker">SAP Hackfest · Workforce workspace</p>
          <h1 className="section-heading mt-2">Select a person to begin</h1>
          <p className="mt-2 max-w-2xl text-sm text-muted">
            RE:WORK reasons over SAP workforce records — capability gaps, roles, and skills from the ZREWORK OData
            services. Choose a candidate and a role, then generate a case. AI diagnosis runs on the backend.{" "}
            <SourceBadge mode={sapMode} liveVerified={health?.live_verified} />
          </p>
        </div>

        {message && (
          <section className="surface-panel border-sage/20 bg-sage/5 p-4 text-sm text-ink">
            <span className="font-medium text-sage">SAP integration</span>
            <p className="mt-1 text-muted">{message}</p>
            <button type="button" className="btn-secondary mt-3 px-3 py-1 text-xs" onClick={() => void reload(candQuery, jobQuery)}>
              Refresh
            </button>
          </section>
        )}

        <div className="grid gap-6 lg:grid-cols-2">
          <section className="surface-card p-6">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="kicker">From SAP</p>
                <h2 className="mt-1 font-display text-xl font-semibold">Candidates</h2>
              </div>
              {writes && (
                <button type="button" className="btn-secondary px-3 py-1 text-xs" onClick={() => setShowCreate((v) => !v)}>
                  + Create candidate
                </button>
              )}
            </div>
            <input
              className="mt-4 w-full rounded-md border border-border bg-surface px-3 py-2 text-sm"
              placeholder="Search people"
              value={candQuery}
              onChange={(e) => setCandQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") void reload(candQuery, jobQuery);
              }}
            />
            {showCreate && (
              <div className="mt-4 space-y-2 rounded-md border border-border p-3">
                <input className="w-full rounded border border-border px-2 py-1 text-sm" placeholder="First name" value={newFirst} onChange={(e) => setNewFirst(e.target.value)} />
                <input className="w-full rounded border border-border px-2 py-1 text-sm" placeholder="Last name" value={newLast} onChange={(e) => setNewLast(e.target.value)} />
                <input className="w-full rounded border border-border px-2 py-1 text-sm" placeholder="Current role" value={newRole} onChange={(e) => setNewRole(e.target.value)} />
                <button type="button" className="btn-primary px-3 py-1 text-xs" disabled={busy} onClick={() => void createCandidate()}>
                  Save to SAP
                </button>
              </div>
            )}
            <ul className="mt-4 space-y-2">
              {candidates.length === 0 && (
                <li className="text-sm text-muted">
                  No candidates are currently available from SAP.
                  {writes ? " Create a candidate through this workspace." : ""}
                </li>
              )}
              {candidates.map((c) => {
                const id = String(c.user_id ?? "");
                return (
                  <li key={id}>
                    <button
                      type="button"
                      onClick={() => setSelectedUser(id)}
                      className={`w-full rounded-lg border px-3 py-3 text-left ${
                        selectedUser === id ? "border-accent bg-accent/5" : "border-border"
                      }`}
                    >
                      <p className="font-medium text-ink">{String(c.display_name || `${c.first_name ?? ""} ${c.last_name ?? ""}`.trim() || id)}</p>
                      <p className="text-xs text-muted">{String(c.current_role ?? "—")} · {String(c.location ?? "—")}</p>
                    </button>
                  </li>
                );
              })}
            </ul>
          </section>

          <section className="surface-card p-6">
            <p className="kicker">From SAP</p>
            <h2 className="mt-1 font-display text-xl font-semibold">Opportunities</h2>
            <input
              className="mt-4 w-full rounded-md border border-border bg-surface px-3 py-2 text-sm"
              placeholder="Search jobs"
              value={jobQuery}
              onChange={(e) => setJobQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") void reload(candQuery, jobQuery);
              }}
            />
            <ul className="mt-4 space-y-2">
              {jobs.length === 0 && <li className="text-sm text-muted">No jobs are currently available from SAP.</li>}
              {jobs.map((j) => {
                const id = String(j.job_id ?? "");
                return (
                  <li key={id}>
                    <button
                      type="button"
                      onClick={() => setSelectedJob(id)}
                      className={`w-full rounded-lg border px-3 py-3 text-left ${
                        selectedJob === id ? "border-accent bg-accent/5" : "border-border"
                      }`}
                    >
                      <p className="font-medium text-ink">{String(j.job_name || id)}</p>
                      <p className="text-xs text-muted">{String(j.location ?? j.org_unit_id ?? "—")}</p>
                    </button>
                  </li>
                );
              })}
            </ul>
          </section>
        </div>

        <section className="surface-card p-6">
          <p className="kicker">RE:WORK</p>
          <h2 className="mt-1 font-display text-xl font-semibold">Open a case</h2>
          <p className="mt-2 text-sm text-muted">
            {selectedCandidate
              ? `Selected candidate: ${String(selectedCandidate.display_name || selectedUser)}`
              : "No candidate selected."}{" "}
            {selectedJobRow ? `Role: ${String(selectedJobRow.job_name || selectedJob)}` : "No role selected."}
          </p>
          <p className="mt-2 text-xs text-muted">
            <span className="font-medium text-ink">How it works:</span> Diagnose creates a case from SAP records,
            then runs Groq-powered agents (gap diagnosis → pathway → targeted learning) and opens the Control Room.
            Expect 30–90 seconds — you will see live pipeline progress.
          </p>
          <div className="mt-4 flex flex-wrap gap-3">
            <button type="button" className="btn-primary" disabled={!selectedUser || !selectedJob || creating} onClick={() => void runCase()}>
              {creating ? (diagnoseStep ?? "Starting…") : "Diagnose this pairing"}
            </button>
            {selectedUser && selectedJob && (
              <Link
                className="btn-secondary"
                href={`/targeted-learning?candidate=${encodeURIComponent(selectedUser)}&role=${encodeURIComponent(selectedJob)}`}
              >
                Targeted learning
              </Link>
            )}
            {selectedUser && (
              <Link className="btn-secondary" href={`/candidate?userId=${encodeURIComponent(selectedUser)}`}>
                Open candidate
              </Link>
            )}
            {selectedJob && (
              <Link className="btn-secondary" href={`/opportunities?jobId=${encodeURIComponent(selectedJob)}`}>
                Open role
              </Link>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
