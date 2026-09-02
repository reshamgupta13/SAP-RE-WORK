/** Human-readable labels for backend enum/snake_case values. */

const ACRONYMS = new Set(["SQL", "SAP", "AI", "HR", "BI", "API", "UI", "ID"]);

const SKILL_LABELS: Record<string, string> = {
  sql: "SQL",
  excel: "Excel",
  communication: "Communication",
  data_analysis: "Data Analysis",
  power_bi: "Power BI",
};

export function formatLabel(value: unknown): string {
  if (value == null || value === "") return "—";
  const str = String(value).trim();
  if (!str.includes("_")) return str;

  return str
    .split("_")
    .filter(Boolean)
    .map((word) => {
      const upper = word.toUpperCase();
      if (ACRONYMS.has(upper)) return upper;
      return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
    })
    .join(" ");
}

export function formatSkillName(skill: string): string {
  return SKILL_LABELS[skill.toLowerCase()] ?? formatLabel(skill);
}

export function formatPathwayId(id: string): string {
  return id
    .replace(/^pathway-/, "")
    .replace(/-/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export function formatOpportunityId(id: string): string {
  return id
    .replace(/^opp-/, "")
    .replace(/-/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export function sapStatusLabel(mode?: string, liveVerified?: boolean): string {
  const m = (mode ?? "NOT_CONNECTED").toUpperCase();
  if (m === "LIVE" && liveVerified) return "SAP • LIVE • VERIFIED";
  if (m === "LIVE") return "SAP • LIVE";
  if (m === "NOT_CONNECTED") return "SAP • CONNECTING";
  if (m === "ERROR") return "SAP • ERROR";
  if (m === "SIMULATED") return "SAP • ODATA MODEL";
  if (m === "MOCKED") return "SAP • DEMO CATALOG";
  return `SAP • ${m}`;
}

export function proficiencyBand(value?: number): string {
  if (value == null) return "Unknown";
  if (value >= 0.7) return "Strong";
  if (value >= 0.5) return "Solid";
  if (value >= 0.35) return "Developing";
  return "Emerging";
}
