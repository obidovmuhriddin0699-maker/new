"use client";

import { useRouter } from "next/navigation";

import { BackendStatus } from "@/components/BackendStatus";
import { Button, Card, ErrorBox, KeyValue, Loading, Notice, PageHeader } from "@/components/ui";
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
        <Notice>
          Sessiya xavfsiz httpOnly cookie’da saqlanadi va brauzer JavaScript’i uni o‘qiy olmaydi. Sessiya muddati tugasa, qayta kirish so‘raladi.
        </Notice>
        <BackendStatus />
      </div>
    </>
  );
}
