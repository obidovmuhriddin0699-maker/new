"use client";

import { Button, Card, ErrorBox } from "@/components/ui";
import { useApi } from "@/lib/useApi";
import type { Health } from "@/lib/types";

const LABELS: Record<string, string> = { database: "Ma’lumotlar bazasi", redis: "Redis" };

export function BackendStatus() {
  const { data, error, loading, reload } = useApi<Health>("health");
  return (
    <Card
      title="Tizim holati"
      actions={
        <Button onClick={() => void reload()} loading={loading}>
          Yangilash
        </Button>
      }
    >
      {error ? (
        <div data-testid="backend-status" data-status="offline">
          <ErrorBox error={error} />
        </div>
      ) : data ? (
        <div data-testid="backend-status" data-status={data.status} className="space-y-3 text-sm">
          <p>
            <span className={`mr-2 inline-block h-2.5 w-2.5 rounded-full ${data.status === "ok" ? "bg-emerald-500" : "bg-amber-500"}`} />
            <span className="font-medium">{data.status === "ok" ? "Ishlayapti" : "Qisman ishlayapti"}</span>
            <span className="text-muted">
              {" "}
              · v{data.version} · {data.environment}
            </span>
          </p>
          <ul className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            {Object.entries(data.components).map(([name, c]) => (
              <li key={name} className="flex items-center justify-between rounded-lg border border-border px-3 py-2">
                <span>{LABELS[name] ?? name}</span>
                <span className={c.ok ? "text-emerald-600" : "text-amber-600"}>{c.ok ? "OK" : "Yo‘q"}</span>
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <p className="text-sm text-muted" data-testid="backend-status">
          Tekshirilmoqda…
        </p>
      )}
    </Card>
  );
}
