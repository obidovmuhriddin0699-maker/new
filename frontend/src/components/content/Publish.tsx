"use client";

import { useRef, useState } from "react";

import { Button, Card, ErrorBox, Field, Notice, inputClass } from "@/components/ui";
import { api, uploadFile } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import type { Content, PublishPreview, PublishResponse } from "@/lib/types";

const PUBLISHABLE = ["APPROVED", "SCHEDULED", "FAILED"];
const STATE_LABEL: Record<string, string> = {
  PENDING: "Navbatda",
  PROCESSING: "Jarayonda",
  DONE: "Nashr qilingan",
  FAILED: "Muvaffaqiyatsiz",
  CANCELLED: "Bekor qilingan",
};

/** Publish to Instagram: preview (no Meta call), then an explicit, confirmed publish. */
export function PublishCard({ content, onChanged }: { content: Content; onChanged: () => Promise<void> }) {
  const [preview, setPreview] = useState<PublishPreview | null>(null);
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState<"preview" | "publish" | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [result, setResult] = useState<PublishResponse | null>(null);
  const state = content.publish_state;
  const canPublish = PUBLISHABLE.includes(content.status) && content.publish_authorized;

  async function loadPreview() {
    setBusy("preview");
    setError(null);
    try {
      setPreview(await api<PublishPreview>(`contents/${content.id}/publish-preview`));
    } catch (err) {
      setError(err);
    } finally {
      setBusy(null);
    }
  }

  async function publish() {
    setBusy("publish");
    setError(null);
    setResult(null);
    try {
      const r = await api<PublishResponse>(`contents/${content.id}/publish`, {
        method: "POST",
        body: { expected_version: content.version },
      });
      setResult(r);
      if (r.preview) setPreview(r.preview);
      setConfirming(false);
      await onChanged();
    } catch (err) {
      setError(err);
      await onChanged();
    } finally {
      setBusy(null);
    }
  }

  return (
    <Card title="Instagram’ga nashr">
      <div className="space-y-3 text-sm" data-testid="publish-card">
        {content.status === "PUBLISHED" ? (
          <Notice tone="success">
            Nashr qilingan: {formatDateTime(content.published_at)}
            {content.ig_permalink && (
              <>
                {" · "}
                <a href={content.ig_permalink} target="_blank" rel="noopener noreferrer" className="underline" data-testid="permalink">
                  Instagram’da ko‘rish
                </a>
              </>
            )}
          </Notice>
        ) : (
          <p className="text-muted">
            Faqat siz tasdiqlagan <b>v{content.version}</b> nashr qilinadi. AI nashr qila olmaydi.
          </p>
        )}

        {state && content.status !== "PUBLISHED" && (
          <div className="rounded-lg border border-border p-2 text-xs" data-testid="publish-state">
            <p>
              Holat: <b>{STATE_LABEL[state.status] ?? state.status}</b> · urinishlar: {state.attempts}
              {state.status === "PENDING" && ` · ${formatDateTime(state.scheduled_at)}`}
            </p>
            {state.outcome_unknown && <p className="text-amber-700 dark:text-amber-300">Meta javobi kelmadi — natija avtomatik tekshirilmoqda. Qayta bosmang.</p>}
            {state.last_error && <p className="text-red-700 dark:text-red-300">{state.last_error}</p>}
          </div>
        )}

        {result && (
          <Notice tone={result.status === "published" ? "success" : result.status === "dry_run" || result.status === "queued" ? "info" : "warning"}>
            <span data-testid="publish-result">{result.message}</span>
          </Notice>
        )}
        <ErrorBox error={error} />

        {content.status !== "PUBLISHED" && (
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => void loadPreview()} loading={busy === "preview"} data-testid="publish-preview">
              Nimalar yuborilishini ko‘rish
            </Button>
            {canPublish && !confirming && (
              <Button variant="primary" onClick={() => setConfirming(true)} data-testid="publish-start" disabled={busy !== null}>
                Instagram’ga nashr qilish
              </Button>
            )}
          </div>
        )}
        {!canPublish && content.status !== "PUBLISHED" && content.status !== "PUBLISHING" && (
          <p className="text-xs text-muted">Nashr uchun joriy versiya tasdiqlangan bo‘lishi kerak.</p>
        )}

        {confirming && (
          <div className="space-y-2 rounded-xl border border-border bg-background p-3" data-testid="publish-confirm">
            <p>
              <b>v{content.version}</b> hozir Instagram’ga joylanadi. Bu ommaviy amal; uni API orqali qaytarib bo‘lmaydi.
            </p>
            <div className="flex flex-wrap gap-2">
              <Button variant="success" loading={busy === "publish"} onClick={() => void publish()} data-testid="publish-confirm-button">
                Ha, nashr qilish
              </Button>
              <Button onClick={() => setConfirming(false)} disabled={busy !== null}>
                Bekor qilish
              </Button>
            </div>
          </div>
        )}

        {preview && <PreviewView preview={preview} />}
      </div>
    </Card>
  );
}

function PreviewView({ preview }: { preview: PublishPreview }) {
  return (
    <div className="space-y-2 rounded-xl border border-border p-3" data-testid="publish-plan">
      {preview.dry_run && (
        <Notice tone="warning">DRY RUN (META_DRY_RUN=true): bu faqat reja, Instagram’ga hech narsa yuborilmaydi.</Notice>
      )}
      {preview.problems.length > 0 && (
        <ul className="list-inside list-disc text-red-700 dark:text-red-300">
          {preview.problems.map((p) => (
            <li key={p}>{p}</li>
          ))}
        </ul>
      )}
      {preview.plan && (
        <>
          <p className="text-xs text-muted">
            Akkaunt: {preview.plan.account_username ? `@${preview.plan.account_username}` : "—"} · caption: {preview.plan.caption_length}/2200 belgi
          </p>
          {preview.plan.caption && (
            <pre className="max-h-40 overflow-auto whitespace-pre-wrap break-words rounded-lg bg-background p-2 text-xs" data-testid="publish-caption">
              {preview.plan.caption}
            </pre>
          )}
          <ol className="list-inside list-decimal space-y-1 text-xs">
            {preview.plan.steps.map((s, i) => (
              <li key={i} className="break-all">
                <code>{s.endpoint}</code>
                {s.note && <span className="text-muted"> — {s.note}</span>}
                {Object.keys(s.params).length > 0 && (
                  <span className="text-muted"> {Object.entries(s.params).filter(([k]) => k !== "caption").map(([k, v]) => `${k}=${v}`).join(", ")}</span>
                )}
              </li>
            ))}
          </ol>
        </>
      )}
    </div>
  );
}

/** Attach media: upload a JPEG/MP4/MOV or give a public HTTPS URL. Each change = new version. */
export function MediaManager({ content, onChanged }: { content: Content; onChanged: () => Promise<void> }) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [url, setUrl] = useState("");
  const [kind, setKind] = useState<"IMAGE" | "VIDEO">("IMAGE");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const editable = ["DRAFT", "EDIT_REQUESTED", "READY_FOR_REVIEW", "APPROVED", "SCHEDULED", "FAILED"].includes(content.status);

  async function run(fn: () => Promise<unknown>) {
    setBusy(true);
    setError(null);
    try {
      await fn();
      await onChanged();
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  }

  return (
    <Card title={`Media (${content.assets.length})`}>
      <div className="space-y-3 text-sm" data-testid="media-manager">
        {content.assets.length > 0 && (
          <ul className="grid grid-cols-3 gap-2">
            {content.assets.map((a) => (
              <li key={a.id} className="space-y-1" data-testid="asset">
                <div className="aspect-square overflow-hidden rounded-lg border border-border bg-background text-xs text-muted">
                  {a.public_url && a.kind === "IMAGE" ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={a.public_url} alt="" className="h-full w-full object-cover" />
                  ) : (
                    <span className="flex h-full items-center justify-center p-1 text-center">{a.kind}</span>
                  )}
                </div>
                <p className="truncate text-xs text-muted" title={a.public_url ?? ""}>
                  #{a.position + 1} · {a.mime_type ?? a.kind}
                </p>
                {editable && (
                  <button
                    type="button"
                    className="text-xs text-red-700 underline disabled:opacity-50 dark:text-red-300"
                    disabled={busy}
                    onClick={() => void run(() => api(`contents/${content.id}/assets/${a.id}?expected_version=${content.version}`, { method: "DELETE" }))}
                  >
                    O‘chirish
                  </button>
                )}
              </li>
            ))}
          </ul>
        )}
        {editable ? (
          <>
            <Field label="Fayl yuklash" hint="JPEG rasm yoki MP4/MOV video. Media o‘zgarsa, kontent qayta tasdiqlanishi kerak.">
              <input
                ref={fileRef}
                type="file"
                accept="image/jpeg,video/mp4,video/quicktime"
                className="block w-full text-sm"
                disabled={busy}
                data-testid="media-file"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) void run(() => uploadFile(`contents/${content.id}/assets/upload?expected_version=${content.version}`, file));
                }}
              />
            </Field>
            <form
              className="flex flex-wrap items-end gap-2"
              onSubmit={(e) => {
                e.preventDefault();
                void run(async () => {
                  await api(`contents/${content.id}/assets`, {
                    method: "POST",
                    body: { expected_version: content.version, kind, public_url: url },
                  });
                  setUrl("");
                });
              }}
            >
              <label className="min-w-0 flex-1 text-sm">
                <span className="mb-1 block font-medium">Yoki ochiq HTTPS havola</span>
                <input className={inputClass} type="url" pattern="https://.*" placeholder="https://..." value={url} onChange={(e) => setUrl(e.target.value)} required />
              </label>
              <select aria-label="Media turi" className="rounded-lg border border-border bg-card px-2 py-2 text-sm" value={kind} onChange={(e) => setKind(e.target.value as "IMAGE" | "VIDEO")}>
                <option value="IMAGE">Rasm</option>
                <option value="VIDEO">Video</option>
              </select>
              <Button type="submit" loading={busy}>
                Qo‘shish
              </Button>
            </form>
          </>
        ) : (
          <p className="text-xs text-muted">Bu holatda media o‘zgartirilmaydi.</p>
        )}
        <ErrorBox error={error} />
      </div>
    </Card>
  );
}
