"use client";

import Link from "next/link";
import { useState, type FormEvent } from "react";

import { QualityView } from "@/components/content/Quality";
import { Button, Card, ErrorBox, Field, Notice, PageHeader, StatusBadge, inputClass } from "@/components/ui";
import { runGeneration } from "@/lib/ai";
import { formatDate, isoDate, TYPE_LABEL } from "@/lib/format";
import type { AIStatus, BrandProfile, ContentType, GenerationResponse, Language } from "@/lib/types";
import { useApi } from "@/lib/useApi";

type Mode = "post" | "carousel" | "reels" | "story" | "ideas" | "plan" | "strategy" | "hashtags";
const MODES: { id: Mode; label: string; path: string }[] = [
  { id: "post", label: "Post", path: "ai/generate-caption" },
  { id: "carousel", label: "Karusel", path: "ai/generate-carousel" },
  { id: "reels", label: "Reels", path: "ai/generate-reels-script" },
  { id: "story", label: "Story", path: "ai/generate-story" },
  { id: "ideas", label: "G‘oyalar", path: "ai/ideas" },
  { id: "plan", label: "Kontent reja", path: "ai/content-plan" },
  { id: "strategy", label: "Strategiya", path: "ai/strategy" },
  { id: "hashtags", label: "Hashtaglar", path: "ai/hashtags" },
];
const CONTENT_MODES: Mode[] = ["post", "carousel", "reels", "story"];
const LANG_LABEL: Record<Language, string> = { uz: "O‘zbek", ru: "Rus", en: "Ingliz" };

function nextMonday(): string {
  const d = new Date();
  d.setDate(d.getDate() + ((8 - d.getDay()) % 7 || 7));
  return isoDate(d);
}

export default function AIStudioPage() {
  const status = useApi<AIStatus>("ai/status");
  const brands = useApi<BrandProfile[]>("brand-profiles");
  const brand = brands.data?.find((b) => b.is_default) ?? brands.data?.[0];
  const [mode, setMode] = useState<Mode>("carousel");
  const [form, setForm] = useState({
    topic: "",
    language: "uz" as Language,
    instructions: "",
    slides: 5,
    target_seconds: 30,
    count: 5,
    start_date: nextMonday(),
    period: "week" as "week" | "month",
    posts_per_week: 5,
    submit_for_review: false,
    save_as_drafts: false,
  });
  const [result, setResult] = useState<GenerationResponse | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState<string | null>(null);

  const current = MODES.find((m) => m.id === mode)!;
  const needsTopic = CONTENT_MODES.includes(mode) || mode === "hashtags";

  async function submit(e: FormEvent) {
    e.preventDefault();
    setRunning(true);
    setError(null);
    setResult(null);
    setProgress("AI ishlamoqda… (lokal modelda 30–120 soniya olishi mumkin)");
    const base = { language: form.language, instructions: form.instructions || null };
    const body: Record<string, unknown> = { ...base };
    if (needsTopic) body.topic = form.topic;
    if (CONTENT_MODES.includes(mode)) body.submit_for_review = form.submit_for_review;
    if (mode === "carousel") body.slides = form.slides;
    if (mode === "reels") body.target_seconds = form.target_seconds;
    if (mode === "ideas") Object.assign(body, { count: form.count, save_as_drafts: form.save_as_drafts, topic: form.topic || null });
    if (mode === "plan") Object.assign(body, { start_date: form.start_date, period: form.period, posts_per_week: form.posts_per_week, save_as_drafts: form.save_as_drafts });
    if (mode === "hashtags") body.count = 15;
    try {
      setResult(await runGeneration(current.path, body, (r) => setProgress(`Vazifa #${r.job.id}: ${r.job.status}`)));
    } catch (err) {
      setError(err);
    } finally {
      setRunning(false);
      setProgress(null);
    }
  }

  const set = (k: keyof typeof form) => (e: { target: { value: string } }) => setForm({ ...form, [k]: e.target.value });

  return (
    <>
      <PageHeader
        title="AI Studio"
        subtitle="AI qoralama tayyorlaydi. Natija hech qachon avtomatik tasdiqlanmaydi yoki nashr qilinmaydi."
      />
      {status.data && !status.data.text.available && (
        <div className="mb-4">
          <Notice tone="warning">
            AI provayder ishlamayapti ({status.data.text.provider}: {status.data.text.message ?? status.data.text.error_code}). Generatsiya xato qaytaradi.
          </Notice>
        </div>
      )}
      {status.data?.text.provider === "mock" && (
        <div className="mb-4">
          <Notice>Mock provayder yoqilgan — natijalar test uchun deterministik matn.</Notice>
        </div>
      )}

      <div className="-mx-4 mb-4 overflow-x-auto px-4 sm:mx-0 sm:px-0" role="tablist" aria-label="Generatsiya turi">
        <div className="flex w-max gap-1">
          {MODES.map((m) => (
            <button
              key={m.id}
              type="button"
              role="tab"
              aria-selected={mode === m.id}
              onClick={() => {
                setMode(m.id);
                setResult(null);
                setError(null);
              }}
              className={`whitespace-nowrap rounded-full px-3 py-1.5 text-sm ${mode === m.id ? "bg-accent text-accent-fg" : "border border-border bg-card"}`}
            >
              {m.label}
            </button>
          ))}
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-[minmax(0,24rem)_minmax(0,1fr)]">
        <Card title={current.label}>
          <form onSubmit={submit} className="space-y-4" data-testid="ai-form">
            {brand && <p className="text-xs text-muted">Brend: {brand.name}</p>}
            {(needsTopic || mode === "ideas") && (
              <Field label={mode === "ideas" ? "Mavzu (ixtiyoriy)" : "Mavzu"}>
                <input name="topic" className={inputClass} required={needsTopic} minLength={needsTopic ? 3 : undefined} maxLength={300} value={form.topic} onChange={set("topic")} placeholder="Masalan: Minimalist yotoqxona" />
              </Field>
            )}
            <Field label="Til">
              <select className={inputClass} value={form.language} onChange={set("language")}>
                {(brand?.languages ?? ["uz"]).map((l) => (
                  <option key={l} value={l}>{LANG_LABEL[l]}</option>
                ))}
              </select>
            </Field>
            {mode === "carousel" && (
              <Field label="Slaydlar soni (2–10)">
                <input type="number" min={2} max={10} className={inputClass} value={form.slides} onChange={(e) => setForm({ ...form, slides: Number(e.target.value) })} />
              </Field>
            )}
            {mode === "reels" && (
              <Field label="Davomiylik (soniya, 5–90)">
                <input type="number" min={5} max={90} className={inputClass} value={form.target_seconds} onChange={(e) => setForm({ ...form, target_seconds: Number(e.target.value) })} />
              </Field>
            )}
            {mode === "ideas" && (
              <Field label="G‘oyalar soni (1–10)">
                <input type="number" min={1} max={10} className={inputClass} value={form.count} onChange={(e) => setForm({ ...form, count: Number(e.target.value) })} />
              </Field>
            )}
            {mode === "plan" && (
              <>
                <Field label="Boshlanish sanasi">
                  <input type="date" className={inputClass} required value={form.start_date} onChange={set("start_date")} />
                </Field>
                <Field label="Davr">
                  <select className={inputClass} value={form.period} onChange={set("period")}>
                    <option value="week">Hafta</option>
                    <option value="month">Oy</option>
                  </select>
                </Field>
                <Field label="Haftasiga postlar (1–7)">
                  <input type="number" min={1} max={7} className={inputClass} value={form.posts_per_week} onChange={(e) => setForm({ ...form, posts_per_week: Number(e.target.value) })} />
                </Field>
              </>
            )}
            <Field label="Qo‘shimcha ko‘rsatma (ixtiyoriy)" hint="Maksimal 1000 belgi">
              <textarea className={`${inputClass} min-h-20`} maxLength={1000} value={form.instructions} onChange={set("instructions")} />
            </Field>
            {CONTENT_MODES.includes(mode) && (
              <label className="flex items-start gap-2 text-sm">
                <input type="checkbox" className="mt-1" checked={form.submit_for_review} onChange={(e) => setForm({ ...form, submit_for_review: e.target.checked })} />
                <span>Sifat tekshiruvidan o‘tsa, darhol ko‘rib chiqishga yuborish (tasdiqlash baribir sizda)</span>
              </label>
            )}
            {(mode === "ideas" || mode === "plan") && (
              <label className="flex items-start gap-2 text-sm">
                <input type="checkbox" className="mt-1" checked={form.save_as_drafts} onChange={(e) => setForm({ ...form, save_as_drafts: e.target.checked })} />
                <span>Har birini qoralama (DRAFT) sifatida saqlash</span>
              </label>
            )}
            <Button type="submit" variant="primary" loading={running} className="w-full" data-testid="ai-generate">
              Yaratish
            </Button>
            {progress && <p className="text-xs text-muted" role="status">{progress}</p>}
          </form>
        </Card>

        <div className="min-w-0 space-y-4">
          <ErrorBox error={error} />
          {result && <ResultView result={result} />}
          {!result && !error && (
            <Card>
              <p className="text-sm text-muted">Natija shu yerda ko‘rinadi. Kontent turlari qoralama sifatida saqlanadi va “Kontent navbati”da paydo bo‘ladi.</p>
            </Card>
          )}
        </div>
      </div>
    </>
  );
}

function ResultView({ result }: { result: GenerationResponse }) {
  const r = (result.result ?? {}) as Record<string, unknown>;
  return (
    <div className="space-y-4" data-testid="ai-result">
      {result.content_id && (
        <Card title="Saqlandi">
          <div className="flex flex-wrap items-center gap-3 text-sm">
            {result.content_status && <StatusBadge status={result.content_status} />}
            <Link href={`/content/${result.content_id}`} className="font-medium underline" data-testid="ai-result-link">
              Kontent #{result.content_id} ni ochish
            </Link>
            <span className="text-muted">{result.job.provider} · {result.job.model} · {result.job.duration_ms ?? "—"} ms</span>
          </div>
        </Card>
      )}
      {result.quality && (
        <Card title="Sifat tekshiruvi">
          <QualityView report={result.quality} />
        </Card>
      )}
      {Array.isArray(r.ideas) && (
        <Card title="G‘oyalar">
          <ul className="space-y-3 text-sm">
            {(r.ideas as Record<string, string>[]).map((idea, i) => (
              <li key={i} className="rounded-xl border border-border p-3">
                <p className="font-medium">{idea.title}</p>
                <p className="text-xs text-muted">{TYPE_LABEL[idea.format as ContentType] ?? idea.format} · {idea.objective} · {idea.topic}</p>
                <p className="mt-1">{idea.hook}</p>
                <p className="mt-1 text-muted">{idea.summary}</p>
              </li>
            ))}
          </ul>
        </Card>
      )}
      {Array.isArray(r.items) && (
        <Card title={`Kontent reja: ${formatDate(r.start_date as string)} – ${formatDate(r.end_date as string)}`}>
          <ul className="divide-y divide-border text-sm">
            {(r.items as Record<string, string | number | null>[]).map((it, i) => (
              <li key={i} className="flex flex-wrap items-center justify-between gap-2 py-2">
                <span>
                  {formatDate(it.suggested_date as string)} · {it.weekday} · {TYPE_LABEL[it.format as ContentType] ?? it.format} — {it.title}
                </span>
                {it.content_id ? (
                  <Link href={`/content/${it.content_id}`} className="underline">#{it.content_id}</Link>
                ) : (
                  <span className="text-xs text-muted">{it.status}</span>
                )}
              </li>
            ))}
          </ul>
          <p className="mt-3 text-xs text-muted">{r.timing_basis as string}</p>
        </Card>
      )}
      {Array.isArray(r.pillars) && (
        <Card title="Strategiya">
          <p className="text-sm">{r.summary as string}</p>
          <ul className="mt-3 space-y-2 text-sm">
            {(r.pillars as Record<string, string>[]).map((p, i) => (
              <li key={i}><b>{p.name}</b> — {p.rationale}</li>
            ))}
          </ul>
          <h3 className="mt-4 text-sm font-medium">Tavsiyalar</h3>
          <ul className="mt-1 list-disc space-y-1 pl-5 text-sm">
            {(r.recommendations as string[]).map((x, i) => <li key={i}>{x}</li>)}
          </ul>
          {Array.isArray(r.risks) && (r.risks as string[]).length > 0 && (
            <>
              <h3 className="mt-4 text-sm font-medium">Xavflar</h3>
              <ul className="mt-1 list-disc space-y-1 pl-5 text-sm">
                {(r.risks as string[]).map((x, i) => <li key={i}>{x}</li>)}
              </ul>
            </>
          )}
        </Card>
      )}
      {!result.content_id && Array.isArray(r.hashtags) && (
        <Card title="Hashtaglar">
          <p className="break-words text-sm">{(r.hashtags as string[]).join(" ")}</p>
        </Card>
      )}
    </div>
  );
}
