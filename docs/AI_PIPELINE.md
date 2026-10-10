# AI content creation pipeline (PHASE 3)

```
Brand profile ─► Strategist ─► Planner (ideas / plan) ─► Creator (post · carousel · reels · story)
                                                              │
                         JSON extraction + Pydantic validation (1 repair attempt)
                                                              │
                              Quality evaluator (rule-based findings)
                                                              │
               ContentService.create(AgentActor) ─► DRAFT ─(optional, if quality passed)─► READY_FOR_REVIEW
                                                              │
                                                     HUMAN review / approve (PHASE 2 rules)
```

The AI never approves, schedules or publishes. There is no publish endpoint.

## 1. Components

| Component | File | Responsibility |
|---|---|---|
| `AIProvider` | `app/providers/ai/base.py` | Model-agnostic interface: `generate_text(..., json_mode)`, `health()` |
| `OllamaProvider` | `app/providers/ai/ollama.py` | Default local provider (`qwen2.5:3b`), typed errors |
| `MockAIProvider` | `app/providers/ai/mock.py` | Deterministic; tests/offline demos; refused in production |
| `generate_structured` | `app/agents/structured.py` | Prompt → provider → JSON → schema validation → 1 repair try |
| Prompts | `app/agents/prompts.py` | Built **only** from the `BrandProfile` row; user text delimited & limited |
| `ContentStrategist` | `app/agents/strategist.py` | Pillars, recommendations, risks; uses stored performance data only if it exists |
| `ContentPlanner` | `app/agents/planner.py` | Ideas; weekly/monthly plan (dates computed server-side) |
| `ContentCreator` | `app/agents/creator.py` | Post, carousel, reels script, story, hashtags |
| `QualityEvaluator` | `app/agents/quality.py` | Deterministic checks → findings with severity/field/suggestion |
| `AIContentService` | `app/services/ai_content.py` | Orchestration, jobs, persistence via `ContentService`, audit |
| `MediaGenerationService` | `app/services/media.py` | Image requests; returns `not_configured` without a provider |

Agents have no database access and no tools. Persistence is done by the
service with `AgentActor("content_creator", PIPELINE_AGENT_TOOLS)`:
`READ_ANALYTICS, CREATE_CONTENT, EDIT_CONTENT, GENERATE_MEDIA, REQUEST_APPROVAL`.
No approve / schedule / publish permission exists for agents.

## 2. Structured outputs (`app/agents/schemas.py`)

| Output | Key fields / limits |
|---|---|
| Post | hook, caption (≤2200), CTA, hashtags (≤30, normalised), alt text, visual prompt |
| Carousel | title, 2–10 ordered slides (heading ≤80, body ≤400), caption, CTA, hashtags |
| Reels | hook, 1–20 scenes (duration, visual, on-screen text, narration), CTA, caption; total ≤180 s, duration recomputed by the server |
| Story | title, 1–10 frames (visual, text, interactive idea: poll/question/quiz/slider) |
| Ideas | 1–20 ideas: title, format, objective, topic, hook, summary |
| Plan | model returns `day_offset` only; server computes date + weekday, status `PLANNED`/`DRAFT_CREATED`, and a `timing_basis` that says days are **not** optimal-time claims unless analytics exist |
| Hashtags | 1–30 hashtags |

Carousel slides, reels scenes and story frames are saved in `Content.structure`.
`structure` is part of the version hash, so editing a slide after approval
creates a new version that needs a new approval.

## 3. Quality evaluation

Checks: completeness, format structure, CTA, length limits, hashtags,
readability, repetition (inside the text and vs. the last 20 captions),
unsupported claims (guarantees, unsourced %, statistics, superlatives,
testimonials), brand banned phrases, language (heuristic).

`ERROR` findings → `passed=false`. Score = 100 − 25·errors − 8·warnings − 2·info
(heuristic only). A failed report keeps the draft in `DRAFT` (it is still saved
for the human); a passed report never approves anything.

## 4. Jobs: synchronous vs background

Every generation request creates an `AIJob` (type, status, created/started/
finished time, duration, error category, safe message, content id, requesting
user, provider, model). Job input holds the validated request (secret-like keys
redacted); output holds the validated result, quality report and generation
metadata (provider, model, attempts, prompt version, prompt **SHA-256** — never
the prompt text).

| `AI_JOBS_MODE` | Behaviour |
|---|---|
| `sync` (default) | Job runs inside the request; response contains the result. Simple for local dev. |
| `celery` | Request returns **202** with the job; worker task `ai.run_job` executes it; poll `GET /api/v1/ai/jobs/{id}`. Use when the model is slow (CPU-only `qwen2.5:3b` can take 30–120 s). |

Execution is idempotent: a job that is no longer `QUEUED` is never re-run.
The LLM call happens outside any DB transaction. `/evaluate-content` and
`/status` are always synchronous (no LLM call / cheap).

## 5. Errors

| Situation | Job | HTTP (sync mode) | Code |
|---|---|---|---|
| Ollama not running | FAILED `provider_unavailable` | 503 | `ai_provider_unavailable` |
| Model not pulled | FAILED `model_not_found` | 503 | `ai_model_not_found` |
| Timeout | FAILED `timeout` | 504 | `ai_timeout` |
| Bad envelope / empty / oversized | FAILED `invalid_response` | 502 | `ai_invalid_response` |
| JSON invalid after repair | FAILED `invalid_output` | 502 | `ai_invalid_output` |
| Too many active jobs | not created | 429 | `too_many_requests` |
| Language not enabled for brand | not created | 400 | `language_not_supported` |
| Unexpected error | FAILED `internal` | 500 | generic message, details only in server log |

In every failure case no content is saved and nothing is fabricated.

## 6. Providers: real, mocked, not configured

| Provider | Status |
|---|---|
| Text — Ollama | **Real** (default). Requires a local Ollama with the model pulled. |
| Text — Mock | **Mock**: `AI_PROVIDER=mock`, deterministic, labelled `provider="mock"` in metadata; refused in production. |
| Text — OpenAI/Claude-compatible | **Not implemented** yet; add a class implementing `AIProvider`. |
| Image | **Not configured** (`IMAGE_PROVIDER=none`): returns `not_configured`, creates no asset. `mock` returns `placeholder` (no file). |
| Video | **Not configured** (`VIDEO_PROVIDER=none`), same rules. |

## 7. API examples (Windows PowerShell)

```powershell
$body = @{ email = "admin@example.com"; password = "PAROLINGIZ" } | ConvertTo-Json
$token = (Invoke-RestMethod -Method Post http://localhost:8000/api/v1/auth/login -ContentType "application/json" -Body $body).access_token
$h = @{ Authorization = "Bearer $token" }

Invoke-RestMethod http://localhost:8000/api/v1/ai/status -Headers $h

$req = @{ topic = "Minimalist yotoqxona"; slides = 5; language = "uz"; submit_for_review = $true } | ConvertTo-Json
$r = Invoke-RestMethod -Method Post http://localhost:8000/api/v1/ai/generate-carousel -Headers $h -ContentType "application/json" -Body $req
$r.content_status        # DRAFT or READY_FOR_REVIEW — never APPROVED
$r.quality.findings | Format-Table severity, code, field, message

$plan = @{ start_date = "2026-10-12"; period = "week"; posts_per_week = 5 } | ConvertTo-Json
Invoke-RestMethod -Method Post http://localhost:8000/api/v1/ai/content-plan -Headers $h -ContentType "application/json" -Body $plan

$eval = @{ content_id = 1 } | ConvertTo-Json
Invoke-RestMethod -Method Post http://localhost:8000/api/v1/ai/evaluate-content -Headers $h -ContentType "application/json" -Body $eval
```

> Uzbek text in PowerShell 5.1: run `chcp 65001` and
> `[Console]::OutputEncoding = [Text.Encoding]::UTF8` first so characters display correctly.

## 8. Limitations

* Not yet verified against a real `qwen2.5:3b` (the build environment could not
  download models). Small local models may need the repair attempt more often;
  raise `AI_STRUCTURED_MAX_ATTEMPTS` or use a larger model if jobs fail with
  `invalid_output`.
* Language detection and claim detection are heuristics (regex/word lists).
* The evaluator does not fact-check; it flags patterns that need human checking.
* Prompt injection cannot be fully prevented; impact is limited because agents
  have no tools, output is schema-validated and a human approves everything.
* A Celery worker crash mid-job leaves the job `RUNNING` (no stale-job reaper yet).
* Single-tenant: any OWNER/ADMIN can use any brand profile.
