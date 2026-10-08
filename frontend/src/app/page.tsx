import { BackendStatus } from "@/components/BackendStatus";

const PHASES = [
  { n: 0, title: "Architecture", done: true },
  { n: 1, title: "Project foundation", done: true },
  { n: 2, title: "Database", done: false },
  { n: 3, title: "AI Content Creator", done: false },
];

export default function Home() {
  return (
    <main className="mx-auto max-w-3xl px-4 py-10 sm:py-16">
      <header>
        <p className="text-xs font-medium uppercase tracking-[0.2em] text-muted">
          Muxriddin Design
        </p>
        <h1 className="mt-2 text-2xl font-semibold sm:text-3xl">AI Instagram Manager</h1>
        <p className="mt-2 text-sm text-muted">
          AI kontent tayyorlaydi — nashr qilish faqat sizning tasdig‘ingizdan keyin.
        </p>
      </header>

      <div className="mt-8 space-y-6">
        <BackendStatus />

        <section className="rounded-2xl border border-border bg-card p-5 shadow-sm">
          <h2 className="text-base font-semibold">Rivojlanish bosqichlari</h2>
          <ol className="mt-3 space-y-1.5 text-sm">
            {PHASES.map((p) => (
              <li key={p.n} className="flex gap-2">
                <span className={p.done ? "text-emerald-600" : "text-muted"}>
                  {p.done ? "✓" : "○"}
                </span>
                <span>
                  PHASE {p.n} — {p.title}
                </span>
              </li>
            ))}
          </ol>
        </section>
      </div>
    </main>
  );
}
