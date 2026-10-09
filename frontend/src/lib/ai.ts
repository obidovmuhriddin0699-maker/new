import { api, ApiError } from "./api";
import type { GenerationResponse } from "./types";

const POLL_MS = 2000;
const MAX_WAIT_MS = 5 * 60 * 1000;

/** POST a generation request; in Celery mode (202, job queued) poll until it finishes. */
export async function runGeneration(path: string, body: unknown, onProgress?: (r: GenerationResponse) => void): Promise<GenerationResponse> {
  let result = await api<GenerationResponse>(path, { method: "POST", body });
  const started = Date.now();
  while (result.job.status === "QUEUED" || result.job.status === "RUNNING") {
    onProgress?.(result);
    if (Date.now() - started > MAX_WAIT_MS) {
      throw new ApiError(504, "ai_timeout", "AI vazifasi juda uzoq davom etmoqda. Keyinroq ‘AI vazifalar’ ro‘yxatini tekshiring.");
    }
    await new Promise((r) => setTimeout(r, POLL_MS));
    result = await api<GenerationResponse>(`ai/jobs/${result.job.id}`);
  }
  if (result.job.status === "FAILED") {
    throw new ApiError(502, `ai_${result.job.error_category ?? "failed"}`, result.job.error ?? "AI generatsiyasi muvaffaqiyatsiz");
  }
  return result;
}
