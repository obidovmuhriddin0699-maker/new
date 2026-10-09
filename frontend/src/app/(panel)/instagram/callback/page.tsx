"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useRef, useState } from "react";

import { Card, ErrorBox, LinkButton, Loading, Notice, PageHeader } from "@/components/ui";
import { ApiError, api } from "@/lib/api";
import type { InstagramConnectResult } from "@/lib/types";

// Meta redirects the browser here with ?code&state (or ?error). The code is handed to
// the backend once over the same-origin proxy; tokens never reach the browser.
function Callback() {
  const params = useSearchParams();
  const started = useRef(false); // effects run twice in dev (StrictMode); the state is one-time
  const [result, setResult] = useState<InstagramConnectResult | null>(null);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    if (started.current) return;
    started.current = true;
    const state = params.get("state");
    if (!state) {
      setError(new ApiError(400, "instagram_oauth_state_invalid", "Ulanish so‘rovi topilmadi. Qaytadan boshlang."));
      return;
    }
    api<InstagramConnectResult>("instagram/oauth/callback", {
      method: "POST",
      body: {
        state,
        code: params.get("code"),
        error: params.get("error"),
        error_reason: params.get("error_reason"),
        error_description: params.get("error_description"),
      },
    })
      .then(setResult)
      .catch((err: unknown) => {
        if (err instanceof ApiError && err.status === 401) return; // api() is redirecting to /login
        setError(err);
      })
      // Drop the one-time code from the address bar and history.
      .finally(() => window.history.replaceState(null, "", "/instagram/callback"));
  }, [params]);

  if (error) {
    return (
      <div className="space-y-4" data-testid="oauth-error">
        <ErrorBox error={error} />
        <LinkButton href="/instagram">Instagram sahifasiga qaytish</LinkButton>
      </div>
    );
  }
  if (!result) return <Loading />;
  const { account, warnings } = result;
  return (
    <div className="space-y-4" data-testid="oauth-success">
      <Notice tone="success">
        Instagram akkaunt ulandi: <strong>@{account.username ?? account.ig_user_id}</strong>
      </Notice>
      {warnings.map((w) => (
        <Notice key={w} tone="warning">
          {w}
        </Notice>
      ))}
      <Card>
        <LinkButton href="/instagram" variant="primary">
          Instagram sahifasiga o‘tish
        </LinkButton>
      </Card>
    </div>
  );
}

export default function InstagramCallbackPage() {
  return (
    <>
      <PageHeader title="Instagram ulanishi" subtitle="Meta OAuth javobi tekshirilmoqda." />
      <Suspense fallback={<Loading />}>
        <Callback />
      </Suspense>
    </>
  );
}
