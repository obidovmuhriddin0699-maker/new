"use client";

import Link from "next/link";

import { BackendStatus } from "@/components/BackendStatus";
import { Card, ErrorBox, Loading, LinkButton, PageHeader } from "@/components/ui";
import { formatDateTime, TYPE_LABEL } from "@/lib/format";
import type { AIStatus, ContentType, DashboardSummary, OpsStatus } from "@/lib/types";
import { useApi } from "@/lib/useApi";

function Stat({ label, value, href, testId, hint }: { label: string; value: number | string; href?: string; testId: string; hint?: string }) {
  const body = (
    <div className="h-full rounded-2xl border border-border bg-card p-4 shadow-sm transition hover:border-accent" data-testid={testId}>
      <p className="text-xs font-medium uppercase tracking-wide text-muted">{label}</p>
      <p className="mt-2 text-2xl font-semibold tabular-nums">{value}</p>
      {hint && <p className="mt-1 text-xs text-muted">{hint}</p>}
    </div>
  );
  return href ? <Link href={href}>{body}</Link> : body;
}

/** Problems from the ops monitor (owners/admins only; others get 403 and see nothing). */
function OpsBanner() {
  const { data } = useApi<OpsStatus>("system/ops-status");
  if (!data || data.ok) return null;
  const critical = data.problems.some((p) => p.severity === "critical");
  return (
    <div
      role="status"
      data-testid="ops-banner"
      className={`mb-4 rounded-2xl border p-4 text-sm ${critical ? "border-red-300 bg-red-50 text-red-900 dark:border-red-900 dark:bg-red-950 dark:text-red-100" : "border-amber-300 bg-amber-50 text-amber-900 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-100"}`}
    >
      <p className="font-semibold">Tizim ogohlantirishi</p>
      <ul className="mt-1 list-disc space-y-0.5 pl-5">
        {data.problems.map((p) => (
          <li key={p.key}>{p.message}</li>
        ))}
      </ul>
    </div>
  );
}

export default function OverviewPage() {
  const { data, error, loading, reload } = useApi<DashboardSummary>("dashboard/summary");
  const ai = useApi<AIStatus>("ai/status");

  return (
    <>
      <PageHeader
        title="Umumiy ko‘rinish"
        subtitle="AI kontent tayyorlaydi — nashr qilish faqat sizning tasdig‘ingizdan keyin."
        actions={<LinkButton href="/ai" variant="primary">AI bilan yaratish</LinkButton>}
      />
      <OpsBanner />
      {loading && !data && <Loading />}
      <ErrorBox error={error} onRetry={reload} />
      {data && (
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
          <Stat testId="stat-total" label="Jami kontent" value={data.total} href="/content" />
          <Stat testId="stat-pending" label="Tasdiq kutmoqda" value={data.pending_approval} href="/content?status=READY_FOR_REVIEW" />
          <Stat testId="stat-scheduled" label="Rejalashtirilgan" value={data.scheduled} href="/content?status=SCHEDULED" />
          <Stat testId="stat-published" label="Nashr qilingan" value={data.published} href="/content?status=PUBLISHED" />
          <Stat testId="stat-failed" label="Xato" value={data.failed} href="/content?status=FAILED" />
          <Stat testId="stat-drafts" label="Qoralama" value={data.drafts} href="/content?status=DRAFT" />
          <Stat
            testId="stat-reach"
            label="Qamrov (reach, 7 kun)"
            value={data.reach ?? "—"}
            hint={data.reach === null ? "Ma’lumot yo‘q: statistika hali sinxronlanmagan" : undefined}
          />
          <Stat
            testId="stat-engagement"
            label="Engagement"
            value={data.engagement_rate === null ? "—" : `${(data.engagement_rate * 100).toFixed(1)}%`}
            hint={data.engagement_rate === null ? "Ma’lumot yo‘q: statistika hali sinxronlanmagan" : undefined}
          />
        </div>
      )}

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Card title="Yaqin rejalar">
          {data?.upcoming.length ? (
            <ul className="divide-y divide-border text-sm">
              {data.upcoming.map((u) => (
                <li key={u.content_id} className="flex items-center justify-between gap-3 py-2">
                  <Link href={`/content/${u.content_id}`} className="min-w-0 truncate hover:underline">
                    {TYPE_LABEL[u.content_type as ContentType] ?? u.content_type} · {u.topic ?? `#${u.content_id}`}
                  </Link>
                  <span className="shrink-0 text-muted">{formatDateTime(u.scheduled_at)}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-muted">Rejalashtirilgan kontent yo‘q.</p>
          )}
          <p className="mt-3 text-xs text-muted">Rejalashtirilgan kontent belgilangan vaqtda avtomatik nashr qilinadi (META_DRY_RUN=true bo‘lsa — yo‘q).</p>
        </Card>

        <Card title="AI holati">
          {ai.data ? (
            <div className="space-y-1 text-sm" data-testid="ai-status">
              <p>
                <span className={`mr-2 inline-block h-2.5 w-2.5 rounded-full ${ai.data.text.available ? "bg-emerald-500" : "bg-red-500"}`} />
                {ai.data.text.provider} · {ai.data.text.model} — {ai.data.text.available ? "ishlayapti" : "ishlamayapti"}
              </p>
              {ai.data.text.message && <p className="text-muted">{ai.data.text.message}</p>}
              <p className="text-muted">Rasm/video: {ai.data.media.map((m) => `${m.kind}: ${m.status}`).join(", ")}</p>
            </div>
          ) : (
            <ErrorBox error={ai.error} />
          )}
        </Card>
      </div>

      <div className="mt-4">
        <BackendStatus />
      </div>
    </>
  );
}
