/**
 * Centralized backend API URL resolution.
 *
 * Production (Vercel): browser calls same-origin `/api/*` → Vercel rewrites → Render.
 * This avoids CORS issues when Render CORS_ORIGINS is not configured.
 *
 * Set NEXT_PUBLIC_API_BASE_URL on Vercel to your Render URL (used for rewrites).
 */
function directBackendUrl(): string {
  const raw =
    process.env.NEXT_PUBLIC_API_BASE_URL?.trim() ||
    process.env.NEXT_PUBLIC_API_URL?.trim() ||
    process.env.API_BASE_URL?.trim() ||
    "";
  return raw.replace(/\/+$/, "");
}

function vercelDeploymentOrigin(): string {
  const host = process.env.VERCEL_URL?.trim();
  if (!host) return "";
  return `https://${host.replace(/\/+$/, "")}`;
}

/** True when requests should use same-origin /api proxy (no CORS). */
export function usesApiProxy(): boolean {
  return process.env.NODE_ENV === "production" && Boolean(directBackendUrl());
}

export function getApiBaseUrl(): string {
  const direct = directBackendUrl();

  if (process.env.NODE_ENV === "production" && direct) {
    // Browser: same-origin proxy
    if (typeof window !== "undefined") {
      return "";
    }
    // SSR on Vercel: hit own deployment so rewrites forward to Render
    const vercel = vercelDeploymentOrigin();
    if (vercel) return vercel;
    return direct;
  }

  if (direct) return direct;

  if (process.env.NODE_ENV === "development") {
    return "http://localhost:8000";
  }

  return "";
}

export function apiUrl(path: string): string {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  const base = getApiBaseUrl();

  if (!base) {
    if (usesApiProxy() || (typeof window !== "undefined" && process.env.NODE_ENV === "production")) {
      return normalized;
    }
    throw new Error(
      "NEXT_PUBLIC_API_BASE_URL is not configured. Set it to your Render backend URL in Vercel project settings.",
    );
  }

  return `${base}${normalized}`;
}
