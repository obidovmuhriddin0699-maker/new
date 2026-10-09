"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { BackendStatus } from "@/components/BackendStatus";
import { Button, Card, ErrorBox, Field, KeyValue, Loading, Notice, PageHeader, inputClass } from "@/components/ui";
import { api } from "@/lib/api";
import type { User } from "@/lib/types";
import { useApi } from "@/lib/useApi";

const ROLE: Record<User["role"], string> = { OWNER: "Egasi (OWNER)", ADMIN: "Administrator", VIEWER: "Kuzatuvchi (faqat o‘qish)" };

export default function SettingsPage() {
  const router = useRouter();
  const { data, error, loading } = useApi<User>("auth/me");

  async function logout() {
    await fetch("/api/auth/logout", { method: "POST", credentials: "same-origin" });
    router.replace("/login");
    router.refresh();
  }

  return (
    <>
      <PageHeader title="Sozlamalar" />
      <div className="space-y-4">
        <Card title="Hisob">
          {loading && <Loading />}
          <ErrorBox error={error} />
          {data && (
            <KeyValue
              items={[
                ["Email", <span key="e" data-testid="me-email">{data.email}</span>],
                ["Ism", data.full_name ?? "—"],
                ["Rol", ROLE[data.role]],
              ]}
            />
          )}
          <Button className="mt-4" onClick={logout} data-testid="logout">Chiqish</Button>
        </Card>
        <SecurityCard />
        <Notice>
          Sessiya xavfsiz httpOnly cookie’da saqlanadi va brauzer JavaScript’i uni o‘qiy olmaydi. Sessiya muddati tugasa, qayta kirish so‘raladi.
        </Notice>
        <BackendStatus />
      </div>
    </>
  );
}

function SecurityCard() {
  const router = useRouter();
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [busy, setBusy] = useState<"password" | "all" | null>(null);
  const [error, setError] = useState<unknown>(null);

  async function done() {
    // The backend has revoked every session, including this one.
    await fetch("/api/auth/logout", { method: "POST", credentials: "same-origin" });
    router.replace("/login");
    router.refresh();
  }

  async function changePassword(e: React.FormEvent) {
    e.preventDefault();
    setBusy("password");
    setError(null);
    try {
      await api("auth/change-password", { method: "POST", body: { current_password: current, new_password: next } });
      await done();
    } catch (err) {
      setError(err);
      setBusy(null);
    }
  }

  async function logoutAll() {
    setBusy("all");
    await fetch("/api/auth/logout?all=1", { method: "POST", credentials: "same-origin" });
    router.replace("/login");
    router.refresh();
  }

  return (
    <Card title="Xavfsizlik">
      <form className="space-y-3" onSubmit={changePassword} data-testid="password-form">
        <Field label="Joriy parol">
          <input type="password" autoComplete="current-password" className={inputClass} value={current} onChange={(e) => setCurrent(e.target.value)} required />
        </Field>
        <Field label="Yangi parol" hint="Kamida 12 belgi. O‘zgartirgandan keyin barcha qurilmalardan chiqib ketasiz.">
          <input type="password" autoComplete="new-password" minLength={12} className={inputClass} value={next} onChange={(e) => setNext(e.target.value)} required />
        </Field>
        <ErrorBox error={error} />
        <div className="flex flex-wrap gap-2">
          <Button type="submit" variant="primary" loading={busy === "password"}>Parolni o‘zgartirish</Button>
          <Button onClick={() => void logoutAll()} loading={busy === "all"} data-testid="logout-all">
            Barcha qurilmalardan chiqish
          </Button>
        </div>
      </form>
    </Card>
  );
}
