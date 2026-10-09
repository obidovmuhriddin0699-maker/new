"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { Button, Card, ErrorBox, Field, PageHeader, inputClass } from "@/components/ui";
import { api } from "@/lib/api";
import { parseHashtags, TYPE_LABEL } from "@/lib/format";
import type { Content, ContentType, Language } from "@/lib/types";

export default function NewContentPage() {
  const router = useRouter();
  const [form, setForm] = useState({ content_type: "POST" as ContentType, language: "uz" as Language, topic: "", hook: "", caption: "", cta: "", hashtags: "" });
  const [error, setError] = useState<unknown>(null);
  const [saving, setSaving] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const content = await api<Content>("contents", {
        method: "POST",
        body: {
          content_type: form.content_type,
          language: form.language,
          topic: form.topic || null,
          hook: form.hook || null,
          caption: form.caption || null,
          cta: form.cta || null,
          hashtags: parseHashtags(form.hashtags),
        },
      });
      router.push(`/content/${content.id}`);
    } catch (err) {
      setError(err);
    } finally {
      setSaving(false);
    }
  }

  const set = (k: keyof typeof form) => (e: { target: { value: string } }) => setForm({ ...form, [k]: e.target.value });

  return (
    <>
      <PageHeader title="Qo‘lda kontent yaratish" subtitle="Qoralama sifatida saqlanadi (DRAFT)." />
      <Card>
        <form onSubmit={submit} className="grid gap-4 sm:grid-cols-2">
          <Field label="Turi">
            <select className={inputClass} value={form.content_type} onChange={set("content_type")}>
              {(Object.keys(TYPE_LABEL) as ContentType[]).map((t) => (
                <option key={t} value={t}>{TYPE_LABEL[t]}</option>
              ))}
            </select>
          </Field>
          <Field label="Til">
            <select className={inputClass} value={form.language} onChange={set("language")}>
              <option value="uz">O‘zbek</option>
              <option value="ru">Rus</option>
              <option value="en">Ingliz</option>
            </select>
          </Field>
          <div className="sm:col-span-2">
            <Field label="Mavzu"><input className={inputClass} maxLength={300} value={form.topic} onChange={set("topic")} /></Field>
          </div>
          <div className="sm:col-span-2">
            <Field label="Hook (birinchi qator)"><input className={inputClass} maxLength={1000} value={form.hook} onChange={set("hook")} /></Field>
          </div>
          <div className="sm:col-span-2">
            <Field label="Caption" hint={`${form.caption.length}/2200`}>
              <textarea className={`${inputClass} min-h-40`} maxLength={2200} value={form.caption} onChange={set("caption")} />
            </Field>
          </div>
          <Field label="CTA"><input className={inputClass} maxLength={500} value={form.cta} onChange={set("cta")} /></Field>
          <Field label="Hashtaglar" hint="Bo‘sh joy yoki vergul bilan, maksimal 30 ta">
            <input className={inputClass} value={form.hashtags} onChange={set("hashtags")} />
          </Field>
          <div className="sm:col-span-2">
            <ErrorBox error={error} />
            <Button type="submit" variant="primary" loading={saving} className="mt-2">Saqlash</Button>
          </div>
        </form>
      </Card>
    </>
  );
}
