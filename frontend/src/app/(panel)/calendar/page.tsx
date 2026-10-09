"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { Button, Card, ErrorBox, LinkButton, Loading, PageHeader, StatusBadge, TypeBadge } from "@/components/ui";
import { formatDate, formatDateTime, isoDate, STATUS_STYLE, TYPE_LABEL } from "@/lib/format";
import type { CalendarItem } from "@/lib/types";
import { useApi } from "@/lib/useApi";

type View = "day" | "week" | "month";
const WEEKDAYS = ["Du", "Se", "Ch", "Pa", "Ju", "Sh", "Ya"];
const MONTHS = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun", "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"];
const KIND_LABEL = { scheduled: "Rejalashtirilgan", published: "Nashr qilingan", planned: "Reja" };

function startOfWeek(d: Date): Date {
  const r = new Date(d);
  r.setHours(0, 0, 0, 0);
  r.setDate(r.getDate() - ((r.getDay() + 6) % 7));
  return r;
}
function addDays(d: Date, n: number): Date {
  const r = new Date(d);
  r.setDate(r.getDate() + n);
  return r;
}

function range(view: View, cursor: Date): { start: Date; end: Date } {
  if (view === "day") return { start: cursor, end: cursor };
  if (view === "week") {
    const s = startOfWeek(cursor);
    return { start: s, end: addDays(s, 6) };
  }
  const first = new Date(cursor.getFullYear(), cursor.getMonth(), 1);
  const s = startOfWeek(first);
  const last = new Date(cursor.getFullYear(), cursor.getMonth() + 1, 0);
  return { start: s, end: addDays(startOfWeek(last), 6) };
}

function today0(): Date {
  const d = new Date();
  d.setHours(0, 0, 0, 0);
  return d;
}

export default function CalendarPage() {
  // "Today" is only known in the browser: render after mount to avoid a
  // server/client hydration mismatch (the page is statically prerendered).
  const [cursor, setCursor] = useState<Date | null>(null);
  useEffect(() => setCursor(today0()), []);
  if (!cursor) return <Loading />;
  return <Calendar cursor={cursor} setCursor={setCursor} />;
}

function Calendar({ cursor, setCursor }: { cursor: Date; setCursor: (d: Date) => void }) {
  const [view, setView] = useState<View>("month");
  const [selected, setSelected] = useState<CalendarItem | null>(null);
  const { start, end } = range(view, cursor);
  const { data, error, loading, reload } = useApi<{ items: CalendarItem[] }>(`calendar?start=${isoDate(start)}&end=${isoDate(end)}`);

  const byDay = useMemo(() => {
    const m = new Map<string, CalendarItem[]>();
    for (const it of data?.items ?? []) m.set(it.date, [...(m.get(it.date) ?? []), it]);
    return m;
  }, [data]);

  function move(dir: -1 | 1) {
    const d = new Date(cursor);
    if (view === "day") d.setDate(d.getDate() + dir);
    else if (view === "week") d.setDate(d.getDate() + 7 * dir);
    else d.setMonth(d.getMonth() + dir, 1);
    setCursor(d);
  }

  const title =
    view === "month"
      ? `${MONTHS[cursor.getMonth()]} ${cursor.getFullYear()}`
      : view === "week"
        ? `${formatDate(isoDate(start))} – ${formatDate(isoDate(end))}`
        : formatDate(isoDate(cursor));
  const days = Array.from({ length: Math.round((end.getTime() - start.getTime()) / 86400000) + 1 }, (_, i) => addDays(start, i));
  const today = isoDate(new Date());

  return (
    <>
      <PageHeader title="Kalendar" subtitle="Rejalashtirilgan, nashr qilingan va rejadagi kontent." />
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <div className="flex rounded-lg border border-border bg-card p-0.5" role="tablist" aria-label="Ko‘rinish">
          {(["day", "week", "month"] as View[]).map((v) => (
            <button key={v} type="button" role="tab" aria-selected={view === v} onClick={() => setView(v)} className={`rounded-md px-3 py-1.5 text-sm ${view === v ? "bg-accent text-accent-fg" : ""}`}>
              {v === "day" ? "Kun" : v === "week" ? "Hafta" : "Oy"}
            </button>
          ))}
        </div>
        <Button onClick={() => move(-1)} aria-label="Oldingi">←</Button>
        <Button onClick={() => setCursor(today0())}>
          Bugun
        </Button>
        <Button onClick={() => move(1)} aria-label="Keyingi">→</Button>
        <h2 className="ml-1 text-base font-semibold" data-testid="calendar-title">{title}</h2>
      </div>
      <ErrorBox error={error} onRetry={reload} />
      {loading && !data && <Loading />}

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_20rem]">
        <div className="min-w-0">
          {view === "month" ? (
            <div className="overflow-hidden rounded-2xl border border-border bg-card" data-testid="calendar-month">
              <div className="grid grid-cols-7 border-b border-border text-center text-xs text-muted">
                {WEEKDAYS.map((w) => <div key={w} className="py-2">{w}</div>)}
              </div>
              <div className="grid grid-cols-7">
                {days.map((d) => {
                  const key = isoDate(d);
                  const items = byDay.get(key) ?? [];
                  const other = d.getMonth() !== cursor.getMonth();
                  return (
                    <button
                      key={key}
                      type="button"
                      onClick={() => {
                        setCursor(d);
                        if (items.length) setSelected(items[0]);
                      }}
                      className={`min-h-16 min-w-0 border-b border-r border-border p-1 text-left align-top sm:min-h-24 sm:p-1.5 ${other ? "opacity-40" : ""}`}
                    >
                      <span className={`text-xs ${key === today ? "rounded-full bg-accent px-1.5 text-accent-fg" : "text-muted"}`}>{d.getDate()}</span>
                      <span className="mt-1 hidden flex-col gap-0.5 sm:flex">
                        {items.slice(0, 3).map((it) => (
                          <span key={`${it.kind}-${it.content_id}`} className={`truncate rounded px-1 py-0.5 text-[11px] ring-1 ring-inset ${STATUS_STYLE[it.status]}`}>
                            {TYPE_LABEL[it.content_type]} · {it.topic ?? `#${it.content_id}`}
                          </span>
                        ))}
                        {items.length > 3 && <span className="text-[11px] text-muted">+{items.length - 3}</span>}
                      </span>
                      {items.length > 0 && <span className="mt-1 block h-1.5 w-1.5 rounded-full bg-accent sm:hidden" aria-label={`${items.length} ta`} />}
                    </button>
                  );
                })}
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              {days.map((d) => {
                const key = isoDate(d);
                const items = byDay.get(key) ?? [];
                return (
                  <Card key={key} title={`${WEEKDAYS[(d.getDay() + 6) % 7]}, ${formatDate(key)}`}>
                    {items.length === 0 ? (
                      <p className="text-sm text-muted">Kontent yo‘q</p>
                    ) : (
                      <ul className="space-y-2">
                        {items.map((it) => (
                          <li key={`${it.kind}-${it.content_id}`}>
                            <button type="button" onClick={() => setSelected(it)} className="flex w-full flex-wrap items-center gap-2 rounded-lg border border-border p-2 text-left text-sm hover:border-accent" data-testid="calendar-item">
                              <StatusBadge status={it.status} />
                              <TypeBadge type={it.content_type} />
                              <span className="min-w-0 flex-1 truncate">{it.topic ?? `Kontent #${it.content_id}`}</span>
                              <span className="text-xs text-muted">{it.at ? formatDateTime(it.at) : KIND_LABEL[it.kind]}</span>
                            </button>
                          </li>
                        ))}
                      </ul>
                    )}
                  </Card>
                );
              })}
            </div>
          )}
          {view === "month" && (
            <div className="mt-3 sm:hidden">
              <Card title={formatDate(isoDate(cursor))}>
                {(byDay.get(isoDate(cursor)) ?? []).map((it) => (
                  <button key={`${it.kind}-${it.content_id}`} type="button" onClick={() => setSelected(it)} className="mb-2 flex w-full items-center gap-2 text-left text-sm">
                    <StatusBadge status={it.status} /> <span className="truncate">{it.topic ?? `#${it.content_id}`}</span>
                  </button>
                ))}
                {!(byDay.get(isoDate(cursor)) ?? []).length && <p className="text-sm text-muted">Bu kunda kontent yo‘q.</p>}
              </Card>
            </div>
          )}
        </div>

        <div className="min-w-0">
          <Card title="Tanlangan kontent">
            {selected ? (
              <div className="space-y-3 text-sm" data-testid="calendar-selected">
                <div className="flex flex-wrap items-center gap-2">
                  <StatusBadge status={selected.status} />
                  <TypeBadge type={selected.content_type} />
                  <span className="text-muted">v{selected.version}</span>
                </div>
                <p className="font-medium">{selected.topic ?? `Kontent #${selected.content_id}`}</p>
                <p className="text-muted">{KIND_LABEL[selected.kind]} · {selected.at ? formatDateTime(selected.at) : formatDate(selected.date)}</p>
                <div className="grid grid-cols-2 gap-2">
                  <LinkButton href={`/content/${selected.content_id}`}>Ko‘rish</LinkButton>
                  <LinkButton href={`/content/${selected.content_id}?action=edit`}>Tahrirlash</LinkButton>
                  <LinkButton href={`/content/${selected.content_id}?action=regenerate`}>Qayta yaratish</LinkButton>
                  <LinkButton href={`/content/${selected.content_id}?action=approve`}>Tasdiqlash</LinkButton>
                  <LinkButton href={`/content/${selected.content_id}?action=schedule`}>Rejalashtirish</LinkButton>
                  <LinkButton href={`/content/${selected.content_id}?action=delete`} variant="danger">O‘chirish</LinkButton>
                </div>
                <p className="text-xs text-muted">Amallar faqat kontent holati ruxsat bergandagina mavjud bo‘ladi.</p>
              </div>
            ) : (
              <p className="text-sm text-muted">Kalendardan kontentni tanlang.</p>
            )}
          </Card>
          <p className="mt-3 text-xs text-muted">
            <Link href="/ai" className="underline">AI Studio → Kontent reja</Link> orqali haftalik rejani qoralamalar bilan yarating.
          </p>
        </div>
      </div>
    </>
  );
}
