"use client";

import { useState } from "react";

import { Button, Card, EmptyState, ErrorBox, KeyValue, Loading, Notice, PageHeader } from "@/components/ui";
import { api } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import type { Capability, InstagramAccountStatus, InstagramStatus, PublishingLimit } from "@/lib/types";
import { useApi } from "@/lib/useApi";

const ACCOUNT_TYPE: Record<string, string> = { business: "Business", creator: "Creator" };

function daysLeft(iso: string | null): number | null {
  if (!iso) return null;
  return Math.floor((new Date(iso).getTime() - Date.now()) / 86_400_000);
}

function Scopes({ granted, missing }: { granted: string[]; missing: string[] }) {
  return (
    <ul className="flex flex-wrap gap-1.5">
      {granted.map((s) => (
        <li key={s} className="rounded-md bg-emerald-50 px-2 py-0.5 text-xs text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200">
          {s}
        </li>
      ))}
      {missing.map((s) => (
        <li key={s} className="rounded-md bg-red-50 px-2 py-0.5 text-xs text-red-800 line-through dark:bg-red-950 dark:text-red-200">
          {s}
        </li>
      ))}
    </ul>
  );
}

function AccountCard({ account, onChanged }: { account: InstagramAccountStatus; onChanged: () => Promise<void> }) {
  const [busy, setBusy] = useState<"refresh" | "disconnect" | null>(null);
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [limit, setLimit] = useState<PublishingLimit | null>(null);
  const [limitBusy, setLimitBusy] = useState(false);
  const left = daysLeft(account.token_expires_at);

  async function checkLimit() {
    setLimitBusy(true);
    setError(null);
    try {
      setLimit(await api<PublishingLimit>(`instagram/accounts/${account.id}/publishing-limit`));
    } catch (err) {
      setError(err);
    } finally {
      setLimitBusy(false);
    }
  }

  async function run(kind: "refresh" | "disconnect") {
    setBusy(kind);
    setError(null);
    setMessage(null);
    try {
      if (kind === "refresh") {
        await api(`instagram/accounts/${account.id}/refresh-token`, { method: "POST" });
        setMessage("Token yangilandi.");
      } else {
        await api(`instagram/accounts/${account.id}`, { method: "DELETE" });
      }
      await onChanged();
    } catch (err) {
      setError(err);
    } finally {
      setBusy(null);
      setConfirming(false);
    }
  }

  return (
    <Card
      title={<span data-testid="instagram-username">@{account.username ?? account.ig_user_id}</span>}
      actions={
        <span className="rounded-md bg-background px-2 py-0.5 text-xs text-muted">
          {ACCOUNT_TYPE[account.account_type] ?? account.account_type}
        </span>
      }
    >
      <div className="space-y-3" data-testid="instagram-account">
        {account.needs_reconnect && (
          <Notice tone="warning">
            Qayta ulash kerak: token yo‘q, muddati o‘tgan yoki majburiy ruxsat berilmagan. “Instagram’ni ulash”
            tugmasini qayta bosing.
          </Notice>
        )}
        {account.warnings.map((w) => (
          <Notice key={w} tone="warning">
            {w}
          </Notice>
        ))}
        <KeyValue
          items={[
            ["Instagram ID", <code key="id" className="text-xs">{account.ig_user_id}</code>],
            ["Ulangan", formatDateTime(account.connected_at)],
            [
              "Token muddati",
              <span key="exp" data-testid="token-expiry">
                {formatDateTime(account.token_expires_at)}
                {left !== null && <span className="text-muted"> ({left >= 0 ? `${left} kun qoldi` : "muddati o‘tgan"})</span>}
              </span>,
            ],
            ["Oxirgi yangilanish", formatDateTime(account.token_last_refreshed_at)],
            ["Ruxsatlar", <Scopes key="sc" granted={account.scopes} missing={account.missing_scopes} />],
          ]}
        />
        {limit && (
          <p className="text-sm" data-testid="publishing-limit">
            Nashr limiti (Meta, 24 soat): <b>{limit.quota_usage}</b> / {limit.quota_total} ishlatilgan · {limit.remaining} ta qoldi
            {!limit.from_meta && <span className="text-muted"> (Meta jami limitni qaytarmadi — sozlamadagi qiymat)</span>}
          </p>
        )}
        <ErrorBox error={error} />
        {message && <Notice tone="success">{message}</Notice>}
        <div className="flex flex-wrap gap-2">
          <Button onClick={() => void run("refresh")} loading={busy === "refresh"} disabled={busy !== null}>
            Tokenni yangilash
          </Button>
          <Button onClick={() => void checkLimit()} loading={limitBusy} disabled={busy !== null} data-testid="check-limit">
            Nashr limitini tekshirish
          </Button>
          {confirming ? (
            <>
              <Button variant="danger" onClick={() => void run("disconnect")} loading={busy === "disconnect"}>
                Ha, uzish
              </Button>
              <Button variant="ghost" onClick={() => setConfirming(false)} disabled={busy !== null}>
                Bekor qilish
              </Button>
            </>
          ) : (
            <Button variant="danger" onClick={() => setConfirming(true)} disabled={busy !== null}>
              Uzish
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
}

export default function InstagramPage() {
  const { data, error, loading, reload } = useApi<InstagramStatus>("instagram/status");
  const [starting, setStarting] = useState(false);
  const [startError, setStartError] = useState<unknown>(null);

  async function connect() {
    setStarting(true);
    setStartError(null);
    try {
      const { authorize_url } = await api<{ authorize_url: string }>("instagram/oauth/start", { method: "POST" });
      window.location.assign(authorize_url); // official Instagram consent screen
    } catch (err) {
      setStartError(err);
      setStarting(false);
    }
  }

  return (
    <>
      <PageHeader title="Instagram akkaunt" subtitle="Rasmiy Meta API (Instagram Login) orqali ulanish." />
      {loading && !data && <Loading />}
      <ErrorBox error={error} onRetry={() => void reload()} />
      {data && (
        <div className="space-y-4">
          <Card title="Ulanish">
            <KeyValue
              items={[
                [
                  "Holat",
                  <span key="s" data-testid="instagram-status">
                    {data.accounts.length ? `${data.accounts.length} ta akkaunt ulangan` : "Ulanmagan"}
                  </span>,
                ],
                ["Usul", "Instagram API with Instagram Login"],
                ["Graph API versiyasi", data.graph_api_version],
                ["Redirect URI", data.redirect_uri ? <code key="r" className="text-xs">{data.redirect_uri}</code> : "—"],
                ["So‘raladigan ruxsatlar", <Scopes key="sc" granted={data.requested_scopes} missing={[]} />],
                ["Token saqlash", "Faqat shifrlangan (Fernet), brauzerga hech qachon yuborilmaydi"],
                ["Nashr rejimi", data.dry_run ? "DRY RUN (Instagram’ga hech narsa yuborilmaydi)" : "Real"],
              ]}
            />
            {!data.configured && (
              <div className="mt-4" data-testid="meta-not-configured">
                <Notice tone="warning">
                  Meta ilovasi sozlanmagan. Backend <code>.env</code> faylida <code>META_APP_ID</code>,{" "}
                  <code>META_APP_SECRET</code> va <code>META_REDIRECT_URI</code> ni to‘ldiring (README, 9–11-bo‘limlar).
                </Notice>
              </div>
            )}
            <ErrorBox error={startError} />
            <Button
              variant="primary"
              className="mt-4"
              onClick={() => void connect()}
              loading={starting}
              disabled={!data.configured}
            >
              Instagram’ni ulash
            </Button>
          </Card>
          {data.accounts.length === 0 ? (
            <EmptyState title="Hali Instagram akkaunt ulanmagan">
              Faqat Business yoki Creator (professional) akkauntlar ulanadi.
            </EmptyState>
          ) : (
            data.accounts.map((a) => <AccountCard key={a.id} account={a} onChanged={reload} />)
          )}
          <CapabilitiesCard />
          <Notice>
            Instagram login yoki paroli hech qachon so‘ralmaydi va saqlanmaydi. Ulanish faqat Meta’ning rasmiy OAuth
            oynasi orqali bo‘ladi. Nashr faqat siz tasdiqlagan kontent uchun va faqat sizning buyrug‘ingiz yoki rejangiz bo‘yicha.
          </Notice>
        </div>
      )}
    </>
  );
}

function CapabilitiesCard() {
  const { data } = useApi<Capability[]>("instagram/capabilities");
  if (!data) return null;
  return (
    <Card title="Meta API imkoniyatlari">
      <ul className="space-y-1.5 text-sm" data-testid="capabilities">
        {data.map((c) => (
          <li key={c.key} className="flex gap-2">
            <span aria-hidden className={c.supported ? "text-emerald-600" : "text-muted"}>{c.supported ? "✓" : "✗"}</span>
            <span>
              {c.label} — <span className="text-muted">{c.note}</span>
            </span>
          </li>
        ))}
      </ul>
    </Card>
  );
}
