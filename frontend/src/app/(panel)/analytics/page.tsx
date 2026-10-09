"use client";

import Link from "next/link";
import { useState } from "react";

import { Button, Card, EmptyState, ErrorBox, Loading, Notice, PageHeader } from "@/components/ui";
import { ApiError, api } from "@/lib/api";
import { TYPE_LABEL, formatDate, formatDateTime } from "@/lib/format";
import type { AnalyticsOverview, AnalyticsPoint, AnalyticsReport, AnalyticsWindow } from "@/lib/types";
import { useApi } from "@/lib/useApi";

const PERIOD_LABEL: Record<AnalyticsWindow["period"], string> = { day: "1 kun", week: "7 kun", days_28: "28 kun" };
const ACCOUNT_METRICS: [string, string][] = [
  ["reach", "Qamrov (reach)"],
  ["views", "Ko‘rishlar (views)"],
  ["accounts_engaged", "Faol akkauntlar"],
  ["total_interactions", "Interaksiyalar"],
];
const MEDIA_METRICS: [string, string][] = [
  ["reach", "Reach"],
  ["views", "Views"],
  ["likes", "Like"],
  ["comments", "Izoh"],
  ["shares", "Ulashish"],
  ["saved", "Saqlash"],
  ["total_interactions", "Jami"],
];

function num(v: number | undefined): string {
  return v === undefined ? "—" : new Intl.NumberFormat("uz-UZ").format(v);
}

function Missing() {
  return (
    <span className="text-muted" title="Meta API bu ko‘rsatkichni qaytarmadi — taxmin qilinmaydi">
      —
    </span>
  );
}

export default function AnalyticsPage() {
  const overview = useApi<AnalyticsOverview>("analytics/overview");
  const history = useApi<AnalyticsPoint[]>("analytics/history?days=30");
  const reports = useApi<AnalyticsReport[]>("analytics/reports");
  const [period, setPeriod] = useState<AnalyticsWindow["period"]>("week");
  const [busy, setBusy] = useState<"sync" | "report" | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [selected, setSelected] = useState<number | null>(null);

  async function sync() {
    setBusy("sync");
    setError(null);
    setMessage(null);
    try {
      const r = await api<{ status: string; reason: string | null; media_synced: number }[]>("analytics/sync", { method: "POST" });
      if (!r.length) setMessage("Ulangan Instagram akkaunt yo‘q.");
      else setMessage(r.map((x) => (x.status === "ok" ? `Yangilandi: ${x.media_synced} ta kontent.` : x.reason ?? x.status)).join(" "));
      await Promise.all([overview.reload(), history.reload()]);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(null);
    }
  }

  async function createReport() {
    setBusy("report");
    setError(null);
    setMessage(null);
    try {
      const r = await api<AnalyticsReport | { queued: true }>("analytics/reports", { method: "POST", body: {} });
      if ("queued" in r) setMessage("Hisobot navbatga qo‘yildi (Celery). Birozdan keyin sahifani yangilang.");
      else setSelected(r.id);
      await reports.reload();
    } catch (err) {
      setError(err);
    } finally {
      setBusy(null);
    }
  }

  const o = overview.data;
  const win = o?.windows.find((w) => w.period === period);
  const report = reports.data?.find((r) => r.id === selected) ?? reports.data?.[0] ?? null;

  return (
    <>
      <PageHeader
        title="Analitika"
        subtitle="Faqat Meta API qaytargan haqiqiy ko‘rsatkichlar. Qaytmagani “—” bo‘lib qoladi."
        actions={
          <Button onClick={() => void sync()} loading={busy === "sync"} data-testid="analytics-sync">
            Statistikani yangilash
          </Button>
        }
      />
      {message && <div className="mb-4"><Notice tone="info"><span data-testid="analytics-message">{message}</span></Notice></div>}
      <ErrorBox error={error ?? overview.error} />
      {overview.loading && !o && <Loading />}

      {o && (
        <div className="space-y-4">
          <Card
            title={o.username ? `@${o.username}` : "Akkaunt"}
            actions={
              <div className="flex gap-1" role="tablist" aria-label="Davr">
                {(["day", "week", "days_28"] as const).map((p) => (
                  <button
                    key={p}
                    type="button"
                    role="tab"
                    aria-selected={period === p}
                    onClick={() => setPeriod(p)}
                    className={`rounded-md px-2 py-1 text-xs ${period === p ? "bg-accent text-accent-fg" : "border border-border"}`}
                  >
                    {PERIOD_LABEL[p]}
                  </button>
                ))}
              </div>
            }
          >
            {!o.account_id ? (
              <EmptyState title="Instagram akkaunt ulanmagan">
                <Link href="/instagram" className="underline">Instagram sahifasida</Link> ulang.
              </EmptyState>
            ) : !win ? (
              <p className="text-sm text-muted" data-testid="no-account-stats">
                Bu davr uchun statistika hali sinxronlanmagan. “Statistikani yangilash” tugmasini bosing.
              </p>
            ) : (
              <div className="space-y-3" data-testid="account-stats">
                <dl className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                  {ACCOUNT_METRICS.map(([key, label]) => (
                    <div key={key} className="rounded-xl border border-border p-3">
                      <dt className="text-xs text-muted">{label}</dt>
                      <dd className="text-xl font-semibold" data-testid={`metric-${key}`}>
                        {key in win.metrics ? num(win.metrics[key]) : <Missing />}
                      </dd>
                    </div>
                  ))}
                </dl>
                <p className="text-xs text-muted">
                  {formatDate(win.window_start)} – {formatDate(win.window_end)} · obunachilar: {o.followers_count ?? "—"}
                  {win.unavailable.length > 0 && <> · Meta qaytarmagan: {win.unavailable.join(", ")}</>}
                </p>
              </div>
            )}
            <p className="mt-3 text-xs text-muted">
              Oxirgi sinxronlash:{" "}
              {o.last_sync ? `${formatDateTime(o.last_sync.at)} — ${o.last_sync.status}${o.last_sync.message ? ` (${o.last_sync.message})` : ""}` : "hali bo‘lmagan"}
            </p>
          </Card>

          <ReportCard
            report={report}
            reports={reports.data ?? []}
            onSelect={setSelected}
            onCreate={() => void createReport()}
            busy={busy === "report"}
            error={reports.error}
          />

          <Card title="Kontent natijalari">
            {o.content.length === 0 ? (
              <EmptyState title="Hali nashr qilingan kontent yo‘q" />
            ) : (
              <div className="overflow-x-auto" data-testid="content-stats">
                <table className="w-full min-w-[44rem] text-sm">
                  <thead className="text-left text-xs text-muted">
                    <tr>
                      <th className="py-2 pr-2">Kontent</th>
                      {MEDIA_METRICS.map(([k, l]) => <th key={k} className="px-2 text-right">{l}</th>)}
                      <th className="px-2 text-right" title={o.engagement_rate_definition}>Engagement</th>
                    </tr>
                  </thead>
                  <tbody>
                    {o.content.map((c) => (
                      <tr key={c.content_id} className="border-t border-border">
                        <td className="py-2 pr-2">
                          <Link href={`/content/${c.content_id}`} className="underline">{c.topic ?? `#${c.content_id}`}</Link>
                          <span className="block text-xs text-muted">
                            {TYPE_LABEL[c.content_type]} · {formatDate(c.published_at)}
                            {c.permalink && <> · <a href={c.permalink} target="_blank" rel="noopener noreferrer" className="underline">Instagram</a></>}
                            {!c.last_synced_at && " · statistika hali yo‘q"}
                          </span>
                        </td>
                        {MEDIA_METRICS.map(([k]) => (
                          <td key={k} className="px-2 text-right tabular-nums">{k in c.metrics ? num(c.metrics[k]) : <Missing />}</td>
                        ))}
                        <td className="px-2 text-right tabular-nums">{c.engagement_rate === null ? <Missing /> : `${(c.engagement_rate * 100).toFixed(2)}%`}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <p className="mt-2 text-xs text-muted">
                  Engagement = {o.engagement_rate_definition}. Bu Instagram’ning rasmiy ko‘rsatkichi emas, ikkala qiymat Meta’dan kelgandagina hisoblanadi.
                </p>
              </div>
            )}
          </Card>

          <Card title="Kunlik qamrov (oxirgi 30 kun)">
            {!history.data?.length ? (
              <p className="text-sm text-muted">Kunlik ma’lumot hali yo‘q.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm" data-testid="history">
                  <thead className="text-left text-xs text-muted">
                    <tr><th className="py-1">Sana</th><th className="text-right">Reach</th><th className="text-right">Views</th><th className="text-right">Obunachilar</th></tr>
                  </thead>
                  <tbody>
                    {[...history.data].reverse().map((p) => (
                      <tr key={p.date} className="border-t border-border">
                        <td className="py-1">{formatDate(p.date)}</td>
                        <td className="text-right tabular-nums">{"reach" in p.metrics ? num(p.metrics.reach) : <Missing />}</td>
                        <td className="text-right tabular-nums">{"views" in p.metrics ? num(p.metrics.views) : <Missing />}</td>
                        <td className="text-right tabular-nums">{"followers_count" in p.metrics ? num(p.metrics.followers_count) : <Missing />}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </div>
      )}
    </>
  );
}

function ReportCard({
  report,
  reports,
  onSelect,
  onCreate,
  busy,
  error,
}: {
  report: AnalyticsReport | null;
  reports: AnalyticsReport[];
  onSelect: (id: number) => void;
  onCreate: () => void;
  busy: boolean;
  error: unknown;
}) {
  return (
    <Card
      title="AI Analyst — haftalik hisobot"
      actions={
        <div className="flex flex-wrap items-center gap-2">
          {reports.length > 1 && (
            <select
              aria-label="Hisobotni tanlash"
              className="rounded-lg border border-border bg-card px-2 py-1 text-sm"
              value={report?.id}
              onChange={(e) => onSelect(Number(e.target.value))}
            >
              {reports.map((r) => (
                <option key={r.id} value={r.id}>{r.period_start} – {r.period_end}</option>
              ))}
            </select>
          )}
          <Button onClick={onCreate} loading={busy} data-testid="create-report">Hisobot yaratish</Button>
        </div>
      }
    >
      <ErrorBox error={error instanceof ApiError ? error : null} />
      {!report ? (
        <p className="text-sm text-muted">Hali hisobot yo‘q. Har dushanba avtomatik yaratiladi yoki tugmani bosing.</p>
      ) : (
        <div className="space-y-3 text-sm" data-testid="report">
          <p className="text-xs text-muted">
            {report.period_start} – {report.period_end} · {report.source === "ai" ? `AI (${report.model ?? report.provider})` : "qoidalar asosida"} · {formatDateTime(report.created_at)}
          </p>
          <p className="whitespace-pre-line" data-testid="report-summary">{report.summary}</p>
          {report.highlights.length > 0 && (
            <ul className="space-y-1">
              {report.highlights.map((h) => (
                <li key={h.content_id}>
                  <Link href={`/content/${h.content_id}`} className="underline">#{h.content_id}</Link> — {h.reason}
                </li>
              ))}
            </ul>
          )}
          {report.recommendations.length > 0 && (
            <div>
              <p className="font-medium">Keyingi hafta uchun tavsiyalar</p>
              <ul className="list-inside list-disc" data-testid="report-recommendations">
                {report.recommendations.map((r) => <li key={r}>{r}</li>)}
              </ul>
            </div>
          )}
          {report.ai_rejected_reason && (
            <p className="text-xs text-amber-700 dark:text-amber-300">
              AI matni ishlatilmadi ({report.ai_rejected_reason}) — hisobot faqat hisoblangan faktlar asosida.
            </p>
          )}
          <p className="text-xs text-muted">Tavsiyalar AI Strategist’ga keyingi strategiya uchun beriladi. Hech narsa avtomatik nashr qilinmaydi.</p>
        </div>
      )}
    </Card>
  );
}
