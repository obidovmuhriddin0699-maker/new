"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Card, EmptyState, ErrorBox, Loading, PageHeader, StatusBadge, TypeBadge, inputClass } from "@/components/ui";
import { formatDateTime, truncate } from "@/lib/format";
import type { ApprovalLogItem, ContentList } from "@/lib/types";
import { useApi } from "@/lib/useApi";

const DECISION: Record<string, string> = { APPROVED: "Tasdiqlangan", REJECTED: "Rad etilgan", EDIT_REQUESTED: "Tahrir so‘ralgan" };
const CHANNEL: Record<string, string> = { WEB: "Panel", TELEGRAM: "Telegram" };

function waited(from: string, now: number): string {
  const h = Math.max(0, (now - new Date(from).getTime()) / 3600000);
  if (h < 1) return `${Math.round(h * 60)} daqiqa`;
  if (h < 48) return `${Math.round(h)} soat`;
  return `${Math.round(h / 24)} kun`;
}

export default function ApprovalsPage() {
  const [tab, setTab] = useState<"queue" | "history">("queue");
  const [decision, setDecision] = useState("");
  const [channel, setChannel] = useState("");
  const [now, setNow] = useState<number | null>(null);
  useEffect(() => setNow(Date.now()), []);

  const queue = useApi<ContentList>(tab === "queue" ? "contents?status=READY_FOR_REVIEW&sort=waiting&limit=50" : null);
  const q = new URLSearchParams({ limit: "100" });
  if (decision) q.set("decision", decision);
  if (channel) q.set("channel", channel);
  const log = useApi<{ items: ApprovalLogItem[]; total: number }>(tab === "history" ? `approvals?${q}` : null);

  return (
    <>
      <PageHeader title="Tasdiqlar" subtitle="Tasdiq kutayotgan kontent va barcha qarorlar tarixi." />
      <div className="mb-4 flex gap-1" role="tablist" aria-label="Bo‘lim">
        {(["queue", "history"] as const).map((t) => (
          <button key={t} type="button" role="tab" aria-selected={tab === t} onClick={() => setTab(t)} className={`rounded-full px-3 py-1.5 text-sm ${tab === t ? "bg-accent text-accent-fg" : "border border-border bg-card"}`}>
            {t === "queue" ? `Kutayotganlar${queue.data ? ` (${queue.data.total})` : ""}` : "Qarorlar tarixi"}
          </button>
        ))}
      </div>

      {tab === "queue" && (
        <>
          {queue.loading && !queue.data && <Loading />}
          <ErrorBox error={queue.error} onRetry={queue.reload} />
          {queue.data && queue.data.items.length === 0 && <EmptyState title="Tasdiq kutayotgan kontent yo‘q" />}
          {queue.data && queue.data.items.length > 0 && (
            <ul className="space-y-3" data-testid="approval-queue">
              {queue.data.items.map((c) => (
                <li key={c.id}>
                  <Link href={`/content/${c.id}`} className="block rounded-2xl border border-border bg-card p-4 shadow-sm hover:border-accent">
                    <div className="flex flex-wrap items-center gap-2">
                      <StatusBadge status={c.status} />
                      <TypeBadge type={c.content_type} />
                      <span className="text-xs text-muted">v{c.version} · {c.created_by === "AGENT" ? "AI" : "Inson"}</span>
                      {now !== null && <span className="ml-auto text-xs text-muted">kutmoqda: {waited(c.updated_at, now)}</span>}
                    </div>
                    <p className="mt-2 font-medium">{c.topic ?? `Kontent #${c.id}`}</p>
                    {c.caption && <p className="mt-1 text-sm text-muted">{truncate(c.caption, 140)}</p>}
                  </Link>
                </li>
              ))}
            </ul>
          )}
          <p className="mt-3 text-xs text-muted">Eng uzoq kutayotgani birinchi. Ommaviy (bulk) tasdiqlash ataylab yo‘q — har bir kontent alohida ko‘rib chiqiladi.</p>
        </>
      )}

      {tab === "history" && (
        <>
          <div className="mb-4 grid gap-2 sm:grid-cols-2">
            <select aria-label="Qaror" className={inputClass} value={decision} onChange={(e) => setDecision(e.target.value)}>
              <option value="">Barcha qarorlar</option>
              {Object.entries(DECISION).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
            </select>
            <select aria-label="Kanal" className={inputClass} value={channel} onChange={(e) => setChannel(e.target.value)}>
              <option value="">Barcha kanallar</option>
              {Object.entries(CHANNEL).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
            </select>
          </div>
          {log.loading && !log.data && <Loading />}
          <ErrorBox error={log.error} onRetry={log.reload} />
          {log.data && (
            <Card>
              {log.data.items.length === 0 ? (
                <p className="text-sm text-muted">Qarorlar yo‘q.</p>
              ) : (
                <ul className="divide-y divide-border text-sm" data-testid="approval-log">
                  {log.data.items.map((a) => (
                    <li key={a.id} className="py-2">
                      <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
                        <span className="font-medium">{DECISION[a.decision]}</span>
                        <Link href={`/content/${a.content_id}`} className="underline">#{a.content_id} v{a.content_version}</Link>
                        <span className="min-w-0 truncate text-muted">{a.content_topic}</span>
                        {a.active && <span className="rounded-full bg-emerald-50 px-2 text-xs text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200">amalda</span>}
                        {a.invalidated_at && <span className="text-xs text-amber-700 dark:text-amber-300">bekor qilingan ({a.invalidation_reason})</span>}
                      </div>
                      <p className="mt-0.5 text-xs text-muted">
                        {a.decided_by_email ?? `#${a.decided_by_user_id}`} · {CHANNEL[a.channel] ?? a.channel} · {formatDateTime(a.created_at)}
                        {a.comment ? ` · “${a.comment}”` : ""}
                      </p>
                    </li>
                  ))}
                </ul>
              )}
            </Card>
          )}
        </>
      )}
    </>
  );
}
