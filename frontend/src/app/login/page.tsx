"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState, type FormEvent } from "react";

import { Button, Field, Notice, inputClass } from "@/components/ui";
import { forgetMe } from "@/lib/api";

/**
 * Post-login target from ?next=. Only same-origin paths are allowed (no open redirect):
 * browsers treat `/\evil.com` or `/<TAB>/evil.com` as protocol-relative, so backslashes and
 * control characters are rejected outright and the result is re-checked with the URL parser.
 */
function safeNext(next: string | null): string {
  if (!next || !next.startsWith("/") || /[\\\u0000-\u001f\u007f]/.test(next)) return "/overview";
  try {
    const url = new URL(next, window.location.origin);
    const target = url.pathname + url.search + url.hash;
    // "/.//evil.com" normalises to "//evil.com": still protocol-relative, so refuse it too.
    if (url.origin !== window.location.origin || target.startsWith("//")) return "/overview";
    return target;
  } catch {
    return "/overview";
  }
}

function LoginForm() {
  const router = useRouter();
  const params = useSearchParams();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
        credentials: "same-origin",
      });
      if (!res.ok) {
        const data = await res.json().catch(() => null);
        setError(
          res.status === 401
            ? "Email yoki parol noto‘g‘ri."
            : (data?.error?.message ?? "Kirishda xato yuz berdi."),
        );
        return;
      }
      forgetMe();
      router.replace(safeNext(params.get("next")));
      router.refresh();
    } catch {
      setError("Server bilan aloqa yo‘q.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={submit} className="space-y-4" noValidate>
      {params.get("logout") === "failed" && (
        <Notice tone="warning">
          <span data-testid="logout-failed">
            Siz bu brauzerdan chiqdingiz, lekin serverda sessiyani bekor qilib bo‘lmadi. Xavfsizlik uchun qayta kirib, “Barcha qurilmalardan chiqish”ni bosing.
          </span>
        </Notice>
      )}
      <Field label="Email">
        <input
          className={inputClass}
          type="email"
          autoComplete="username"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </Field>
      <Field label="Parol">
        <input
          className={inputClass}
          type="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </Field>
      {error && (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      )}
      <Button type="submit" variant="primary" className="w-full" loading={loading}>
        Kirish
      </Button>
    </form>
  );
}

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-10">
      <div className="w-full max-w-sm rounded-2xl border border-border bg-card p-6 shadow-sm">
        <p className="text-[10px] font-medium uppercase tracking-[0.25em] text-muted">Muxriddin Design</p>
        <h1 className="mt-1 text-xl font-semibold">AI Instagram Manager</h1>
        <p className="mt-1 text-sm text-muted">Admin panelga kirish</p>
        <div className="mt-6">
          <Suspense>
            <LoginForm />
          </Suspense>
        </div>
        <p className="mt-6 text-xs text-muted">
          Bu yerda faqat panel paroli kiritiladi. Instagram paroli hech qachon so‘ralmaydi.
        </p>
      </div>
    </main>
  );
}
