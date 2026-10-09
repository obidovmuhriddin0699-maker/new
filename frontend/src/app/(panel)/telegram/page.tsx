"use client";

import { useState } from "react";

import { Button, Card, ErrorBox, KeyValue, Loading, Notice, PageHeader } from "@/components/ui";
import { api } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import { useApi } from "@/lib/useApi";

type Status = {
  enabled: boolean;
  bot_username: string | null;
  linked: boolean;
  telegram_user_id: number | null;
  allowed: boolean;
  commands: string[];
};
type LinkCode = { code: string; expires_at: string; deep_link: string | null; instructions: string };

export default function TelegramPage() {
  const { data, error, loading, reload } = useApi<Status>("telegram/status");
  const [code, setCode] = useState<LinkCode | null>(null);
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState<unknown>(null);

  async function createCode() {
    setBusy(true);
    setActionError(null);
    try {
      setCode(await api<LinkCode>("telegram/link-code", { method: "POST" }));
    } catch (err) {
      setActionError(err);
    } finally {
      setBusy(false);
    }
  }

  async function unlink() {
    setBusy(true);
    setActionError(null);
    try {
      await api("telegram/link", { method: "DELETE" });
      setCode(null);
      await reload();
    } catch (err) {
      setActionError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <PageHeader title="Telegram" subtitle="Kontentni Telegram orqali ko‘rib chiqish va tasdiqlash." />
      {loading && !data && <Loading />}
      <ErrorBox error={error} onRetry={reload} />
      <ErrorBox error={actionError} />
      {data && (
        <div className="space-y-4">
          {!data.enabled && (
            <Notice tone="warning">
              Bot sozlanmagan. Serverda <code>TELEGRAM_ENABLED=true</code>, <code>TELEGRAM_BOT_TOKEN</code> va{" "}
              <code>TELEGRAM_ALLOWED_USER_IDS</code> ni o‘rnating, keyin botni ishga tushiring:{" "}
              <code>python -m app.integrations.telegram</code>. Hisobni hozir ham bog‘lash mumkin.
            </Notice>
          )}
          <Card title="Holat">
            <KeyValue
              items={[
                ["Bot", data.enabled ? `Yoqilgan${data.bot_username ? ` (@${data.bot_username})` : ""}` : "O‘chirilgan"],
                ["Hisobingiz", <span key="l" data-testid="telegram-linked">{data.linked ? `Bog‘langan (ID ${data.telegram_user_id})` : "Bog‘lanmagan"}</span>],
                ["Ruxsat ro‘yxati", data.linked ? (data.allowed ? "Ha" : "Yo‘q — TELEGRAM_ALLOWED_USER_IDS ga qo‘shing") : "—"],
              ]}
            />
            <div className="mt-4 flex flex-wrap gap-2">
              <Button variant="primary" onClick={createCode} loading={busy} data-testid="telegram-code">
                {data.linked ? "Boshqa Telegram hisobini bog‘lash" : "Bog‘lash kodini olish"}
              </Button>
              {data.linked && (
                <Button variant="danger" onClick={unlink} disabled={busy} data-testid="telegram-unlink">
                  Bog‘lanishni uzish
                </Button>
              )}
            </div>
          </Card>

          {code && (
            <Card title="Bog‘lash kodi">
              <p className="text-sm">Botga quyidagi buyruqni yuboring (kod bir marta ishlaydi):</p>
              <p className="mt-2 select-all rounded-lg bg-background px-3 py-2 font-mono text-lg" data-testid="telegram-code-value">
                /start {code.code}
              </p>
              {code.deep_link && (
                <a href={code.deep_link} className="mt-2 inline-block text-sm underline" target="_blank" rel="noreferrer">
                  Telegram’da ochish
                </a>
              )}
              <p className="mt-2 text-xs text-muted">Amal qilish muddati: {formatDateTime(code.expires_at)}. Kod faqat xesh ko‘rinishida saqlanadi.</p>
            </Card>
          )}

          <Card title="Buyruqlar">
            <div className="flex flex-wrap gap-2">
              {data.commands.map((c) => (
                <code key={c} className="rounded bg-background px-2 py-1 text-sm">{c}</code>
              ))}
            </div>
            <ul className="mt-4 list-disc space-y-1 pl-5 text-sm text-muted">
              <li>Tasdiqlash tugmalari bir martalik va faqat sizning Telegram hisobingiz uchun ishlaydi.</li>
              <li>Tasdiqlash va rad etish ikki bosqichli: avval tugma, keyin “Ha”.</li>
              <li>Tugma kontentning aniq versiyasiga bog‘langan; kontent o‘zgarsa, eski tugma ishlamaydi.</li>
              <li>Tasdiqlash nashr qilmaydi — avtomatik nashr PHASE 8 da.</li>
            </ul>
          </Card>
        </div>
      )}
    </>
  );
}
