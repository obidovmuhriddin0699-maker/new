import { useCallback, useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { ApiError, api } from "./api";
import type { Billing, CurrentUser, Plan, Workflow } from "./api";

type Panel = "overview" | "ai" | "orchestrator" | "billing" | "telegram";
type ChatMessage = { role: "user" | "assistant"; content: string; model?: string };

const panels: { id: Panel; title: string; icon: string }[] = [
  { id: "overview", title: "Umumiy", icon: "◫" },
  { id: "ai", title: "AI chat", icon: "✳" },
  { id: "orchestrator", title: "Orchestrator", icon: "⌘" },
  { id: "billing", title: "Tarif va limitlar", icon: "◇" },
  { id: "telegram", title: "Telegram bot", icon: "➤" },
];

function formatDate(timestamp: number) {
  return new Date(timestamp * 1000).toLocaleDateString("uz-UZ", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function App() {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [activePanel, setActivePanel] = useState<Panel>("overview");
  const [workspaceId, setWorkspaceId] = useState("");
  const [billing, setBilling] = useState<Billing | null>(null);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [busy, setBusy] = useState(false);
  const [initializing, setInitializing] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [workspaceName, setWorkspaceName] = useState("");
  const [prompt, setPrompt] = useState("");
  const [workflowTitle, setWorkflowTitle] = useState("");
  const [workflowTask, setWorkflowTask] = useState("");
  const [showWorkspaceForm, setShowWorkspaceForm] = useState(false);

  const activeWorkspace = useMemo(
    () => user?.workspaces.find((workspace) => workspace.id === workspaceId) ?? null,
    [user, workspaceId],
  );

  const refreshUser = useCallback(async () => {
    const profile = await api.me();
    setUser(profile);
    setWorkspaceId((current) =>
      profile.workspaces.some((workspace) => workspace.id === current)
        ? current
        : profile.active_workspace_id &&
            profile.workspaces.some((workspace) => workspace.id === profile.active_workspace_id)
          ? profile.active_workspace_id
          : (profile.workspaces[0]?.id ?? ""),
    );
    return profile;
  }, []);

  useEffect(() => {
    api.me()
      .then((profile) => {
        setUser(profile);
        setWorkspaceId(
          profile.active_workspace_id &&
            profile.workspaces.some((workspace) => workspace.id === profile.active_workspace_id)
            ? profile.active_workspace_id
            : (profile.workspaces[0]?.id ?? ""),
        );
      })
      .catch((reason: unknown) => {
        if (reason instanceof Error && !(reason instanceof ApiError && reason.status === 401)) {
          setError(reason.message);
        }
      })
      .finally(() => setInitializing(false));
  }, []);

  const loadWorkspaceData = useCallback(async () => {
    if (!workspaceId) {
      setBilling(null);
      setPlans([]);
      setWorkflows([]);
      return;
    }
    const [billingData, planData, workflowData] = await Promise.all([
      api.billing(workspaceId),
      api.plans(workspaceId),
      api.workflows(workspaceId),
    ]);
    setBilling(billingData);
    setPlans(planData);
    setWorkflows(workflowData);
  }, [workspaceId]);

  useEffect(() => {
    if (!user || !workspaceId) return;
    loadWorkspaceData().catch((reason: unknown) => {
      setError(reason instanceof Error ? reason.message : "Ma’lumotlarni yuklab bo‘lmadi");
    });
  }, [loadWorkspaceData, user, workspaceId]);

  async function runAction(action: () => Promise<void>) {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await action();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Kutilmagan xatolik yuz berdi");
    } finally {
      setBusy(false);
    }
  }

  async function submitAuth(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await runAction(async () => {
      if (authMode === "register") await api.register(email, password);
      else await api.login(email, password);
      const profile = await refreshUser();
      setPassword("");
      setNotice(
        profile.workspaces.length
          ? "Xush kelibsiz. Workspace tanlang."
          : "Hisob tayyor. Boshlash uchun workspace yarating.",
      );
    });
  }

  async function createWorkspace(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await runAction(async () => {
      const created = await api.createWorkspace(workspaceName);
      setWorkspaceName("");
      const profile = await refreshUser();
      setWorkspaceId(created.id);
      setUser(profile);
      setShowWorkspaceForm(false);
      setNotice("Workspace yaratildi.");
    });
  }

  async function switchWorkspace(id: string) {
    if (!id || id === workspaceId) return;
    await runAction(async () => {
      await api.selectWorkspace(id);
      setWorkspaceId(id);
      setMessages([]);
      setNotice("Workspace almashtirildi.");
    });
  }

  async function logout() {
    await runAction(async () => {
      await api.logout();
      setUser(null);
      setWorkspaceId("");
      setBilling(null);
      setPlans([]);
      setWorkflows([]);
      setMessages([]);
      setNotice("");
    });
  }

  async function submitChat(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!workspaceId || !prompt.trim()) return;
    const userPrompt = prompt.trim();
    setPrompt("");
    setMessages((current) => [...current, { role: "user", content: userPrompt }]);
    await runAction(async () => {
      const result = await api.chat(workspaceId, userPrompt);
      setMessages((current) => [
        ...current,
        { role: "assistant", content: result.response, model: result.model },
      ]);
    });
  }

  async function createWorkflow(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!workspaceId) return;
    await runAction(async () => {
      const workflow = await api.createWorkflow(workspaceId, workflowTitle, workflowTask);
      setWorkflowTitle("");
      setWorkflowTask("");
      setWorkflows((current) => [workflow, ...current]);
      setNotice("Workflow navbatga qo‘shildi.");
    });
  }

  async function runWorkflow(workflowId: string) {
    await runAction(async () => {
      try {
        const workflow = await api.runWorkflow(workspaceId, workflowId);
        setWorkflows((current) => [
          workflow,
          ...current.filter((item) => item.id !== workflow.id),
        ]);
        setNotice("Workflow bajarildi.");
      } catch (reason) {
        await loadWorkspaceData();
        throw reason;
      }
      await loadWorkspaceData();
    });
  }

  async function checkout(planId: string) {
    await runAction(async () => {
      const result = await api.checkout(workspaceId, planId);
      setNotice(
        result.simulated
          ? "Test checkout muvaffaqiyatli. Haqiqiy to‘lov amalga oshirilmadi."
          : "Tarif yangilandi.",
      );
      await loadWorkspaceData();
    });
  }

  if (initializing) {
    return <div className="splash"><span className="brand-mark">✳</span><p>Panel yuklanmoqda…</p></div>;
  }

  if (!user) {
    return (
      <main className="auth-shell">
        <section className="auth-aside">
          <div className="brand"><span className="brand-mark">✳</span> mahalliy<span className="brand-muted">.ai</span></div>
          <div className="auth-pitch">
            <p className="eyebrow">LOKAL AI WORKSPACE</p>
            <h1>G‘oyadan natijagacha — bitta joyda.</h1>
            <p>O‘z modelingiz, workspace’ingiz va ketma-ket AI ish jarayoningiz.</p>
            <div className="pitch-tags"><span>Maxfiylik sizning qo‘lingizda</span><span>Ollama bilan lokal</span></div>
          </div>
          <span className="aside-foot">Sizning AI. Sizning infratuzilmangiz.</span>
        </section>
        <section className="auth-main">
          <div className="auth-card">
            <p className="eyebrow">BOSHLASH</p>
            <h2>{authMode === "login" ? "Xush kelibsiz" : "Hisob yarating"}</h2>
            <p className="muted">Davom etish uchun ma’lumotlaringizni kiriting.</p>
            {error && <div className="alert error" role="alert">{error}</div>}
            {notice && <div className="alert success" role="status">{notice}</div>}
            <form onSubmit={submitAuth} className="stack-form">
              <label>Email manzil<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required autoComplete="email" placeholder="siz@misol.uz" /></label>
              <label>Parol<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required minLength={8} maxLength={128} autoComplete={authMode === "login" ? "current-password" : "new-password"} placeholder="Kamida 8 ta belgi" /></label>
              <button className="button primary full" disabled={busy}>{busy ? "Kuting…" : authMode === "login" ? "Kirish" : "Hisob yaratish"}<span>↗</span></button>
            </form>
            <p className="auth-switch">
              {authMode === "login" ? "Hisobingiz yo‘qmi?" : "Hisobingiz bormi?"}{" "}
              <button className="link-button" onClick={() => { setAuthMode(authMode === "login" ? "register" : "login"); setError(""); }}>
                {authMode === "login" ? "Ro‘yxatdan o‘tish" : "Kirish"}
              </button>
            </p>
            <p className="local-note"><span className="status-dot" /> Sessiyalar xavfsiz cookie orqali boshqariladi</p>
          </div>
        </section>
      </main>
    );
  }

  if (!user.workspaces.length || !workspaceId) {
    return (
      <main className="onboarding-shell">
        <header className="topbar"><div className="brand"><span className="brand-mark">✳</span> mahalliy<span className="brand-muted">.ai</span></div><button className="button ghost" onClick={logout}>Chiqish</button></header>
        <section className="onboarding-card">
          <div className="onboarding-icon">⌂</div>
          <p className="eyebrow">1-QADAM · WORKSPACE</p>
          <h1>Ish joyingizni yarating</h1>
          <p className="muted">Workspace jamoangiz, billing’ingiz va AI ishlaringizni bir joyda saqlaydi.</p>
          {error && <div className="alert error" role="alert">{error}</div>}
          <form onSubmit={createWorkspace} className="stack-form">
            <label>Workspace nomi<input value={workspaceName} onChange={(event) => setWorkspaceName(event.target.value)} required maxLength={100} placeholder="Masalan, Mahalliy AI Studio" /></label>
            <button className="button primary full" disabled={busy}>{busy ? "Yaratilmoqda…" : "Workspace yaratish"}<span>↗</span></button>
          </form>
        </section>
      </main>
    );
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">✳</span> mahalliy<span className="brand-muted">.ai</span></div>
        <div className="side-label">WORKSPACE</div>
        <div className="workspace-select-wrap">
          <span className="workspace-avatar">{activeWorkspace?.name.slice(0, 1).toUpperCase()}</span>
          <select aria-label="Workspace tanlang" value={workspaceId} onChange={(event) => void switchWorkspace(event.target.value)}>
            {user.workspaces.map((workspace) => <option key={workspace.id} value={workspace.id}>{workspace.name}</option>)}
          </select>
          <span className="select-caret">⌄</span>
        </div>
        <button className="add-workspace-button" onClick={() => { setShowWorkspaceForm(true); setError(""); }}>＋ Yangi workspace</button>
        <div className="side-label nav-label">PLATFORM</div>
        <nav className="nav-list" aria-label="Asosiy navigatsiya">
          {panels.map((panel) => (
            <button key={panel.id} className={`nav-item ${activePanel === panel.id ? "active" : ""}`} onClick={() => { setActivePanel(panel.id); setError(""); }}>
              <span className="nav-icon">{panel.icon}</span>{panel.title}
              {panel.id === "orchestrator" && <span className="nav-count">{workflows.length}</span>}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="connection-card"><span className="status-dot" /><div><strong>Lokal AI</strong><small>Model API sozlamada</small></div><span className="connection-chevron">↗</span></div>
          <div className="profile-row"><div className="profile-avatar">{user.email.slice(0, 1).toUpperCase()}</div><div className="profile-copy"><strong>{user.email}</strong><small>{activeWorkspace?.role ?? "member"}</small></div><button className="icon-button" title="Chiqish" aria-label="Chiqish" onClick={logout}>↪</button></div>
        </div>
      </aside>

      <main className="main-area">
        <header className="page-top">
          <div className="breadcrumbs"><span>Workspace</span><b>/</b><strong>{panels.find((panel) => panel.id === activePanel)?.title}</strong></div>
          <div className="top-actions"><span className="secure-pill"><span className="status-dot" /> Lokal muhit</span><button className="avatar-small" title={user.email}>{user.email.slice(0, 1).toUpperCase()}</button></div>
        </header>
        <div className="page-content">
          {(error || notice) && <div className={`alert ${error ? "error" : "success"} page-alert`} role={error ? "alert" : "status"}>{error || notice}<button aria-label="Xabarni yopish" onClick={() => { setError(""); setNotice(""); }}>×</button></div>}
          {!activeWorkspace ? (
            <EmptyState title="Workspace topilmadi" body="Yangi workspace yarating yoki a’zolikni tekshiring." action={<button className="button primary" onClick={() => setUser({ ...user, workspaces: [] })}>Workspace yaratish</button>} />
          ) : activePanel === "overview" ? (
            <Overview user={user} workspaceName={activeWorkspace.name} billing={billing} workflows={workflows} onNavigate={setActivePanel} />
          ) : activePanel === "billing" ? (
            <BillingPanel billing={billing} plans={plans} busy={busy} onCheckout={checkout} />
          ) : activePanel === "ai" ? (
            <ChatPanel messages={messages} prompt={prompt} setPrompt={setPrompt} busy={busy} onSubmit={submitChat} />
          ) : activePanel === "telegram" ? (
            <TelegramPanel busy={busy} runAction={runAction} />
          ) : (
            <OrchestratorPanel workflows={workflows} title={workflowTitle} task={workflowTask} setTitle={setWorkflowTitle} setTask={setWorkflowTask} busy={busy} onCreate={createWorkflow} onRun={runWorkflow} />
          )}
        </div>
      </main>
      {showWorkspaceForm && <div className="modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setShowWorkspaceForm(false); }}><section className="modal-card" role="dialog" aria-modal="true" aria-labelledby="new-workspace-title"><button className="modal-close" aria-label="Yopish" onClick={() => setShowWorkspaceForm(false)}>×</button><p className="eyebrow">WORKSPACE</p><h2 id="new-workspace-title">Yangi ish joyi</h2><p className="muted">Yangi loyiha uchun alohida workspace yarating.</p>{error && <div className="alert error" role="alert">{error}</div>}<form onSubmit={createWorkspace} className="stack-form"><label>Workspace nomi<input value={workspaceName} onChange={(event) => setWorkspaceName(event.target.value)} required maxLength={100} placeholder="Masalan, Tajriba loyihasi" /></label><button className="button primary full" disabled={busy}>{busy ? "Yaratilmoqda…" : "Yaratish"}<span>↗</span></button></form></section></div>}
    </div>
  );
}

function TelegramPanel({ busy, runAction }: {
  busy: boolean;
  runAction: (action: () => Promise<void>) => Promise<void>;
}) {
  const [status, setStatus] = useState<{ linked: boolean; workspace_id: string | null } | null>(null);
  const [code, setCode] = useState<{ code: string; expires_at: number; bot_username: string | null } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const refresh = useCallback(async () => setStatus(await api.telegramStatus()), []);
  useEffect(() => {
    refresh().catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "Bog‘lanish holati yuklanmadi")).finally(() => setLoading(false));
  }, [refresh]);

  async function generateCode() {
    setError("");
    try {
      setCode(await api.createTelegramLinkCode());
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Kod yaratilmadi");
    }
  }

  async function unlink() {
    await runAction(async () => {
      await api.unlinkTelegram();
      setCode(null);
      setStatus({ linked: false, workspace_id: null });
    });
  }

  return (
    <>
      <PageHeading eyebrow="BOT INTEGRATION" title="Telegram bot" body="Telegram hisobingizni bir martalik kod bilan xavfsiz bog‘lang. Bot faqat private chat’da ishlaydi." />
      {error && <div className="alert error" role="alert">{error}</div>}
      {loading ? <div className="empty-card"><strong>Bog‘lanish holati yuklanmoqda…</strong></div> : status?.linked ? (
        <section className="telegram-card"><div className="telegram-card-icon">➤</div><div className="telegram-info"><p className="eyebrow">TELEGRAM HISOBI</p><h2>Bog‘langan</h2><p className="muted">{status.workspace_id ? `Tanlangan workspace: ${status.workspace_id}` : "Bot ichida /workspaces orqali workspace tanlang."}</p></div><button className="button secondary" disabled={busy} onClick={() => void unlink()}>{busy ? "Uzilmoqda…" : "Bog‘lanishni uzish"}</button></section>
      ) : (
        <section className="telegram-card link-card"><div className="telegram-card-icon">➤</div><div className="telegram-info"><p className="eyebrow">BIR MARTALIK BOG‘LANISH</p><h2>Telegram’ni ulang</h2><p className="muted">Kodni oling va Telegram botga <code>/link KOD</code> yuboring. Kod 10 daqiqada tugaydi va bir marta ishlatiladi.</p>{code ? <><div className="telegram-code"><code>{code.code}</code><span>{new Date(code.expires_at * 1000).toLocaleTimeString("uz-UZ", { hour: "2-digit", minute: "2-digit" })} gacha amal qiladi</span></div><button className="button secondary new-code-button" disabled={busy} onClick={() => void generateCode()}>Yangi kod yaratish</button></> : <button className="button primary" disabled={busy} onClick={() => void generateCode()}>{busy ? "Tayyorlanmoqda…" : "Bog‘lanish kodi yaratish"}<span>↗</span></button>}{code?.bot_username && <p className="bot-username">Bot: @{code.bot_username}</p>}</div></section>
      )}
      <div className="telegram-steps"><p className="eyebrow">QANDAY ISHLAYDI</p><ol><li>Mahalliy sozlamada `TELEGRAM_BOT_TOKEN` ni BotFather bergan token bilan kiriting.</li><li>Polling botni alohida terminalda `python -m backend.telegram_bot` bilan ishga tushiring.</li><li>Yuqoridagi kodni botga yuboring, so‘ng `/workspaces` va `/use ID` bilan workspace tanlang.</li><li>Matnli xabar yuboring; AI so‘rovlari workspace quota’sidan hisoblanadi.</li></ol><div className="safety-note"><span>ⓘ</span> Tokenni chatga yoki kodga yozmang. Faqat lokal environment variable sifatida saqlang. Bot buyruq bajarmaydi va faylga yozmaydi.</div></div>
    </>
  );
}

function Overview({ user, workspaceName, billing, workflows, onNavigate }: {
  user: CurrentUser;
  workspaceName: string;
  billing: Billing | null;
  workflows: Workflow[];
  onNavigate: (panel: Panel) => void;
}) {
  const trialDays = billing ? Math.max(0, Math.ceil((billing.trial_ends_at - Date.now() / 1000) / 86_400)) : 0;
  return (
    <>
      <div className="welcome-row"><div><p className="eyebrow">WORKSPACE OVERVIEW</p><h1>Salom, {user.email.split("@")[0]} <span className="wave">✳</span></h1><p className="muted">AI ishlaringizni shu yerdan boshqaring.</p></div><span className="date-chip">{new Date().toLocaleDateString("uz-UZ", { day: "numeric", month: "long", year: "numeric" })}</span></div>
      <section className="hero-card"><div className="hero-copy"><span className="hero-kicker">SIZNING AI MUHITINGIZ</span><h2>{workspaceName}</h2><p>Mahalliy model bilan xavfsiz suhbat va bosqichma-bosqich ish jarayonlari.</p><button className="button light" onClick={() => onNavigate("ai")}>AI bilan suhbat <span>↗</span></button></div><div className="hero-art" aria-hidden="true"><div className="orbit orbit-one" /><div className="orbit orbit-two" /><div className="orbit-core">✳</div><span className="orbit-dot dot-one" /><span className="orbit-dot dot-two" /><span className="orbit-dot dot-three" /></div></section>
      <div className="section-heading"><div><p className="eyebrow">HOLAT</p><h2>Workspace ko‘rinishi</h2></div><button className="text-action" onClick={() => onNavigate("billing")}>Billing’ni ko‘rish <span>→</span></button></div>
      <div className="stats-grid">
        <article className="stat-card"><div className="stat-top"><span>Hisob</span><span className="stat-icon violet">◉</span></div><strong className="stat-value">Faol</strong><small>{user.email}</small><div className="stat-foot"><span className="status-dot" /> Himoyalangan sessiya</div></article>
        <article className="stat-card"><div className="stat-top"><span>Tarif holati</span><span className="stat-icon green">◇</span></div><strong className="stat-value capitalize">{billing?.status ?? "Yuklanmoqda"}</strong><small>{billing?.plan?.name ?? "Boshlang‘ich sinov tarifi"}</small><div className="stat-foot">{billing?.status === "trialing" ? `${trialDays} kun sinov muddati qoldi` : "Tarif tafsilotlari"}</div></article>
        <article className="stat-card"><div className="stat-top"><span>AI workflows</span><span className="stat-icon blue">⌘</span></div><strong className="stat-value">{workflows.length}</strong><small>Jami workspace jarayonlari</small><div className="stat-foot"><button className="inline-link" onClick={() => onNavigate("orchestrator")}>Orchestrator’ni ochish →</button></div></article>
      </div>
      <div className="section-heading section-heading-tight"><div><p className="eyebrow">TEZKOR BOSHLASH</p><h2>Keyingi qadamingiz</h2></div></div>
      <div className="quick-grid"><button className="quick-card" onClick={() => onNavigate("ai")}><span className="quick-icon violet">✳</span><span><strong>AI chat</strong><small>Mahalliy modelga savol bering</small></span><b>↗</b></button><button className="quick-card" onClick={() => onNavigate("orchestrator")}><span className="quick-icon blue">⌘</span><span><strong>Workflow yarating</strong><small>Planner → Developer → QA</small></span><b>↗</b></button></div>
    </>
  );
}

function BillingPanel({ billing, plans, busy, onCheckout }: {
  billing: Billing | null;
  plans: Plan[];
  busy: boolean;
  onCheckout: (id: string) => Promise<void>;
}) {
  const days = billing ? Math.max(0, Math.ceil((billing.trial_ends_at - Date.now() / 1000) / 86_400)) : 0;
  const metrics = billing
    ? [...new Set([...Object.keys(billing.plan?.limits ?? {}), "ai_requests"])]
    : [];
  return (
    <>
      <PageHeading eyebrow="WORKSPACE BILLING" title="Tarif va limitlar" body="Sinov muddati, amaldagi tarif va sozlangan reja limitlari." />
      <section className="billing-summary">
        <div><span className="summary-label">JORIY HOLAT</span><h2 className="capitalize">{billing?.status ?? "Yuklanmoqda"}</h2><p className="muted">{billing?.status === "trialing" ? `Sinov muddati ${formatDate(billing.trial_ends_at)} gacha · ${days} kun qoldi` : billing?.plan ? billing.plan.name : "Hozircha pullik tarif tanlanmagan"}</p></div>
        <div className={`billing-badge ${billing?.status === "active" ? "active" : ""}`}><span className="status-dot" />{billing?.plan?.name ?? "30 kunlik sinov"}</div>
      </section>
      {billing && <section className="usage-card"><div className="usage-title"><div><p className="eyebrow">JORIY 30 KUNLIK DAVR</p><h2>Foydalanish</h2></div><span>{metrics.length} metrik</span></div>{metrics.map((metric) => { const used = billing.usage[metric] ?? 0; const limit = billing.plan?.limits[metric]; const percent = limit ? Math.min(100, (used / limit) * 100) : 0; return <div className="usage-row" key={metric}><div><strong>{metric.replaceAll("_", " ")}</strong><span>{limit === undefined ? `${used.toLocaleString("uz-UZ")} ishlatildi · limit belgilanmagan` : `${used.toLocaleString("uz-UZ")} / ${limit.toLocaleString("uz-UZ")}`}</span></div>{limit !== undefined && <div className="usage-track"><span style={{ width: `${percent}%` }} /></div>}</div>; })}</section>}
      <div className="section-heading"><div><p className="eyebrow">TARIF KATALOGI</p><h2>Mavjud rejalar</h2></div></div>
      {!plans.length ? <div className="empty-card"><div className="empty-icon">◇</div><strong>Hozircha tariflar sozlanmagan</strong><p>Administrator backend’da `BILLING_PLANS_JSON` orqali tarif katalogini kiritishi mumkin. Trial davrida hozir foydalanishni davom ettiring.</p></div> : <div className="plan-grid">{plans.map((plan) => <article className={`plan-card ${billing?.plan?.id === plan.id ? "selected" : ""}`} key={plan.id}><div className="plan-head"><span className="plan-icon">◇</span>{billing?.plan?.id === plan.id && <span className="current-tag">JORIY</span>}</div><h3>{plan.name}</h3><div className="plan-price">{(plan.price_minor / 100).toLocaleString("uz-UZ")} <span>{plan.currency}</span></div><small className="muted">oylik tarif</small><div className="plan-limits"><span className="side-label">LIMITLAR</span>{Object.entries(plan.limits).length ? Object.entries(plan.limits).map(([metric, limit]) => <div className="limit-row" key={metric}><span>{metric.replaceAll("_", " ")}</span><strong>{limit.toLocaleString("uz-UZ")}</strong></div>) : <p className="muted">Maxsus limit belgilanmagan</p>}</div><button className={`button ${billing?.plan?.id === plan.id ? "secondary" : "primary"} full`} disabled={busy || billing?.plan?.id === plan.id} onClick={() => void onCheckout(plan.id)}>{billing?.plan?.id === plan.id ? "Tanlangan" : busy ? "Kuting…" : "Test rejada tanlash"}</button><small className="demo-note">Simulyatsiya · haqiqiy to‘lov yo‘q</small></article>)}</div>}
      <div className="notice-card"><span>ⓘ</span><p>Tarif tanlash hozircha faqat test adapter’da simulyatsiya qilinadi. To‘lov provayderi ulanmagan va pul yechilmaydi.</p></div>
    </>
  );
}

function ChatPanel({ messages, prompt, setPrompt, busy, onSubmit }: {
  messages: ChatMessage[];
  prompt: string;
  setPrompt: (value: string) => void;
  busy: boolean;
  onSubmit: (event: FormEvent<HTMLFormElement>) => Promise<void>;
}) {
  return (
    <>
      <PageHeading eyebrow="LOCAL MODEL" title="AI chat" body="Workspace’ingiz uchun sozlangan mahalliy Ollama model bilan suhbat." />
      <section className="chat-card">
        <div className="chat-toolbar"><div className="model-avatar">✳</div><div><strong>Mahalliy yordamchi</strong><small><span className="status-dot" /> Ollama · backend konfiguratsiyasi</small></div><span className="local-label">LOKAL</span></div>
        <div className="chat-messages" aria-live="polite">
          {!messages.length && <div className="chat-welcome"><div className="chat-welcome-icon">✳</div><h3>Nimadan boshlaymiz?</h3><p>Savolingizni yozing. Suhbat tanlangan workspace’ning AI limitidan foydalanadi.</p><div className="prompt-chips"><button onClick={() => setPrompt("Lokal AI loyiham uchun xavfsiz API arxitekturasini taklif qil")}>API arxitekturasini rejalash <span>↗</span></button><button onClick={() => setPrompt("Ushbu kodni ko‘rib chiqish uchun test strategiyasini taklif qil")}>Test strategiyasi <span>↗</span></button></div></div>}
          {messages.map((message, index) => <div className={`message-row ${message.role}`} key={`${index}-${message.role}`}><div className="message-avatar">{message.role === "assistant" ? "✳" : "S"}</div><div className="message-bubble"><div className="message-meta">{message.role === "assistant" ? `Mahalliy AI${message.model ? ` · ${message.model}` : ""}` : "Siz"}</div><p>{message.content}</p></div></div>)}
          {busy && <div className="message-row assistant"><div className="message-avatar">✳</div><div className="message-bubble"><div className="message-meta">Mahalliy AI</div><p className="thinking">Javob tayyorlanmoqda <span>•••</span></p></div></div>}
        </div>
        <form className="chat-input-area" onSubmit={onSubmit}><textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} maxLength={16_000} rows={2} placeholder="Xabaringizni yozing…" disabled={busy} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); event.currentTarget.form?.requestSubmit(); } }} /><div className="chat-input-footer"><span>Enter — yuborish · Shift+Enter — yangi qator</span><button className="send-button" disabled={busy || !prompt.trim()} aria-label="Xabarni yuborish">↑</button></div></form>
      </section>
    </>
  );
}

function OrchestratorPanel({ workflows, title, task, setTitle, setTask, busy, onCreate, onRun }: {
  workflows: Workflow[];
  title: string;
  task: string;
  setTitle: (value: string) => void;
  setTask: (value: string) => void;
  busy: boolean;
  onCreate: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  onRun: (id: string) => Promise<void>;
}) {
  return (
    <>
      <PageHeading eyebrow="SEQUENTIAL AI WORKFLOW" title="Orchestrator" body="Vazifani Planner → Developer → QA bosqichlarida ko‘rib chiqing. Natijalar workspace’da saqlanadi." />
      <div className="orchestrator-layout">
        <section className="panel-card workflow-create">
          <div className="card-heading"><div><span className="section-icon blue">⌘</span><div><h2>Yangi workflow</h2><p>Vazifani aniq va qisqa yozing.</p></div></div></div>
          <div className="phase-preview"><PhasePill name="Planner" number="01" /><span className="phase-arrow">→</span><PhasePill name="Developer" number="02" /><span className="phase-arrow">→</span><PhasePill name="QA" number="03" /></div>
          <form className="stack-form" onSubmit={onCreate}><label>Sarlavha<input value={title} onChange={(event) => setTitle(event.target.value)} required maxLength={160} placeholder="Masalan, API health tekshiruvi" /></label><label>Vazifa<textarea value={task} onChange={(event) => setTask(event.target.value)} required maxLength={16_000} rows={5} placeholder="AI bosqichlari ko‘rib chiqishi kerak bo‘lgan vazifani tasvirlang…" /></label><div className="safety-note"><span>ⓘ</span> Bu versiya faqat matnli taklif yaratadi. Kod bajarilmaydi va fayllar o‘zgartirilmaydi.</div><button className="button primary full" disabled={busy || !title.trim() || !task.trim()}>{busy ? "Yaratilmoqda…" : "Workflow yaratish"}<span>↗</span></button></form>
        </section>
        <section className="workflow-list-section"><div className="section-heading"><div><p className="eyebrow">SAQLANGAN NATIJALAR</p><h2>Workflow’lar <span className="count-tag">{workflows.length}</span></h2></div></div>{!workflows.length ? <div className="empty-card compact"><div className="empty-icon">⌘</div><strong>Hali workflow yo‘q</strong><p>Birinchi vazifangizni yarating — natijalar shu yerda ko‘rinadi.</p></div> : <div className="workflow-list">{workflows.map((workflow) => <WorkflowCard key={workflow.id} workflow={workflow} busy={busy} onRun={onRun} />)}</div>}</section>
      </div>
    </>
  );
}

function PhasePill({ name, number }: { name: string; number: string }) {
  return <span className="phase-pill"><small>{number}</small>{name}</span>;
}

function WorkflowCard({ workflow, busy, onRun }: { workflow: Workflow; busy: boolean; onRun: (id: string) => Promise<void> }) {
  const canRun = workflow.status === "queued" || workflow.status === "failed";
  return (
    <article className="workflow-card">
      <div className="workflow-card-head"><div><span className="workflow-mini-icon">⌘</span><div><h3>{workflow.title}</h3><small>{formatDate(workflow.created_at)}</small></div></div><span className={`state-badge ${workflow.status}`}>{workflow.status === "queued" ? "Navbatda" : workflow.status === "running" ? "Bajarilmoqda" : workflow.status === "completed" ? "Tugallandi" : "Xatolik"}</span></div>
      <p className="workflow-task">{workflow.task}</p>
      <div className="phase-list">{workflow.phases.map((phase, index) => <div className={`phase-item ${phase.status}`} key={phase.name}><div className="phase-item-head"><span className="phase-step">{String(index + 1).padStart(2, "0")}</span><strong>{phase.name}</strong><span className={`phase-state ${phase.status}`}>{phase.status === "completed" ? "Tayyor" : phase.status === "failed" ? "Xatolik" : phase.status === "running" ? "Jarayonda" : "Kutilmoqda"}</span></div>{phase.output && <details><summary>Natijani ko‘rish {phase.model && <small>· {phase.model}</small>}</summary><pre>{phase.output}</pre></details>}</div>)}</div>
      {workflow.last_error && <div className="workflow-error">{workflow.last_error}</div>}
      {canRun && <button className="button secondary run-workflow" disabled={busy} onClick={() => void onRun(workflow.id)}>{busy ? "Ishlayapti…" : workflow.status === "failed" ? "Qayta davom ettirish" : "Workflow’ni ishga tushirish"}<span>→</span></button>}
    </article>
  );
}

function PageHeading({ eyebrow, title, body }: { eyebrow: string; title: string; body: string }) {
  return <div className="page-heading"><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p className="muted">{body}</p></div>;
}

function EmptyState({ title, body, action }: { title: string; body: string; action: React.ReactNode }) {
  return <div className="empty-card"><div className="empty-icon">⌂</div><strong>{title}</strong><p>{body}</p>{action}</div>;
}

export default App;
