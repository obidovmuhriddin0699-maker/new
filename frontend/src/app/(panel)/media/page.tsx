"use client";

import Link from "next/link";

import { Card, EmptyState, ErrorBox, Loading, Notice, PageHeader } from "@/components/ui";
import { formatDateTime } from "@/lib/format";
import type { AIStatus, Asset } from "@/lib/types";
import { useApi } from "@/lib/useApi";

type AssetItem = Asset & { content_id: number; provider: string | null; created_at: string };

export default function MediaPage() {
  const { data, error, loading, reload } = useApi<{ items: AssetItem[]; total: number }>("assets");
  const ai = useApi<AIStatus>("ai/status");
  const image = ai.data?.media.find((m) => m.kind === "image");

  return (
    <>
      <PageHeader title="Media kutubxona" subtitle="Kontentga biriktirilgan rasm va videolar." />
      {image && image.status !== "configured" && (
        <div className="mb-4">
          <Notice tone="warning">
            Rasm generatsiyasi provayderi sozlanmagan ({image.status}). Tizim soxta rasm yaratmaydi. Media’ni kontent sahifasida yuklang (JPEG / MP4) yoki ochiq HTTPS havola bering — Meta uni shu manzildan yuklab oladi.
          </Notice>
        </div>
      )}
      {loading && !data && <Loading />}
      <ErrorBox error={error} onRetry={reload} />
      {data && data.items.length === 0 && <EmptyState title="Media hali yo‘q" />}
      {data && data.items.length > 0 && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4" data-testid="asset-grid">
          {data.items.map((a) => (
            <Card key={a.id} className="p-3">
              <div className="flex aspect-square items-center justify-center overflow-hidden rounded-lg bg-background text-xs text-muted">
                {a.public_url ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={a.public_url} alt="" className="h-full w-full object-cover" />
                ) : (
                  <span className="p-2 text-center">Fayl yo‘q (faqat metadata)</span>
                )}
              </div>
              <p className="mt-2 text-xs">
                {a.kind} · {a.width ?? "?"}×{a.height ?? "?"}
              </p>
              <p className="text-xs text-muted">
                <Link href={`/content/${a.content_id}`} className="underline">Kontent #{a.content_id}</Link> · {a.provider ?? "—"}
              </p>
              <p className="text-xs text-muted">{formatDateTime(a.created_at)}</p>
            </Card>
          ))}
        </div>
      )}
    </>
  );
}
