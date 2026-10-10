"use client";

import { useEffect, useState, type FormEvent } from "react";

import { Button, Card, ErrorBox, Field, Loading, Notice, PageHeader, inputClass } from "@/components/ui";
import { api } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import type { BrandProfile, Language } from "@/lib/types";
import { useApi } from "@/lib/useApi";

const LIST_FIELDS: { key: keyof BrandProfile; label: string; hint?: string }[] = [
  { key: "voice", label: "Brend ovozi (uslub)" },
  { key: "topics", label: "Mavzular" },
  { key: "services", label: "Xizmatlar" },
  { key: "preferred_styles", label: "Afzal dizayn uslublari" },
  { key: "content_goals", label: "Kontent maqsadlari" },
  { key: "preferred_ctas", label: "Afzal CTA’lar" },
  { key: "forbidden_rules", label: "Qoidalar va taqiqlar", hint: "AI uchun ko‘rsatma (masalan: Uydirma statistika yozma)" },
  { key: "banned_phrases", label: "Taqiqlangan iboralar", hint: "Sifat tekshiruvi bularni xato deb belgilaydi" },
];

type Form = Record<string, string>;

function toForm(b: BrandProfile): Form {
  const f: Form = {
    name: b.name,
    niche: b.niche ?? "",
    target_audience: b.target_audience ?? "",
    visual_style: b.visual_style ?? "",
  };
  for (const { key } of LIST_FIELDS) f[key] = (b[key] as string[]).join("\n");
  return f;
}

export default function BrandPage() {
  const { data, error, loading, reload } = useApi<BrandProfile[]>("brand-profiles");
  const brand = data?.find((b) => b.is_default) ?? data?.[0];
  const [form, setForm] = useState<Form | null>(null);
  const [languages, setLanguages] = useState<Language[]>([]);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<unknown>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (brand) {
      setForm(toForm(brand));
      setLanguages(brand.languages);
    }
  }, [brand]);

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!brand || !form) return;
    setSaving(true);
    setSaveError(null);
    setSaved(false);
    const body: Record<string, unknown> = {
      name: form.name,
      niche: form.niche || null,
      target_audience: form.target_audience || null,
      visual_style: form.visual_style || null,
      languages,
    };
    for (const { key } of LIST_FIELDS) {
      body[key] = form[key].split("\n").map((s) => s.trim()).filter(Boolean);
    }
    try {
      await api(`brand-profiles/${brand.id}`, { method: "PATCH", body });
      setSaved(true);
      await reload();
    } catch (err) {
      setSaveError(err);
    } finally {
      setSaving(false);
    }
  }

  return (
    <>
      <PageHeader title="Brend sozlamalari" subtitle="AI shu profil asosida kontent yozadi va sifatni tekshiradi." />
      {loading && !data && <Loading />}
      <ErrorBox error={error} onRetry={reload} />
      {data && !brand && <Notice>Brend profili yo‘q. Backendda <code>python -m app.cli seed</code> ni ishga tushiring.</Notice>}
      {brand && form && (
        <Card>
          <form onSubmit={submit} className="space-y-4" data-testid="brand-form">
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="Brend nomi"><input className={inputClass} required minLength={2} maxLength={120} value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></Field>
              <Field label="Soha"><input className={inputClass} maxLength={120} value={form.niche} onChange={(e) => setForm({ ...form, niche: e.target.value })} /></Field>
            </div>
            <Field label="Maqsadli auditoriya"><textarea className={`${inputClass} min-h-20`} maxLength={1500} value={form.target_audience} onChange={(e) => setForm({ ...form, target_audience: e.target.value })} /></Field>
            <Field label="Vizual uslub"><textarea className={`${inputClass} min-h-20`} maxLength={1500} value={form.visual_style} onChange={(e) => setForm({ ...form, visual_style: e.target.value })} /></Field>
            <fieldset>
              <legend className="mb-1 text-sm font-medium">Tillar</legend>
              <div className="flex gap-4 text-sm">
                {(["uz", "ru", "en"] as Language[]).map((l) => (
                  <label key={l} className="flex items-center gap-1.5">
                    <input
                      type="checkbox"
                      checked={languages.includes(l)}
                      onChange={(e) => setLanguages(e.target.checked ? [...languages, l] : languages.filter((x) => x !== l))}
                    />
                    {l.toUpperCase()}
                  </label>
                ))}
              </div>
            </fieldset>
            <div className="grid gap-4 md:grid-cols-2">
              {LIST_FIELDS.map(({ key, label, hint }) => (
                <Field key={key} label={label} hint={hint ?? "Har bir qatorga bittadan"}>
                  <textarea className={`${inputClass} min-h-28`} value={form[key]} onChange={(e) => setForm({ ...form, [key]: e.target.value })} />
                </Field>
              ))}
            </div>
            <ErrorBox error={saveError} />
            {saved && <Notice tone="success">Saqlandi.</Notice>}
            <div className="flex flex-wrap items-center gap-3">
              <Button type="submit" variant="primary" loading={saving} disabled={languages.length === 0}>Saqlash</Button>
              <span className="text-xs text-muted">Oxirgi o‘zgarish: {formatDateTime(brand.updated_at)}</span>
            </div>
          </form>
        </Card>
      )}
    </>
  );
}
