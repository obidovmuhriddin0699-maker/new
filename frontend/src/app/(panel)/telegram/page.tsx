import { Card, Notice, PageHeader } from "@/components/ui";

const COMMANDS = ["/start", "/content", "/plan", "/reels", "/story", "/status", "/approve", "/reject", "/analytics", "/settings"];

export default function TelegramPage() {
  return (
    <>
      <PageHeader title="Telegram" subtitle="Telegram bot orqali boshqaruv." />
      <div className="space-y-4">
        <Notice>Telegram bot PHASE 5 da qo‘shiladi. Tasdiqlash xavfsiz inline tugmalar orqali va faqat ruxsat berilgan Telegram ID’lar uchun bo‘ladi.</Notice>
        <Card title="Rejadagi buyruqlar">
          <div className="flex flex-wrap gap-2">
            {COMMANDS.map((c) => (
              <code key={c} className="rounded bg-background px-2 py-1 text-sm">{c}</code>
            ))}
          </div>
        </Card>
      </div>
    </>
  );
}
