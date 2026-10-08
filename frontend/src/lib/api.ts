import { API_URL } from "./config";

export type ComponentStatus = { ok: boolean; error?: string | null };

export type HealthResponse = {
  status: "ok" | "degraded";
  app: string;
  version: string;
  environment: string;
  components: Record<string, ComponentStatus>;
};

export type ApiError = { code: string; message: string; request_id?: string };

export async function fetchHealth(signal?: AbortSignal): Promise<HealthResponse> {
  const res = await fetch(`${API_URL}/health`, { signal, cache: "no-store" });
  // /health returns a body on 503 too (degraded) — show it instead of failing.
  if (!res.ok && res.status !== 503) {
    throw new Error(`Backend returned HTTP ${res.status}`);
  }
  return (await res.json()) as HealthResponse;
}
