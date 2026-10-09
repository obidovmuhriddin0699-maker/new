"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";

const NAV: { href: string; label: string; group?: string }[] = [
  { href: "/overview", label: "Umumiy ko‘rinish" },
  { href: "/content", label: "Kontent navbati" },
  { href: "/ai", label: "AI Studio" },
  { href: "/calendar", label: "Kalendar" },
  { href: "/media", label: "Media kutubxona" },
  { href: "/instagram", label: "Instagram akkaunt", group: "Integratsiya" },
  { href: "/analytics", label: "Analitika" },
  { href: "/telegram", label: "Telegram" },
  { href: "/ai-settings", label: "AI sozlamalari", group: "Sozlamalar" },
  { href: "/brand", label: "Brend sozlamalari" },
  { href: "/logs", label: "Tizim loglari" },
  { href: "/settings", label: "Sozlamalar" },
];

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [open, setOpen] = useState(false);

  useEffect(() => setOpen(false), [pathname]);

  async function logout() {
    await fetch("/api/auth/logout", { method: "POST", credentials: "same-origin" });
    router.replace("/login");
    router.refresh();
  }

  const nav = (
    <nav aria-label="Asosiy menyu" className="flex flex-col gap-0.5 text-sm">
      {NAV.map((item) => {
        const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
        return (
          <div key={item.href}>
            {item.group && (
              <p className="mb-1 mt-4 px-3 text-xs font-medium uppercase tracking-wider text-muted">{item.group}</p>
            )}
            <Link
              href={item.href}
              aria-current={active ? "page" : undefined}
              className={`block rounded-lg px-3 py-2 ${active ? "bg-accent text-accent-fg" : "hover:bg-background"}`}
            >
              {item.label}
            </Link>
          </div>
        );
      })}
      <button type="button" onClick={logout} className="mt-6 rounded-lg px-3 py-2 text-left text-muted hover:bg-background">
        Chiqish
      </button>
    </nav>
  );

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[15rem_1fr]">
      <aside className="hidden border-r border-border bg-card p-4 lg:block">
        <Brand />
        <div className="mt-6">{nav}</div>
      </aside>

      <div className="sticky top-0 z-30 flex items-center justify-between border-b border-border bg-card/95 px-4 py-3 backdrop-blur lg:hidden">
        <Brand />
        <button
          type="button"
          aria-label="Menyuni ochish"
          aria-expanded={open}
          onClick={() => setOpen(true)}
          className="rounded-lg border border-border px-3 py-2 text-sm"
        >
          Menyu
        </button>
      </div>

      {open && (
        <div className="fixed inset-0 z-40 lg:hidden" role="dialog" aria-modal="true" aria-label="Menyu">
          <button type="button" aria-label="Yopish" className="absolute inset-0 bg-black/40" onClick={() => setOpen(false)} />
          <div className="absolute inset-y-0 left-0 w-72 max-w-[85vw] overflow-y-auto bg-card p-4 shadow-xl">
            <div className="flex items-center justify-between">
              <Brand />
              <button type="button" onClick={() => setOpen(false)} className="rounded-lg px-2 py-1 text-sm text-muted">
                Yopish
              </button>
            </div>
            <div className="mt-6">{nav}</div>
          </div>
        </div>
      )}

      <main className="mx-auto w-full min-w-0 max-w-6xl px-4 py-6 sm:px-6 lg:py-8">{children}</main>
    </div>
  );
}

function Brand() {
  return (
    <Link href="/overview" className="block leading-tight">
      <span className="block text-[10px] font-medium uppercase tracking-[0.25em] text-muted">Muxriddin Design</span>
      <span className="block text-sm font-semibold">AI Instagram Manager</span>
    </Link>
  );
}
