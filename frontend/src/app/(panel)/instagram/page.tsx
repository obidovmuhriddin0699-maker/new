import { Card, KeyValue, Notice, PageHeader } from "@/components/ui";

export default function InstagramPage() {
  return (
    <>
      <PageHeader title="Instagram akkaunt" subtitle="Rasmiy Meta API orqali ulanish." />
      <div className="space-y-4">
        <Card title="Holat">
          <KeyValue
            items={[
              ["Ulanish", <span key="s" data-testid="instagram-status">Ulanmagan</span>],
              ["Usul", "Instagram API with Instagram Login (default)"],
              ["Token saqlash", "Faqat shifrlangan (Fernet)"],
            ]}
          />
          <button
            type="button"
            disabled
            className="mt-4 min-h-10 cursor-not-allowed rounded-lg border border-dashed border-border px-4 py-2 text-sm text-muted"
          >
            Instagram’ni ulash — PHASE 7
          </button>
        </Card>
        <Notice>
          Instagram login yoki paroli hech qachon so‘ralmaydi va saqlanmaydi. Ulanish faqat Meta OAuth orqali bo‘ladi;
          ruxsatlar va App Review talablari PHASE 7 da rasmiy Meta hujjatlari asosida tekshiriladi.
        </Notice>
      </div>
    </>
  );
}
