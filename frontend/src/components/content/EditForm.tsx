"use client";

import { useState, type FormEvent } from "react";

import { Button, ErrorBox, Field, Notice, inputClass } from "@/components/ui";
import { api } from "@/lib/api";
import { parseHashtags } from "@/lib/format";
import type { Content, Structure, StructureItem } from "@/lib/types";

const TEXT_KEYS = ["heading", "body", "visual", "on_screen_text", "narration", "text"];
const KEY_LABEL: Record<string, string> = {
  heading: "Sarlavha",
  body: "Matn",
  visual: "Kadr",
  on_screen_text: "Ekrandagi matn",
  narration: "Ovoz",
  text: "Matn",
};

export function EditForm({ content, onSaved, onCancel }: { content: Content; onSaved: (c: Content) => void; onCancel: () => void }) {
  const [form, setForm] = useState({
    topic: content.topic ?? "",
    hook: content.hook ?? "",
    caption: content.caption ?? "",
    cta: content.cta ?? "",
    hashtags: content.hashtags.join(" "),
    planned_date: content.planned_date ?? "",
    change_note: "",
  });
  const [structure, setStructure] = useState<Structure>(structuredClone(content.structure ?? {}));
  const [error, setError] = useState<unknown>(null);
  const [saving, setSaving] = useState(false);
  const listKey = (["slides", "scenes", "frames"] as const).find((k) => structure[k]?.length);
  const wasApproved = ["APPROVED", "SCHEDULED"].includes(content.status);

  function setItem(i: number, key: string, value: string) {
    if (!listKey) return;
    const items = [...(structure[listKey] ?? [])] as StructureItem[];
    items[i] = { ...items[i], [key]: value };
    setStructure({ ...structure, [listKey]: items });
  }

  async function submit(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const updated = await api<Content>(`contents/${content.id}`, {
        method: "PATCH",
        body: {
          expected_version: content.version,
          topic: form.topic || null,
          hook: form.hook || null,
          caption: form.caption || null,
          cta: form.cta || null,
          hashtags: parseHashtags(form.hashtags),
          planned_date: form.planned_date || null,
          change_note: form.change_note || null,
          ...(listKey ? { structure } : {}),
        },
      });
      onSaved(updated);
    } catch (err) {
      setError(err);
    } finally {
      setSaving(false);
    }
  }

  const set = (k: keyof typeof form) => (e: { target: { value: string } }) => setForm({ ...form, [k]: e.target.value });

  return (
    <form onSubmit={submit} className="space-y-4" data-testid="edit-form">
      {wasApproved && (
        <Notice tone="warning">
          Bu kontent tasdiqlangan. Saqlasangiz yangi versiya yaratiladi, oldingi tasdiq bekor bo‘ladi va kontent qayta ko‘rib chiqishga qaytadi.
        </Notice>
      )}
      <Field label="Mavzu"><input className={inputClass} maxLength={300} value={form.topic} onChange={set("topic")} /></Field>
      <Field label="Hook"><input className={inputClass} maxLength={1000} value={form.hook} onChange={set("hook")} /></Field>
      <Field label="Caption" hint={`${form.caption.length}/2200`}>
        <textarea name="caption" className={`${inputClass} min-h-40`} maxLength={2200} value={form.caption} onChange={set("caption")} />
      </Field>
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="CTA"><input className={inputClass} maxLength={500} value={form.cta} onChange={set("cta")} /></Field>
        <Field label="Reja sanasi" hint="Faqat kalendar uchun; nashr qilmaydi">
          <input type="date" className={inputClass} value={form.planned_date} onChange={set("planned_date")} />
        </Field>
      </div>
      <Field label="Hashtaglar" hint="Bo‘sh joy yoki vergul bilan, maksimal 30 ta">
        <input className={inputClass} value={form.hashtags} onChange={set("hashtags")} />
      </Field>
      {listKey && (
        <fieldset className="space-y-3">
          <legend className="text-sm font-medium">{listKey === "slides" ? "Slaydlar" : listKey === "scenes" ? "Sahnalar" : "Kadrlar"}</legend>
          {(structure[listKey] as StructureItem[]).map((item, i) => (
            <div key={i} className="space-y-2 rounded-xl border border-border p-3">
              <p className="text-xs text-muted">#{i + 1}</p>
              {TEXT_KEYS.filter((k) => k in item).map((k) => (
                <Field key={k} label={KEY_LABEL[k]}>
                  <textarea className={`${inputClass} min-h-16`} value={String(item[k] ?? "")} onChange={(e) => setItem(i, k, e.target.value)} />
                </Field>
              ))}
            </div>
          ))}
        </fieldset>
      )}
      <Field label="O‘zgarish izohi (ixtiyoriy)"><input className={inputClass} maxLength={500} value={form.change_note} onChange={set("change_note")} /></Field>
      <ErrorBox error={error} />
      <div className="flex flex-wrap gap-2">
        <Button type="submit" variant="primary" loading={saving}>Saqlash (yangi versiya)</Button>
        <Button onClick={onCancel}>Bekor qilish</Button>
      </div>
    </form>
  );
}
