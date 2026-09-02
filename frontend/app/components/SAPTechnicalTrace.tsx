"use client";

import { useState } from "react";
import { formatLabel } from "../../lib/format";
import type { SapTraceRow } from "../../lib/types";

export function SAPTechnicalTrace({
  rows,
  writeAvailable,
  writeReason,
}: {
  rows?: SapTraceRow[];
  writeAvailable?: boolean;
  writeReason?: string;
}) {
  const [open, setOpen] = useState(false);
  if (!rows?.length) return null;

  return (
    <section className="surface-panel p-4">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between text-left text-xs font-medium text-ocean"
      >
        {open ? "Hide technical details" : "View technical details"}
      </button>
      {open && (
        <div className="mt-3 space-y-3 font-mono text-[10px] text-muted">
          <p>OData entity sets: PENDING_OFFICIAL_ODATA_METADATA</p>
          <p>Write operations: {writeAvailable ? "available" : "disabled"}{writeReason ? ` — ${writeReason}` : ""}</p>
          <ul className="space-y-2">
            {rows.map((row) => (
              <li key={row.sap_table} className="rounded border border-border bg-surface px-2 py-2">
                <p className="text-ink">{row.product_label}</p>
                <p>
                  {row.sap_table} → {row.odata_entity} → {row.odata_method}
                </p>
                <p>
                  {row.rework_model} → {row.agent} · {row.record_count} records · {formatLabel(row.source_mode)}
                </p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
