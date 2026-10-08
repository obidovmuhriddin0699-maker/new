export type Workspace = {
  id: string;
  name: string;
  role: "owner" | "admin" | "member";
};

export type CurrentUser = {
  id: string;
  email: string;
  active_workspace_id: string | null;
  workspaces: Workspace[];
};

export type Plan = {
  id: string;
  name: string;
  price_minor: number;
  currency: string;
  limits: Record<string, number>;
};

export type Billing = {
  workspace_id: string;
  status: "trialing" | "active" | "expired";
  trial_started_at: number;
  trial_ends_at: number;
  plan: Plan | null;
  usage: Record<string, number>;
};

export type Phase = {
  name: "planner" | "developer" | "qa";
  status: "pending" | "running" | "completed" | "failed";
  attempt_count: number;
  output: string | null;
  model: string | null;
};

export type Workflow = {
  id: string;
  workspace_id: string;
  created_by_user_id: string;
  title: string;
  task: string;
  status: "queued" | "running" | "completed" | "failed";
  last_error: string | null;
  phases: Phase[];
  created_at: number;
  updated_at: number;
};

export type TelegramLinkStatus = {
  linked: boolean;
  workspace_id: string | null;
};

const apiBase = (import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000").replace(
  /\/$/,
  "",
);

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function csrfToken(): string {
  const token = document.cookie
    .split("; ")
    .find((item) => item.startsWith("csrf_token="))
    ?.split("=")
    .slice(1)
    .join("=");
  return token ? decodeURIComponent(token) : "";
}

export async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body) headers.set("Content-Type", "application/json");
  if (options.method && options.method !== "GET") {
    const token = csrfToken();
    if (token) headers.set("X-CSRF-Token", token);
  }

  let response: Response;
  try {
    response = await fetch(`${apiBase}${path}`, {
      ...options,
      headers,
      credentials: "include",
    });
  } catch {
    throw new Error(`Backend bilan aloqa yo‘q (${apiBase}). Backend ishlayotganini tekshiring.`);
  }

  if (!response.ok) {
    let message = `So‘rov bajarilmadi (${response.status})`;
    try {
      const payload = (await response.json()) as { detail?: unknown };
      if (typeof payload.detail === "string") message = payload.detail;
      else if (payload.detail) message = JSON.stringify(payload.detail);
    } catch {
      // Keep the status-based message when the response is not JSON.
    }
    throw new ApiError(message, response.status);
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export const api = {
  me: () => request<CurrentUser>("/auth/me"),
  login: (email: string, password: string) =>
    request("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  register: (email: string, password: string) =>
    request("/auth/register", { method: "POST", body: JSON.stringify({ email, password }) }),
  logout: () => request<void>("/auth/logout", { method: "POST" }),
  createWorkspace: (name: string) =>
    request<Workspace>("/workspaces", { method: "POST", body: JSON.stringify({ name }) }),
  selectWorkspace: (id: string) =>
    request<Workspace>(`/workspaces/${id}/select`, { method: "POST" }),
  billing: (id: string) => request<Billing>(`/workspaces/${id}/billing`),
  plans: (id: string) => request<Plan[]>(`/workspaces/${id}/billing/plans`),
  checkout: (workspaceId: string, planId: string) =>
    request<{ status: string; simulated: boolean }>(`/workspaces/${workspaceId}/billing/checkout`, {
      method: "POST",
      body: JSON.stringify({ plan_id: planId }),
    }),
  chat: (workspaceId: string, prompt: string) =>
    request<{ model: string; response: string }>(`/workspaces/${workspaceId}/ai/chat`, {
      method: "POST",
      body: JSON.stringify({ prompt }),
    }),
  workflows: (id: string) => request<Workflow[]>(`/workspaces/${id}/workflows`),
  createWorkflow: (workspaceId: string, title: string, task: string) =>
    request<Workflow>(`/workspaces/${workspaceId}/workflows`, {
      method: "POST",
      body: JSON.stringify({ title, task }),
    }),
  runWorkflow: (workspaceId: string, workflowId: string) =>
    request<Workflow>(`/workspaces/${workspaceId}/workflows/${workflowId}/run`, {
      method: "POST",
    }),
  telegramStatus: () => request<TelegramLinkStatus>("/telegram/link"),
  createTelegramLinkCode: () =>
    request<{ code: string; expires_at: number; bot_username: string | null }>(
      "/telegram/link-code",
      { method: "POST" },
    ),
  unlinkTelegram: () => request<void>("/telegram/link", { method: "DELETE" }),
};
