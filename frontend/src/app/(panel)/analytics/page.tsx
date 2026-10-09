"use client";

import { Card, ErrorBox, KeyValue, Loading, Notice, PageHeader } from "@/components/ui";
import type { DashboardSummary } from "@/lib/types";
import { useApi } from "@/lib/useApi";

export default function AnalyticsPage() {
  const { data, error, loading } = useApi<DashboardSummary>("dashboard/summary");
  return (
    <>
      <PageHeader title="Analitika" subtitle="Faqat Meta API qaytargan haqiqiy ko‘rsatkichlar." />
      {loading && <Loading />}
      <ErrorBox error={error} />
      {data && !data.analytics_available && (
        <Notice>
          Hozircha analitika ma’lumoti yo‘q. Instagram ulanmagan (PHASE 7) va insights sinxronizatsiyasi PHASE 9 da qo‘shiladi.
          Tizim ko‘rsatkichlarni taxmin qilmaydi yoki uydirmaydi.
        </Notice>
      )}
      {data?.analytics_available && (
        <Card title="Ko‘rsatkichlar">
          <KeyValue
            items={[
              ["Qamrov (reach)", data.reach ?? "—"],
              ["O‘rtacha engagement", data.engagement_rate === null ? "—" : `${(data.engagement_rate * 100).toFixed(2)}%`],
            ]}
          />
        </Card>
      )}
      {data && (
        <Card title="Kontent holatlari" className="mt-4">
          <KeyValue items={Object.entries(data.by_status).map(([k, v]) => [k, v])} />
        </Card>
      )}
    </>
  );
}
