"use client";

import { useCallback, useEffect, useState } from "react";

import { fetchHealth, type HealthResponse } from "@/lib/api";
import { API_URL } from "@/lib/config";

type State =
  | { kind: "loading" }
  | { kind: "ok"; data: HealthResponse }
  | { kind: "error"; message: string };

const COMPONENT_LABELS: Record<string, string> = {
  database: "Database",
  redis: "Redis",
};

export function BackendStatus() {
  const [state, setState] = useState<State>({ kind: "loading" });

  const load = useCallback(async (signal?: AbortSignal) => {
    setState({ kind: "loading" });
    try {
      setState({ kind: "ok", data: await fetchHealth(signal) });
    } catch (err) {
      if (signal?.aborted) return;
      setState({
        kind: "error",
        message: err instanceof Error ? err.message : "Unknown error",
      });
    }
  }, []);

  useEffect(() => {
    const ctrl = new AbortController();
    void load(ctrl.signal);
    return () => ctrl.abort();
  }, [load]);

  return (
    <section
      aria-labelledby="backend-status-title"
      className="rounded-2xl border border-border bg-card p-5 shadow-sm"
    >
      <div className="flex items-center justify-between gap-3">
        <h2 id="backend-status-title" className="text-base font-semibold">
          Backend holati
        </h2>
        <button
          type="button"
          onClick={() => void load()}
          className="rounded-lg border border-border px-3 py-1.5 text-sm hover:bg-background"
        >
          Yangilash
        </button>
      </div>

      {state.kind === "loading" && (
        <p className="mt-4 text-sm text-muted" data-testid="backend-status">
          Tekshirilmoqda…
        </p>
      )}

      {state.kind === "error" && (
        <div className="mt-4 text-sm" data-testid="backend-status" data-status="offline">
          <p className="font-medium text-red-600">Backend bilan aloqa yo‘q</p>
          <p className="mt-1 text-muted">
            {API_URL} manziliga ulanib bo‘lmadi ({state.message}). Backend ishga tushganini
            tekshiring.
          </p>
        </div>
      )}

      {state.kind === "ok" && (
        <div className="mt-4 space-y-3 text-sm" data-testid="backend-status" data-status={state.data.status}>
          <p>
            <StatusDot ok={state.data.status === "ok"} />
            <span className="font-medium">
              {state.data.status === "ok" ? "Ishlayapti" : "Qisman ishlayapti"}
            </span>
            <span className="text-muted">
              {" "}
              · v{state.data.version} · {state.data.environment}
            </span>
          </p>
          <ul className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            {Object.entries(state.data.components).map(([name, c]) => (
              <li
                key={name}
                className="flex items-center justify-between rounded-lg border border-border px-3 py-2"
              >
                <span>{COMPONENT_LABELS[name] ?? name}</span>
                <span className={c.ok ? "text-emerald-600" : "text-amber-600"}>
                  {c.ok ? "OK" : `Yo‘q${c.error ? ` (${c.error})` : ""}`}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

function StatusDot({ ok }: { ok: boolean }) {
  return (
    <span
      aria-hidden
      className={`mr-2 inline-block h-2.5 w-2.5 rounded-full ${ok ? "bg-emerald-500" : "bg-amber-500"}`}
    />
  );
}
