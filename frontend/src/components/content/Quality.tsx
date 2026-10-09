"use client";

import type { QualityReport } from "@/lib/types";

const SEV: Record<string, string> = {
  ERROR: "text-red-700 dark:text-red-300",
  WARNING: "text-amber-700 dark:text-amber-300",
  INFO: "text-muted",
};
const SEV_LABEL: Record<string, string> = { ERROR: "Xato", WARNING: "Ogohlantirish", INFO: "Ma’lumot" };

export function QualityView({ report }: { report: QualityReport }) {
  return (
    <div className="space-y-3 text-sm" data-testid="quality-report">
      <p>
        <span className={`font-semibold ${report.passed ? "text-emerald-700 dark:text-emerald-300" : "text-red-700 dark:text-red-300"}`}>
          {report.passed ? "Tekshiruvdan o‘tdi" : "Tuzatish kerak"}
        </span>
        <span className="text-muted"> · ball {report.score}/100</span>
      </p>
      {report.findings.length === 0 ? (
        <p className="text-muted">Muammo topilmadi.</p>
      ) : (
        <ul className="space-y-2">
          {report.findings.map((f, i) => (
            <li key={i} className="rounded-lg border border-border p-2">
              <p className={SEV[f.severity]}>
                <span className="font-medium">{SEV_LABEL[f.severity]}</span> · {f.field} — {f.message}
              </p>
              {f.suggestion && <p className="mt-0.5 text-muted">Taklif: {f.suggestion}</p>}
            </li>
          ))}
        </ul>
      )}
      <p className="text-xs text-muted">{report.disclaimer}</p>
    </div>
  );
}
