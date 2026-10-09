export type ContentType = "POST" | "CAROUSEL" | "REELS" | "STORY";
export type ContentStatus =
  | "DRAFT"
  | "GENERATING"
  | "READY_FOR_REVIEW"
  | "EDIT_REQUESTED"
  | "APPROVED"
  | "SCHEDULED"
  | "PUBLISHING"
  | "PUBLISHED"
  | "FAILED"
  | "REJECTED";
export type Language = "uz" | "ru" | "en";

export type Asset = {
  id: number;
  kind: "IMAGE" | "VIDEO";
  position: number;
  public_url: string | null;
  mime_type: string | null;
  width: number | null;
  height: number | null;
  duration_seconds: number | null;
  checksum_sha256?: string | null;
};

export type StructureItem = Record<string, string | number | null | undefined>;
export type Structure = {
  kind?: string;
  title?: string;
  alt_text?: string | null;
  slides?: StructureItem[];
  scenes?: StructureItem[];
  frames?: StructureItem[];
  approx_duration_seconds?: number;
};

export type Content = {
  id: number;
  content_type: ContentType;
  status: ContentStatus;
  version: number;
  language: Language;
  topic: string | null;
  hook: string | null;
  caption: string | null;
  hashtags: string[];
  cta: string | null;
  script: string | null;
  visual_prompt: string | null;
  aspect_ratio: string | null;
  brand_profile_id: number | null;
  instagram_account_id: number | null;
  created_by: "HUMAN" | "AGENT" | "SYSTEM";
  structure: Structure;
  planned_date: string | null;
  scheduled_at: string | null;
  published_at: string | null;
  ig_permalink: string | null;
  last_error: string | null;
  created_at: string;
  updated_at: string;
  assets: Asset[];
  publish_authorized: boolean;
};

export type ContentList = { items: Content[]; total: number; offset: number; limit: number };

export type Approval = {
  id: number;
  content_version: number;
  decision: "APPROVED" | "REJECTED" | "EDIT_REQUESTED";
  decided_by_user_id: number;
  channel: string;
  comment: string | null;
  created_at: string;
  invalidated_at: string | null;
  invalidation_reason: string | null;
};

export type ContentVersion = {
  version: number;
  caption: string | null;
  source: "HUMAN" | "AGENT" | "SYSTEM";
  created_by_name: string | null;
  change_note: string | null;
  content_hash: string;
  created_at: string;
  ai_metadata: Record<string, unknown>;
};

export type AuditEvent = {
  id: number;
  timestamp: string;
  actor_type: "HUMAN" | "AGENT" | "SYSTEM";
  actor_user_id: number | null;
  actor_name: string | null;
  action: string;
  content_id?: number | null;
  content_version: number | null;
  status: string;
  error: string | null;
  details: Record<string, unknown>;
};

export type ContentHistory = {
  content_id: number;
  current_version: number;
  status: ContentStatus;
  versions: ContentVersion[];
  approvals: Approval[];
  events: AuditEvent[];
};

export type DashboardSummary = {
  total: number;
  by_status: Record<string, number>;
  pending_approval: number;
  scheduled: number;
  published: number;
  failed: number;
  drafts: number;
  reach: number | null;
  engagement_rate: number | null;
  analytics_available: boolean;
  upcoming: { content_id: number; scheduled_at: string; content_type: string; topic: string | null }[];
};

export type CalendarItem = {
  content_id: number;
  date: string;
  at: string | null;
  kind: "scheduled" | "published" | "planned";
  content_type: ContentType;
  status: ContentStatus;
  topic: string | null;
  version: number;
};

export type Finding = {
  severity: "INFO" | "WARNING" | "ERROR";
  code: string;
  field: string;
  message: string;
  suggestion: string | null;
};
export type QualityReport = {
  passed: boolean;
  score: number;
  findings: Finding[];
  checks: string[];
  disclaimer: string;
};

export type AIJob = {
  id: number;
  job_type: string;
  agent: string;
  status: "QUEUED" | "RUNNING" | "SUCCEEDED" | "FAILED";
  provider: string | null;
  model: string | null;
  content_id: number | null;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
  duration_ms: number | null;
  error_category: string | null;
  error: string | null;
};

export type GenerationResponse = {
  job: AIJob;
  result: Record<string, unknown> | null;
  quality: QualityReport | null;
  content_id: number | null;
  content_status: ContentStatus | null;
};

export type AIStatus = {
  text: {
    provider: string;
    model: string;
    available: boolean;
    model_installed: boolean;
    error_code: string | null;
    message: string | null;
  };
  jobs_mode: "sync" | "celery";
  media: { kind: string; provider: string; configured: boolean; status: string }[];
  agents: string[];
  agent_permissions: string[];
  publishing_available: boolean;
};

export type BrandProfile = {
  id: number;
  name: string;
  niche: string | null;
  voice: string[];
  topics: string[];
  forbidden_rules: string[];
  languages: Language[];
  visual_style: string | null;
  target_audience: string | null;
  services: string[];
  preferred_styles: string[];
  content_goals: string[];
  preferred_ctas: string[];
  banned_phrases: string[];
  is_default: boolean;
  updated_at: string;
};

export type User = {
  id: number;
  email: string;
  full_name: string | null;
  role: "OWNER" | "ADMIN" | "VIEWER";
  is_active: boolean;
};

export type Health = {
  status: "ok" | "degraded";
  app: string;
  version: string;
  environment: string;
  components: Record<string, { ok: boolean; error?: string | null }>;
};

export type ReadinessCheck = { key: string; ok: boolean; severity: "blocker" | "warning" | "info"; message: string };
export type Readiness = { ready: boolean; content_id: number; version: number; checks: ReadinessCheck[]; note: string };

export type DiffLine = { op: "equal" | "add" | "remove"; text: string };
export type FieldDiff = { field: string; changed: boolean; old: unknown; new: unknown; lines: DiffLine[] };
export type VersionDiff = {
  content_id: number;
  from_version: number;
  to_version: number;
  from_label: string;
  changed_fields: string[];
  fields: FieldDiff[];
};

export type ApprovalLogItem = Approval & {
  content_id: number;
  content_topic: string | null;
  decided_by_email: string | null;
  active: boolean;
};
