"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";

import { EmptyState, ErrorBox, LinkButton, Loading, PageHeader, StatusBadge, TypeBadge, inputClass } from "@/components/ui";
import { formatDateTime, STATUS_LABEL, truncate, TYPE_LABEL } from "@/lib/format";
import type { ContentList, ContentStatus, ContentType } from "@/lib/types";
import { useApi } from "@/lib/useApi";

const TABS: (ContentStatus | "ALL")[] = [
  "ALL", "READY_FOR_REVIEW", "DRAFT", "EDIT_REQUESTED", "APPROVED", "SCHEDULED", "PUBLISHED", "FAILED", "REJECTED",
];
const PAGE = 20;

function Queue() {
  const router = useRouter();
  const params = useSearchParams();
  const status = (params.get("status") ?? "ALL") as ContentStatus | "ALL";
  const type = params.get("type") ?? "";
  const offset = Number(params.get("offset") ?? 0);

  const query = new URLSearchParams({ limit: String(PAGE), offset: String(offset) });
  if (status !== "ALL") query.set("status", status);
  if (type) query.set("content_type", type);
  const { data, error, loading, reload } = useApi<ContentList>(`contents?${query}`);

  function go(next: Record<string, string>) {
    const p = new URLSearchParams(params.toString());
    for (const [k, v] of Object.entries(next)) {
      if (v) p.set(k, v);
      else p.delete(k);
    }
    if (!("offset" in next)) p.delete("offset");
    router.push(`/content?${p}`);
  }

  return (
    <>
      <PageHeader
        title="Kontent navbati"
        subtitle="Har bir kontentni ko‘rib chiqing: tasdiqlang, tahrirlang yoki rad eting."
        actions={
          <>
            <LinkButton href="/content/new">Qo‘lda yaratish</LinkButton>
            <LinkButton href="/ai" variant="primary">AI bilan yaratish</LinkButton>
          </>
        }
      />
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="-mx-4 overflow-x-auto px-4 sm:mx-0 sm:px-0" role="tablist" aria-label="Holat bo‘yicha filtr">
          <div className="flex w-max gap-1">
            {TABS.map((t) => (
              <button
                key={t}
                type="button"
                role="tab"
                aria-selected={status === t}
                onClick={() => go({ status: t === "ALL" ? "" : t })}
                className={`whitespace-nowrap rounded-full px-3 py-1.5 text-sm ${status === t ? "bg-accent text-accent-fg" : "border border-border bg-card"}`}
              >
                {t === "ALL" ? "Hammasi" : STATUS_LABEL[t]}
              </button>
            ))}
          </div>
        </div>
        <select aria-label="Turi" className={`${inputClass} sm:w-40`} value={type} onChange={(e) => go({ type: e.target.value })}>
          <option value="">Barcha turlar</option>
          {(Object.keys(TYPE_LABEL) as ContentType[]).map((t) => (
            <option key={t} value={t}>{TYPE_LABEL[t]}</option>
          ))}
        </select>
      </div>

      {loading && !data && <Loading />}
      <ErrorBox error={error} onRetry={reload} />
      {data && data.items.length === 0 && (
        <EmptyState title="Bu yerda hozircha kontent yo‘q">
          <Link href="/ai" className="underline">AI Studio</Link> orqali yangi kontent yarating.
        </EmptyState>
      )}
      {data && data.items.length > 0 && (
        <ul className="space-y-3" data-testid="content-list">
          {data.items.map((c) => (
            <li key={c.id}>
              <Link
                href={`/content/${c.id}`}
                className="block rounded-2xl border border-border bg-card p-4 shadow-sm transition hover:border-accent"
                data-testid="content-item"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <StatusBadge status={c.status} />
                  <TypeBadge type={c.content_type} />
                  <span className="text-xs text-muted">v{c.version}</span>
                  <span className="text-xs text-muted">· {c.created_by === "AGENT" ? "AI" : "Inson"}</span>
                  <span className="ml-auto text-xs text-muted">{formatDateTime(c.updated_at)}</span>
                </div>
                <p className="mt-2 font-medium">{c.topic ?? `Kontent #${c.id}`}</p>
                {c.caption && <p className="mt-1 text-sm text-muted">{truncate(c.caption, 160)}</p>}
              </Link>
            </li>
          ))}
        </ul>
      )}
      {data && data.total > PAGE && (
        <div className="mt-4 flex items-center justify-between text-sm">
          <button type="button" disabled={offset === 0} onClick={() => go({ offset: String(Math.max(0, offset - PAGE)) })} className="rounded-lg border border-border px-3 py-2 disabled:opacity-40">
            Oldingi
          </button>
          <span className="text-muted">
            {offset + 1}–{Math.min(offset + PAGE, data.total)} / {data.total}
          </span>
          <button type="button" disabled={offset + PAGE >= data.total} onClick={() => go({ offset: String(offset + PAGE) })} className="rounded-lg border border-border px-3 py-2 disabled:opacity-40">
            Keyingi
          </button>
        </div>
      )}
    </>
  );
}

export default function ContentPage() {
  return (
    <Suspense fallback={<Loading />}>
      <Queue />
    </Suspense>
  );
}
