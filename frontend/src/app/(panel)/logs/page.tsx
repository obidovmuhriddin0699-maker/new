"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Button, Card, EmptyState, ErrorBox, Loading, PageHeader, inputClass } from "@/components/ui";
import { ApiError } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import type { AuditEvent } from "@/lib/types";
import { useApi } from "@/lib/useApi";

const PAGE = 50;

export default function LogsPage() {
  const [action, setAction] = useState("");
  const [status, setStatus] = useState("");
  const [offset, setOffset] = useState(0);
  // Typing in the action filter queries the backend only after a 300 ms pause.
  const [actionQuery, setActionQuery] = useState("");
  useEffect(() => {
    const t = setTimeout(() => setActionQuery(action), 300);
    return () => clearTimeout(t);
  }, [action]);
  const q = new URLSearchParams({ limit: String(PAGE), offset: String(offset) });
  if (actionQuery) q.set("action", actionQuery);
  if (status) q.set("status", status);
  const { data, error, loading, reload } = useApi<{ items: AuditEvent[]; total: number }>(`audit-logs?${q}`);
  const forbidden = error instanceof ApiError && error.status === 403;

  return (
    <>
      <PageHeader title="Tizim loglari" subtitle="Audit jurnali: kim, nima, qachon. Maxfiy ma’lumotlar yashirilgan." actions={<Button onClick={() => void reload()} loading={loading}>Yangilash</Button>} />
      <div className="mb-4 grid gap-2 sm:grid-cols-[1fr_12rem]">
        <input className={inputClass} placeholder="Amal (masalan CONTENT_APPROVED)" value={action} onChange={(e) => { setAction(e.target.value.toUpperCase().trim()); setOffset(0); }} />
        <select className={inputClass} value={status} onChange={(e) => { setStatus(e.target.value); setOffset(0); }} aria-label="Natija">
          <option value="">Barcha natijalar</option>
          <option value="SUCCESS">SUCCESS</option>
          <option value="FAILED">FAILED</option>
          <option value="DENIED">DENIED</option>
        </select>
      </div>
      {forbidden ? (
        <EmptyState title="Ruxsat yo‘q">Tizim loglarini faqat OWNER yoki ADMIN ko‘ra oladi.</EmptyState>
      ) : (
        <ErrorBox error={error} onRetry={reload} />
      )}
      {loading && !data && <Loading />}
      {data && (
        <Card>
          {data.items.length === 0 ? (
            <p className="text-sm text-muted">Yozuvlar yo‘q.</p>
          ) : (
            <ul className="divide-y divide-border text-sm" data-testid="log-list">
              {data.items.map((e) => (
                <li key={e.id} className="py-2">
                  <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
                    <span className="font-mono text-xs text-muted">{formatDateTime(e.timestamp)}</span>
                    <span className="break-all font-medium">{e.action}</span>
                    <span className={`text-xs ${e.status === "SUCCESS" ? "text-emerald-700 dark:text-emerald-300" : "text-red-700 dark:text-red-300"}`}>{e.status}</span>
                  </div>
                  <div className="mt-0.5 text-xs text-muted">
                    {e.actor_name ?? e.actor_type}
                    {e.content_id ? (
                      <> · <Link href={`/content/${e.content_id}`} className="underline">kontent #{e.content_id}</Link>{e.content_version ? ` v${e.content_version}` : ""}</>
                    ) : null}
                    {e.error && <> · {e.error}</>}
                  </div>
                </li>
              ))}
            </ul>
          )}
          <div className="mt-3 flex items-center justify-between text-sm">
            <button type="button" className="rounded-lg border border-border px-3 py-1.5 disabled:opacity-40" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - PAGE))}>Oldingi</button>
            <span className="text-muted">{data.total} ta yozuv</span>
            <button type="button" className="rounded-lg border border-border px-3 py-1.5 disabled:opacity-40" disabled={offset + PAGE >= data.total} onClick={() => setOffset(offset + PAGE)}>Keyingi</button>
          </div>
        </Card>
      )}
    </>
  );
}
