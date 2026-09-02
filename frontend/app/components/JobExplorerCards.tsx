import { formatLabel } from "../../lib/format";
import type { EnterpriseJob, JobSkill } from "../../lib/types";

export function JobExplorerCards({
  jobs,
  jobSkills,
}: {
  jobs: EnterpriseJob[];
  jobSkills: JobSkill[];
}) {
  if (!jobs.length) {
    return <p className="text-sm text-muted">No SAP records available for jobs.</p>;
  }

  return (
    <ul className="grid gap-4 md:grid-cols-2">
      {jobs.map((job) => {
        const skills = jobSkills.filter((s) => s.job_id === job.job_id);
        return (
          <li key={job.job_id} className="surface-card p-5">
            <p className="kicker">{job.is_target ? "Target role" : job.family ?? "Role"}</p>
            <h3 className="mt-2 font-display text-xl text-ink">{job.job_name}</h3>
            <p className="mt-1 text-sm text-muted">{job.location}</p>
            <p className="mt-3 text-xs text-muted">
              {job.required_skill_count ?? skills.length} required capabilities
              {job.mandatory_skill_count != null ? ` · ${job.mandatory_skill_count} mandatory` : ""}
            </p>
            {job.job_description && (
              <p className="font-body mt-3 line-clamp-3 text-sm text-muted">{job.job_description}</p>
            )}
            <ul className="mt-4 space-y-1 text-xs">
              {skills.slice(0, 6).map((s) => (
                <li key={`${s.job_id}-${s.skill_id}`} className="flex justify-between gap-2">
                  <span>{formatLabel(s.skill_name || s.skill_id)}</span>
                  <span className="text-muted">
                    {s.is_mandatory ? "Required" : "Optional"} {s.required_proficiency?.toFixed(2)}
                  </span>
                </li>
              ))}
            </ul>
          </li>
        );
      })}
    </ul>
  );
}
