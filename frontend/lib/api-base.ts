/**
 * Centralized backend API base URL.
 * Production: set NEXT_PUBLIC_API_BASE_URL on Vercel (public URL only — no secrets).
 * Development: defaults to http://localhost:8000
 */
export function getApiBaseUrl(): string {
  const raw =
    process.env.NEXT_PUBLIC_API_BASE_URL?.trim() ||
    process.env.NEXT_PUBLIC_API_URL?.trim() ||
    "";

  if (raw) {
    return raw.replace(/\/+$/, "");
  }

  if (process.env.NODE_ENV === "development") {
    return "http://localhost:8000";
  }

  return "";
}

export function apiUrl(path: string): string {
  const base = getApiBaseUrl();
  if (!base) {
    throw new Error(
      "NEXT_PUBLIC_API_BASE_URL is not configured. Set it to your Render backend URL in Vercel project settings.",
    );
  }
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${base}${normalized}`;
}
