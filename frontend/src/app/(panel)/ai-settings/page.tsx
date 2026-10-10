"use client";

import { Button, Card, ErrorBox, KeyValue, Loading, Notice, PageHeader } from "@/components/ui";
import type { AIStatus } from "@/lib/types";
import { useApi } from "@/lib/useApi";

export default function AISettingsPage() {
  const { data, error, loading, reload } = useApi<AIStatus>("ai/status");
  return (
    <>
      <PageHeader title="AI sozlamalari" subtitle="Provayder holati va agent ruxsatlari." actions={<Button onClick={() => void reload()} loading={loading}>Yangilash</Button>} />
      {loading && !data && <Loading />}
      <ErrorBox error={error} onRetry={reload} />
      {data && (
        <div className="space-y-4">
          <Card title="Matn modeli">
            <KeyValue
              items={[
                ["Provayder", data.text.provider],
                ["Model", data.text.model],
                ["Holat", data.text.available ? "Ishlayapti" : "Ishlamayapti"],
                ["Model o‘rnatilgan", data.text.model_installed ? "Ha" : "Yo‘q"],
                ["Xabar", data.text.message ?? "—"],
                ["Vazifa rejimi", data.jobs_mode === "sync" ? "sync (so‘rov ichida)" : "celery (fon rejimi)"],
              ]}
            />
          </Card>
          <Card title="Media provayderlar">
            <KeyValue items={data.media.map((m) => [m.kind === "image" ? "Rasm" : "Video", `${m.provider} — ${m.status}`])} />
          </Card>
          <Card title="AI agentlar va ruxsatlar">
            <KeyValue
              items={[
                ["Agentlar", data.agents.join(", ")],
                ["Ruxsatlar", data.agent_permissions.join(", ")],
                ["Nashr qilish", data.publishing_available ? "Ha" : "Yo‘q — AI hech qachon nashr qila olmaydi"],
              ]}
            />
          </Card>
          <Notice>
            Sozlamalar <code>.env</code> faylidan olinadi (masalan <code>AI_MODEL</code>, <code>AI_JOBS_MODE</code>). Maxfiy kalitlar panelda ko‘rsatilmaydi.
            Modelni almashtirish: <code>ollama pull &lt;model&gt;</code>, keyin <code>.env</code> da <code>AI_MODEL</code> ni o‘zgartirib backendni qayta ishga tushiring.
          </Notice>
        </div>
      )}
    </>
  );
}
