"use client";

import { useState } from "react";

import { Card, ErrorBox, Loading } from "@/components/ui";
import type { ContentVersion, Readiness, VersionDiff } from "@/lib/types";
import { useApi } from "@/lib/useApi";

const FIELD_LABEL: Record<string, string> = {
  topic: "Mavzu",
  hook: "Hook",
  caption: "Caption",
  cta: "CTA",
  script: "Ssenariy",
  visual_prompt: "Vizual prompt",
  content_type: "Turi",
  language: "Til",
  aspect_ratio: "Format",
  hashtags: "Hashtaglar",
  structure: "Slaydlar / sahnalar",
  media: "Media",
};

export function ReadinessCard({ contentId, version }: { contentId: number; version: number }) {
  const { data, error, loading } = useApi<Readiness>(`contents/${contentId}/readiness?v=${version}`);
  return (
    <Card title="Nashrga tayyorlik">
      {loading && !data && <Loading />}
      <ErrorBox error={error} />
      {data && (
        <div className="space-y-2 text-sm" data-testid="readiness">
          <p className={data.ready ? "font-medium text-emerald-700 dark:text-emerald-300" : "font-medium text-amber-700 dark:text-amber-300"}>
            {data.ready ? "Nashrga tayyor" : "Hali nashrga tayyor emas"}
          </p>
          <ul className="space-y-1.5">
            {data.checks.map((c) => (
              <li key={c.key} className="flex gap-2" data-testid={`readiness-${c.key}`} data-ok={c.ok}>
                <span aria-hidden className={c.ok ? "text-emerald-600" : c.severity === "blocker" ? "text-red-600" : "text-muted"}>
                  {c.ok ? "✓" : c.severity === "blocker" ? "✗" : "•"}
                </span>
                <span className={c.ok ? "" : c.severity === "blocker" ? "" : "text-muted"}>{c.message}</span>
              </li>
            ))}
          </ul>
          <p className="text-xs text-muted">{data.note}</p>
        </div>
      )}
    </Card>
  );
}

export function DiffCard({ contentId, version, versions }: { contentId: number; version: number; versions: ContentVersion[] }) {
  const [from, setFrom] = useState<number | "">("");
  const path = version > 1 ? `contents/${contentId}/diff${from ? `?from_version=${from}` : ""}${from ? "&" : "?"}v=${version}` : null;
  const { data, error, loading } = useApi<VersionDiff>(path);
  if (version <= 1) return null;
  const changed = data?.fields.filter((f) => f.changed) ?? [];
  return (
    <Card
      title="O‘zgarishlar"
      actions={
        <select
          aria-label="Qaysi versiya bilan solishtirish"
          className="rounded-lg border border-border bg-card px-2 py-1 text-sm"
          value={from}
          onChange={(e) => setFrom(e.target.value ? Number(e.target.value) : "")}
        >
          <option value="">Avtomatik</option>
          {versions.filter((v) => v.version < version).map((v) => (
            <option key={v.version} value={v.version}>v{v.version}</option>
          ))}
        </select>
      }
    >
      {loading && !data && <Loading />}
      <ErrorBox error={error} />
      {data && (
        <div className="space-y-4 text-sm" data-testid="diff">
          <p className="text-muted">
            v{data.from_version} ({data.from_label}) → v{data.to_version}: {changed.length ? `${changed.length} ta maydon o‘zgargan` : "o‘zgarish yo‘q"}
          </p>
          {changed.map((f) => (
            <div key={f.field}>
              <p className="mb-1 font-medium">{FIELD_LABEL[f.field] ?? f.field}</p>
              {f.lines.length ? (
                <pre className="overflow-x-auto whitespace-pre-wrap break-words rounded-lg border border-border p-2 text-xs leading-relaxed">
                  {f.lines.map((l, i) => (
                    <span
                      key={i}
                      className={`block ${l.op === "add" ? "bg-emerald-50 text-emerald-900 dark:bg-emerald-950 dark:text-emerald-100" : l.op === "remove" ? "bg-red-50 text-red-900 line-through dark:bg-red-950 dark:text-red-100" : "text-muted"}`}
                    >
                      {l.op === "add" ? "+ " : l.op === "remove" ? "− " : "  "}
                      {l.text}
                    </span>
                  ))}
                </pre>
              ) : (
                <p>
                  <span className="text-red-700 line-through dark:text-red-300">{String(f.old ?? "—")}</span> →{" "}
                  <span className="text-emerald-700 dark:text-emerald-300">{String(f.new ?? "—")}</span>
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
