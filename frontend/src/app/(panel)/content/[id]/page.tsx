"use client";

import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

import { EditForm } from "@/components/content/EditForm";
import { CaptionView, MediaBox, StructureView } from "@/components/content/Preview";
import { QualityView } from "@/components/content/Quality";
import { MediaManager, PublishCard, publishInFlight } from "@/components/content/Publish";
import { DiffCard, ReadinessCard } from "@/components/content/Review";
import { Button, Card, ErrorBox, Field, KeyValue, Loading, Notice, StatusBadge, TypeBadge, inputClass } from "@/components/ui";
import { api } from "@/lib/api";
import { runGeneration } from "@/lib/ai";
import { formatDate, formatDateTime, STATUS_LABEL, tashkentInputValue, tashkentToIso } from "@/lib/format";
import type { Content, ContentHistory, ContentStatus, QualityReport } from "@/lib/types";
import { useApi } from "@/lib/useApi";
import { useMe } from "@/lib/useMe";

type Action = "approve" | "reject" | "request-edit" | "submit" | "regenerate" | "schedule" | "unschedule" | "revoke" | "delete";

const ALLOWED: Record<ContentStatus, Action[]> = {
  DRAFT: ["submit", "regenerate", "delete"],
  GENERATING: [],
  READY_FOR_REVIEW: ["approve", "request-edit", "reject", "regenerate", "delete"],
  EDIT_REQUESTED: ["submit", "regenerate", "delete"],
  APPROVED: ["schedule", "revoke", "request-edit", "delete"],
  SCHEDULED: ["unschedule", "revoke", "request-edit", "delete"],
  PUBLISHING: [],
  PUBLISHED: [],
  FAILED: ["regenerate", "delete"],
  REJECTED: ["delete"],
};
const EDITABLE: ContentStatus[] = ["DRAFT", "EDIT_REQUESTED", "READY_FOR_REVIEW", "APPROVED", "SCHEDULED", "FAILED"];

const ACTION_LABEL: Record<Action, string> = {
  approve: "Tasdiqlash",
  reject: "Rad etish",
  "request-edit": "Tahrir so‘rash",
  submit: "Ko‘rib chiqishga yuborish",
  regenerate: "Qayta yaratish (AI)",
  schedule: "Rejalashtirish",
  unschedule: "Rejani bekor qilish",
  revoke: "Tasdiqni bekor qilish",
  delete: "O‘chirish",
};

/** Tomorrow, same hour, :00 — as Tashkent wall-clock time (whatever the browser's zone). */
function defaultScheduleValue(): string {
  const d = new Date(Date.now() + 24 * 3600 * 1000);
  d.setUTCMinutes(0, 0, 0); // UTC+5 has whole hours, so this is :00 in Tashkent too
  return tashkentInputValue(d);
}

function Detail() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const search = useSearchParams();
  const content = useApi<Content>(`contents/${id}`);
  const history = useApi<ContentHistory>(`contents/${id}/history`);
  const [editing, setEditing] = useState(false);
  const [pending, setPending] = useState<Action | null>(null);
  const [comment, setComment] = useState("");
  const [when, setWhen] = useState(defaultScheduleValue);
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState<unknown>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [warning, setWarning] = useState<string | null>(null);
  const [quality, setQuality] = useState<QualityReport | null>(null);
  const [aiRework, setAiRework] = useState(true);
  const [checking, setChecking] = useState(false);

  const { me, readOnly } = useMe();

  const c = content.data;
  // VIEWER: read-only (the backend refuses these anyway). While a publish is running,
  // scheduling is hidden too — the worker owns the content until it settles.
  const allowed = c && !readOnly ? ALLOWED[c.status].filter((a) => !(a === "schedule" && publishInFlight(c))) : [];
  const canEdit = Boolean(c && !readOnly && EDITABLE.includes(c.status));

  // Calendar deep links: /content/12?action=approve, ?action=edit — only when the
  // current status (and role) allows it. Waits for auth/me so a VIEWER gets nothing.
  useEffect(() => {
    const a = search.get("action");
    if (!c || !me || !a) return;
    if (a === "edit") {
      if (canEdit) setEditing(true);
    } else if (allowed.includes(a as Action)) {
      setPending(a as Action);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [c?.id, me]);

  async function refresh() {
    await Promise.all([content.reload(), history.reload()]);
  }

  async function confirm(action: Action) {
    if (!c) return;
    setBusy(true);
    setActionError(null);
    setMessage(null);
    setWarning(null);
    const body = { expected_version: c.version, comment: comment || null };
    try {
      if (action === "approve") {
        await api(`contents/${c.id}/approve`, { method: "POST", body });
        setMessage(`${c.version}-versiya tasdiqlandi. Tasdiqlash nashr qilmaydi — nashr uchun “Instagram’ga nashr” bo‘limidan foydalaning.`);
      } else if (action === "reject") {
        await api(`contents/${c.id}/reject`, { method: "POST", body });
      } else if (action === "request-edit") {
        await api(`contents/${c.id}/request-edit`, { method: "POST", body });
        if (aiRework) {
          // Edit -> AI rework -> back to the review queue (never auto-approved).
          try {
            const r = await runGeneration("ai/regenerate", { content_id: c.id, expected_version: c.version, instructions: comment || null });
            if (r.quality) setQuality(r.quality);
            setMessage("AI izohingiz asosida yangi versiya yaratdi va u ko‘rib chiqishga qaytdi.");
          } catch (err) {
            // The edit request itself is saved: close the panel and show the real state.
            setPending(null);
            setComment("");
            setActionError(err);
            setWarning("Tahrir so‘rovi saqlandi, lekin AI qayta ishlash bosqichi bajarilmadi. Kontentni qo‘lda tahrirlang yoki “Qayta yaratish (AI)” ni keyinroq bosing.");
            await refresh();
            return;
          }
        }
      } else if (action === "revoke") {
        await api(`contents/${c.id}/revoke-approval`, { method: "POST", body });
        setMessage("Tasdiq bekor qilindi. Kontent qayta ko‘rib chiqishda.");
      } else if (action === "submit") {
        await api(`contents/${c.id}/submit-review`, { method: "POST" });
      } else if (action === "schedule") {
        // The input is Tashkent wall-clock time, independent of the browser's time zone.
        await api(`contents/${c.id}/schedule`, { method: "POST", body: { scheduled_at: tashkentToIso(when) } });
        setMessage("Rejalashtirildi. Belgilangan vaqtda avtomatik nashr qilinadi (META_DRY_RUN=true bo‘lsa, yuborilmaydi).");
      } else if (action === "unschedule") {
        await api(`contents/${c.id}/schedule`, { method: "DELETE" });
      } else if (action === "delete") {
        await api(`contents/${c.id}`, { method: "DELETE" });
        router.push("/content");
        return;
      } else if (action === "regenerate") {
        const r = await runGeneration("ai/regenerate", { content_id: c.id, expected_version: c.version, instructions: comment || null });
        if (r.quality) setQuality(r.quality);
        setMessage("AI yangi versiya yaratdi. U qayta ko‘rib chiqishga yuborildi.");
      }
      setPending(null);
      setComment("");
      await refresh();
    } catch (err) {
      setActionError(err);
      await refresh();
    } finally {
      setBusy(false);
    }
  }

  async function checkQuality() {
    if (!c) return;
    setChecking(true);
    try {
      setQuality(await api<QualityReport>("ai/evaluate-content", { method: "POST", body: { content_id: c.id } }));
    } catch (err) {
      setActionError(err);
    } finally {
      setChecking(false);
    }
  }

  if (content.loading && !c) return <Loading />;
  if (content.error) return <ErrorBox error={content.error} onRetry={content.reload} />;
  if (!c) return null;

  const needsComment = pending === "reject" || pending === "request-edit" || pending === "regenerate";

  return (
    <>
      <div className="mb-4 text-sm">
        <Link href="/content" className="text-muted hover:underline">← Kontent navbati</Link>
      </div>
      <header className="mb-6 flex flex-wrap items-center gap-2">
        <h1 className="mr-2 min-w-0 text-xl font-semibold sm:text-2xl">{c.topic ?? `Kontent #${c.id}`}</h1>
        <StatusBadge status={c.status} />
        <TypeBadge type={c.content_type} />
        <span className="text-sm text-muted" data-testid="version">v{c.version}</span>
        <span className="text-sm text-muted">· {c.created_by === "AGENT" ? "AI yaratgan" : "Inson yaratgan"}</span>
      </header>

      {message && <div className="mb-4"><Notice tone="success">{message}</Notice></div>}
      {warning && <div className="mb-4"><Notice tone="warning"><span data-testid="action-warning">{warning}</span></Notice></div>}
      {actionError ? <div className="mb-4"><ErrorBox error={actionError} /></div> : null}

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_20rem]">
        <div className="min-w-0 space-y-4">
          <Card title="Kontent ko‘rinishi">
            <div className="grid gap-4 md:grid-cols-[14rem_minmax(0,1fr)]">
              <MediaBox content={c} />
              <div className="min-w-0">
                {editing ? (
                  <EditForm
                    content={c}
                    onCancel={() => setEditing(false)}
                    onSaved={async () => {
                      setEditing(false);
                      setQuality(null);
                      setMessage("Saqlandi — yangi versiya yaratildi.");
                      await refresh();
                    }}
                  />
                ) : (
                  <CaptionView content={c} />
                )}
              </div>
            </div>
            {!editing && <div className="mt-4"><StructureView content={c} /></div>}
          </Card>

          <Card
            title="Sifat tekshiruvi"
            actions={<Button onClick={checkQuality} loading={checking}>Sifatni tekshirish</Button>}
          >
            {quality ? <QualityView report={quality} /> : <p className="text-sm text-muted">Avtomatik qoidalar bo‘yicha tekshirish uchun tugmani bosing. Holat o‘zgarmaydi.</p>}
          </Card>

          <DiffCard contentId={c.id} version={c.version} versions={history.data?.versions ?? []} />

          <HistoryCard history={history.data} />
        </div>

        <div className="min-w-0 space-y-4">
          <Card title="Ma’lumot">
            <KeyValue
              items={[
                ["Platforma", "Instagram"],
                ["Rejalashtirilgan vaqt", formatDateTime(c.scheduled_at)],
                ["Reja sanasi", formatDate(c.planned_date)],
                ["Format", c.aspect_ratio ?? "—"],
                ["Til", c.language.toUpperCase()],
                ["Nashrga ruxsat", c.publish_authorized ? `Ha (v${c.version} tasdiqlangan)` : "Yo‘q"],
                ["Yangilangan", formatDateTime(c.updated_at)],
              ]}
            />
            {c.last_error && <p className="mt-3 text-sm text-red-700 dark:text-red-300">Oxirgi xato: {c.last_error}</p>}
          </Card>

          <ReadinessCard key={`${c.version}-${c.status}`} contentId={c.id} version={c.version} />

          <PublishCard key={`p-${c.version}`} content={c} onChanged={refresh} />

          <MediaManager content={c} onChanged={refresh} />

          <Card title="Amallar">
            <div className="flex flex-col gap-2" data-testid="actions">
              {canEdit && !editing && (
                <Button onClick={() => setEditing(true)} data-testid="action-edit">Tahrirlash</Button>
              )}
              {allowed.map((a) => (
                <Button
                  key={a}
                  data-testid={`action-${a}`}
                  variant={a === "approve" ? "success" : a === "reject" || a === "delete" ? "danger" : "secondary"}
                  onClick={() => {
                    setPending(a);
                    setActionError(null);
                  }}
                >
                  {ACTION_LABEL[a]}
                </Button>
              ))}
              {readOnly ? (
                <p className="text-sm text-muted">Kuzatuvchi roli: faqat ko‘rish mumkin.</p>
              ) : (
                allowed.length === 0 && !canEdit && (
                  <p className="text-sm text-muted">Holat: {STATUS_LABEL[c.status]} — amallar mavjud emas.</p>
                )
              )}
            </div>

            {pending && allowed.includes(pending) && (
              <div className="mt-4 space-y-3 rounded-xl border border-border bg-background p-3" data-testid="confirm-panel">
                <p className="text-sm font-medium">{ACTION_LABEL[pending]}</p>
                {pending === "approve" && (
                  <p className="text-sm text-muted">
                    Siz <b>{c.version}-versiyani</b> tasdiqlayapsiz. Tasdiq faqat shu versiyaga tegishli; keyin o‘zgartirilsa, qayta tasdiqlash kerak bo‘ladi. Bu amal nashr qilmaydi.
                  </p>
                )}
                {pending === "delete" && <p className="text-sm text-muted">Kontent arxivlanadi (soft delete), tasdiqlar bekor qilinadi.</p>}
                {pending === "revoke" && <p className="text-sm text-muted">Tasdiq kuchini yo‘qotadi, rejalashtirish bekor qilinadi, kontent qayta ko‘rib chiqishga qaytadi.</p>}
                {pending === "request-edit" && (
                  <label className="flex items-start gap-2 text-sm">
                    <input type="checkbox" className="mt-1" checked={aiRework} onChange={(e) => setAiRework(e.target.checked)} data-testid="ai-rework" />
                    <span>AI izoh asosida qayta ishlab chiqsin va yana ko‘rib chiqishga yuborsin</span>
                  </label>
                )}
                {pending === "regenerate" && (
                  <p className="text-sm text-muted">AI yangi versiya yozadi. U avtomatik tasdiqlanmaydi.</p>
                )}
                {pending === "schedule" && (
                  <Field label="Vaqt (Toshkent vaqti, UTC+5)" hint="Belgilangan vaqtda Celery worker nashr qiladi">
                    <input type="datetime-local" className={inputClass} data-testid="schedule-at" value={when} onChange={(e) => setWhen(e.target.value)} />
                  </Field>
                )}
                {(needsComment || pending === "approve" || pending === "revoke") && (
                  <Field label={pending === "regenerate" ? "AI uchun ko‘rsatma (ixtiyoriy)" : "Izoh (ixtiyoriy)"}>
                    <textarea className={`${inputClass} min-h-20`} maxLength={1000} value={comment} onChange={(e) => setComment(e.target.value)} />
                  </Field>
                )}
                <div className="flex flex-wrap gap-2">
                  <Button
                    data-testid="confirm-action"
                    variant={pending === "approve" ? "success" : pending === "reject" || pending === "delete" ? "danger" : "primary"}
                    loading={busy}
                    onClick={() => void confirm(pending)}
                  >
                    Tasdiqlayman
                  </Button>
                  <Button onClick={() => setPending(null)} disabled={busy}>Bekor qilish</Button>
                </div>
              </div>
            )}
          </Card>
        </div>
      </div>
    </>
  );
}

function HistoryCard({ history }: { history: ContentHistory | null }) {
  if (!history) return null;
  return (
    <Card title="Tarix">
      <div className="space-y-5 text-sm">
        <div>
          <h3 className="mb-2 font-medium">Versiyalar</h3>
          <ul className="space-y-1" data-testid="versions">
            {[...history.versions].reverse().map((v) => (
              <li key={v.version} className="flex flex-wrap justify-between gap-2">
                <span>v{v.version} · {v.source === "AGENT" ? "AI" : v.source === "HUMAN" ? "Inson" : "Tizim"}{v.change_note ? ` · ${v.change_note}` : ""}</span>
                <span className="text-muted">{formatDateTime(v.created_at)}</span>
              </li>
            ))}
          </ul>
        </div>
        {history.approvals.length > 0 && (
          <div>
            <h3 className="mb-2 font-medium">Qarorlar</h3>
            <ul className="space-y-1" data-testid="approvals">
              {history.approvals.map((a) => (
                <li key={a.id} className="flex flex-wrap justify-between gap-2">
                  <span>
                    v{a.content_version} · {a.decision === "APPROVED" ? "Tasdiqlangan" : a.decision === "REJECTED" ? "Rad etilgan" : "Tahrir so‘ralgan"} · foydalanuvchi #{a.decided_by_user_id}
                    {a.invalidated_at && <span className="text-amber-700 dark:text-amber-300"> · bekor qilingan ({a.invalidation_reason})</span>}
                    {a.comment && <span className="text-muted"> · “{a.comment}”</span>}
                  </span>
                  <span className="text-muted">{formatDateTime(a.created_at)}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        <details>
          <summary className="cursor-pointer font-medium">Audit hodisalari ({history.events.length})</summary>
          <ul className="mt-2 space-y-1">
            {[...history.events].reverse().map((e) => (
              <li key={e.id} className="flex flex-wrap justify-between gap-2">
                <span className="break-all">{e.action} · {e.actor_name ?? e.actor_type}{e.content_version ? ` · v${e.content_version}` : ""}{e.status !== "SUCCESS" ? ` · ${e.status}` : ""}</span>
                <span className="text-muted">{formatDateTime(e.timestamp)}</span>
              </li>
            ))}
          </ul>
        </details>
      </div>
    </Card>
  );
}

export default function ContentDetailPage() {
  return (
    <Suspense fallback={<Loading />}>
      <Detail />
    </Suspense>
  );
}
