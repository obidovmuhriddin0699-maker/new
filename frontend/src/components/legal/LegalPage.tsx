import Link from "next/link";
import type { ReactNode } from "react";

export function legalInfo() {
  return {
    operator: process.env.LEGAL_OPERATOR_NAME || "MUXRIDDIN DESIGN",
    email: process.env.LEGAL_CONTACT_EMAIL || "",
    updated: process.env.LEGAL_LAST_UPDATED || "2026-10-09",
    site: process.env.PANEL_PUBLIC_URL || "",
  };
}

export function LegalPage({ title, children }: { title: string; children: ReactNode }) {
  const { operator, updated } = legalInfo();
  return (
    <main className="mx-auto max-w-3xl px-4 py-10 text-sm leading-relaxed sm:px-6">
      <header className="mb-8 border-b border-border pb-4">
        <p className="text-xs uppercase tracking-wide text-muted">{operator}</p>
        <h1 className="mt-1 text-2xl font-semibold">{title}</h1>
        <p className="mt-1 text-xs text-muted">Last updated / Oxirgi yangilanish: {updated}</p>
      </header>
      <div className="space-y-6 [&_h2]:text-base [&_h2]:font-semibold [&_li]:ml-5 [&_li]:list-disc [&_p]:mt-2">
        {children}
      </div>
      <footer className="mt-10 border-t border-border pt-4 text-xs text-muted">
        <Link href="/privacy" className="underline">Privacy Policy</Link> · <Link href="/terms" className="underline">Terms of Service</Link>
      </footer>
    </main>
  );
}

export function Contact() {
  const { email, operator } = legalInfo();
  return email ? (
    <a href={`mailto:${email}`} className="underline">{email}</a>
  ) : (
    <span>{operator}</span>
  );
}
