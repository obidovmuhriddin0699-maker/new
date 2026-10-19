"use client";

import { useState } from "react";
import { Button, Card, ErrorBox, PageHeader } from "@/components/ui";
import { api } from "@/lib/api";

type Tab = "generator" | "ai_seo" | "analytics" | "oauth";

interface VideoGenResponse {
  title: string;
  hook: string;
  video_url: string;
  file_path: string;
  youtube_video_id?: string | null;
  youtube_url?: string | null;
}

interface MetadataResponse {
  titles: string[];
  description: string;
  tags: string[];
  hashtags: string[];
  thumbnail_concept: string;
  pinned_comment: string;
}

interface ChannelStats {
  channel_id: string;
  title: string;
  description: string;
  custom_url?: string | null;
  subscriber_count: number;
  video_count: number;
  view_count: number;
}

export default function YouTubePage() {
  const [tab, setTab] = useState<Tab>("generator");

  // Video Generator State
  const [genTopic, setGenTopic] = useState("Sun'iy intellekt kelajagi va 3 ta muhim sir");
  const [genVoice, setGenVoice] = useState("uz-UZ-SardorNeural");
  const [genSeconds, setGenSeconds] = useState(45);
  const [genLoading, setGenLoading] = useState(false);
  const [genResult, setGenResult] = useState<VideoGenResponse | null>(null);
  const [genError, setGenError] = useState<string | null>(null);

  // SEO Metadata State
  const [seoTopic, setSeoTopic] = useState("Python dasturlash orqali daromad topish");
  const [seoAudience, setSeoAudience] = useState("Dasturchilar va IT qiziquvchilari");
  const [seoLoading, setSeoLoading] = useState(false);
  const [seoResult, setSeoResult] = useState<MetadataResponse | null>(null);
  const [seoError, setSeoError] = useState<string | null>(null);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  // Channel Analytics State
  const [channelData, setChannelData] = useState<ChannelStats | null>(null);
  const [channelLoading, setChannelLoading] = useState(false);
  const [channelError, setChannelError] = useState<string | null>(null);
  const [accessToken, setAccessToken] = useState("");

  async function handleGenerateVideo() {
    if (!genTopic.trim()) return;
    setGenLoading(true);
    setGenError(null);
    setGenResult(null);

    try {
      const res = await api<VideoGenResponse>("youtube/generate-video", {
        method: "POST",
        body: JSON.stringify({
          topic: genTopic,
          language: "uz",
          voice: genVoice,
          seconds: genSeconds,
          upload_to_youtube: false,
        }),
      });
      setGenResult(res);
    } catch (err: unknown) {
      setGenError(err instanceof Error ? err.message : "Video yaratishda xatolik yuz berdi");
    } finally {
      setGenLoading(false);
    }
  }

  async function handleGenerateSEO() {
    if (!seoTopic.trim()) return;
    setSeoLoading(true);
    setSeoError(null);
    setSeoResult(null);

    try {
      const res = await api<MetadataResponse>("youtube/ai/metadata", {
        method: "POST",
        body: JSON.stringify({
          topic: seoTopic,
          target_audience: seoAudience,
          language: "uz",
        }),
      });
      setSeoResult(res);
    } catch (err: unknown) {
      setSeoError(err instanceof Error ? err.message : "SEO metadata yaratishda xato");
    } finally {
      setSeoLoading(false);
    }
  }

  async function handleLoadChannel() {
    if (!accessToken.trim()) {
      setChannelError("Iltimos, avval OAuth Access Tokenni kiriting.");
      return;
    }
    setChannelLoading(true);
    setChannelError(null);
    try {
      const res = await api<ChannelStats>(`youtube/channel?access_token=${encodeURIComponent(accessToken)}`);
      setChannelData(res);
    } catch (err: unknown) {
      setChannelError(err instanceof Error ? err.message : "Kanal ma'lumotlarini olishda xato");
    } finally {
      setChannelLoading(false);
    }
  }

  function copyToClipboard(text: string, key: string) {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="YouTube Studio & AI Agent"
        subtitle="YouTube Shorts va videolarni to'liq avtomatik generatsiya qilish, SEO optimallashtirish va kanalni boshqarish."
      />

      {/* Tabs Header */}
      <div className="flex flex-wrap gap-2 border-b border-border pb-3">
        <button
          type="button"
          onClick={() => setTab("generator")}
          className={`rounded-xl px-4 py-2 text-sm font-medium transition ${
            tab === "generator"
              ? "bg-accent text-accent-fg shadow-sm"
              : "border border-border bg-card text-muted hover:text-foreground"
          }`}
        >
          🎬 Video Generator (.mp4)
        </button>
        <button
          type="button"
          onClick={() => setTab("ai_seo")}
          className={`rounded-xl px-4 py-2 text-sm font-medium transition ${
            tab === "ai_seo"
              ? "bg-accent text-accent-fg shadow-sm"
              : "border border-border bg-card text-muted hover:text-foreground"
          }`}
        >
          ✍️ AI Ssenariy & SEO
        </button>
        <button
          type="button"
          onClick={() => setTab("analytics")}
          className={`rounded-xl px-4 py-2 text-sm font-medium transition ${
            tab === "analytics"
              ? "bg-accent text-accent-fg shadow-sm"
              : "border border-border bg-card text-muted hover:text-foreground"
          }`}
        >
          📊 Kanal & Analitika
        </button>
        <button
          type="button"
          onClick={() => setTab("oauth")}
          className={`rounded-xl px-4 py-2 text-sm font-medium transition ${
            tab === "oauth"
              ? "bg-accent text-accent-fg shadow-sm"
              : "border border-border bg-card text-muted hover:text-foreground"
          }`}
        >
          🔑 Sozlamalar & Ulanish
        </button>
      </div>

      {/* TAB 1: VIDEO GENERATOR */}
      {tab === "generator" && (
        <div className="grid gap-6 lg:grid-cols-12">
          {/* Left Form */}
          <div className="lg:col-span-7">
            <Card title="🎬 Avtomatik Shorts Video Yaratish">
              <p className="mb-4 text-xs text-muted">
                AI avval 3 soniyalik qiziqarli HOOK va ssenariy yozadi, so&apos;ngra Edge TTS bilan ovoz beradi va 
                1080x1920 HD vertikal video sifatida montaj qiladi.
              </p>

              <div className="space-y-4">
                <div>
                  <label htmlFor="gen-topic" className="mb-1 block text-xs font-semibold text-muted">
                    Video mavzusi
                  </label>
                  <input
                    id="gen-topic"
                    type="text"
                    value={genTopic}
                    onChange={(e) => setGenTopic(e.target.value)}
                    placeholder="Masalan: Dasturlashni o'rganishda 3 ta katta xato"
                    className="w-full rounded-xl border border-border bg-background px-4 py-2.5 text-sm focus:border-accent focus:outline-none"
                  />
                </div>

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label htmlFor="gen-voice" className="mb-1 block text-xs font-semibold text-muted">
                      TTS Ovoz (Neural)
                    </label>
                    <select
                      id="gen-voice"
                      value={genVoice}
                      onChange={(e) => setGenVoice(e.target.value)}
                      className="w-full rounded-xl border border-border bg-background px-3 py-2.5 text-sm focus:border-accent focus:outline-none"
                    >
                      <option value="uz-UZ-SardorNeural">🇺🇿 Sardor (O&apos;zbekcha - Erkak)</option>
                      <option value="uz-UZ-MadinaNeural">🇺🇿 Madina (O&apos;zbekcha - Ayol)</option>
                      <option value="ru-RU-DmitryNeural">🇷🇺 Dmitry (Ruscha - Erkak)</option>
                      <option value="en-US-ChristopherNeural">🇺🇸 Christopher (Inglizcha)</option>
                    </select>
                  </div>

                  <div>
                    <label htmlFor="gen-seconds" className="mb-1 block text-xs font-semibold text-muted">
                      Mo&apos;ljallangan vaqt
                    </label>
                    <select
                      id="gen-seconds"
                      value={genSeconds}
                      onChange={(e) => setGenSeconds(Number(e.target.value))}
                      className="w-full rounded-xl border border-border bg-background px-3 py-2.5 text-sm focus:border-accent focus:outline-none"
                    >
                      <option value={30}>30 soniya (Tezkor)</option>
                      <option value={45}>45 soniya (Standart)</option>
                      <option value={60}>60 soniya (Batafsil)</option>
                    </select>
                  </div>
                </div>

                <ErrorBox error={genError} />

                <Button
                  variant="primary"
                  onClick={handleGenerateVideo}
                  loading={genLoading}
                  className="w-full py-3 text-base shadow-md"
                >
                  {genLoading ? "✨ Video yig'ilmoqda (TTS + Montaj)..." : "🚀 Video Yaratish (Start)"}
                </Button>
              </div>
            </Card>
          </div>

          {/* Right Preview */}
          <div className="lg:col-span-5">
            <Card title="📱 Natija va Video Pleer">
              {genLoading ? (
                <div className="flex h-96 flex-col items-center justify-center space-y-4 rounded-xl border border-dashed border-border p-6 text-center">
                  <div className="h-10 w-10 animate-spin rounded-full border-4 border-accent border-t-transparent" />
                  <p className="text-sm font-semibold">AI Video tayyorlanmoqda...</p>
                  <p className="text-xs text-muted">
                    Ssenariy tuzilmoqda, audio sintezlanmoqda va 1080x1920 kadrlar montaj qilinmoqda (10-15s).
                  </p>
                </div>
              ) : genResult ? (
                <div className="space-y-4">
                  <div className="relative mx-auto aspect-[9/16] max-h-[500px] overflow-hidden rounded-2xl border border-border bg-black shadow-lg">
                    <video
                      controls
                      autoPlay
                      src={genResult.video_url}
                      className="h-full w-full object-contain"
                    >
                      <track kind="captions" />
                    </video>
                  </div>

                  <div className="rounded-xl border border-border bg-background p-3 text-xs">
                    <p className="font-semibold text-foreground">Sarlavha: {genResult.title}</p>
                    <p className="mt-1 text-muted">Hook: &ldquo;{genResult.hook}&rdquo;</p>
                  </div>

                  <div className="flex gap-2">
                    <a
                      href={genResult.video_url}
                      download="shorts.mp4"
                      className="inline-flex w-full items-center justify-center rounded-xl bg-emerald-600 px-4 py-2.5 text-xs font-semibold text-white shadow hover:bg-emerald-700"
                    >
                      📥 Videoni Yuklab Olish
                    </a>
                  </div>
                </div>
              ) : (
                <div className="flex h-96 flex-col items-center justify-center rounded-xl border border-dashed border-border p-6 text-center text-muted">
                  <span className="text-4xl mb-2">🎬</span>
                  <p className="text-sm font-medium text-foreground">Hozircha video generatsiya qilinmadi</p>
                  <p className="text-xs">Mavzuni kiriting va &quot;Video Yaratish&quot; tugmasini bosing.</p>
                </div>
              )}
            </Card>
          </div>
        </div>
      )}

      {/* TAB 2: AI SEO & SSENARIY */}
      {tab === "ai_seo" && (
        <div className="space-y-6">
          <Card title="✍️ YouTube AI SEO & Ssenariy">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label htmlFor="seo-topic" className="mb-1 block text-xs font-semibold text-muted">
                  Video mavzusi
                </label>
                <input
                  id="seo-topic"
                  type="text"
                  value={seoTopic}
                  onChange={(e) => setSeoTopic(e.target.value)}
                  placeholder="Mavzuni yozing..."
                  className="w-full rounded-xl border border-border bg-background px-4 py-2 text-sm focus:border-accent focus:outline-none"
                />
              </div>
              <div>
                <label htmlFor="seo-audience" className="mb-1 block text-xs font-semibold text-muted">
                  Maqsadli auditoriya
                </label>
                <input
                  id="seo-audience"
                  type="text"
                  value={seoAudience}
                  onChange={(e) => setSeoAudience(e.target.value)}
                  placeholder="Auditoriya..."
                  className="w-full rounded-xl border border-border bg-background px-4 py-2 text-sm focus:border-accent focus:outline-none"
                />
              </div>
            </div>

            {seoError && <div className="mt-3"><ErrorBox error={seoError} /></div>}

            <Button
              variant="primary"
              onClick={handleGenerateSEO}
              loading={seoLoading}
              className="mt-4"
            >
              ✨ Yuqori CTR Metadata & Tavsif Generatsiya Qilish
            </Button>
          </Card>

          {seoResult && (
            <div className="grid gap-6 lg:grid-cols-2">
              {/* Titles & Description */}
              <div className="space-y-4">
                <Card title="🎯 Tavsiya Etilgan Sarlavhalar (Yuqori CTR)">
                  <div className="space-y-2">
                    {seoResult.titles.map((t, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between rounded-xl border border-border bg-background p-3 text-sm"
                      >
                        <span>{idx + 1}. {t}</span>
                        <button
                          type="button"
                          onClick={() => copyToClipboard(t, `title_${idx}`)}
                          className="rounded-lg bg-accent/20 px-2.5 py-1 text-xs text-accent hover:bg-accent/30"
                        >
                          {copiedKey === `title_${idx}` ? "✓ Nusxalandi" : "Nusxa"}
                        </button>
                      </div>
                    ))}
                  </div>
                </Card>

                <Card title="📝 YouTube Tavsifi (Description)">
                  <div className="relative rounded-xl border border-border bg-background p-4">
                    <pre className="whitespace-pre-wrap font-sans text-xs text-foreground/90">
                      {seoResult.description}
                    </pre>
                    <button
                      type="button"
                      onClick={() => copyToClipboard(seoResult.description, "desc")}
                      className="absolute right-3 top-3 rounded-lg bg-accent/20 px-3 py-1 text-xs text-accent hover:bg-accent/30"
                    >
                      {copiedKey === "desc" ? "✓ Nusxalandi" : "Nusxa olish"}
                    </button>
                  </div>
                </Card>
              </div>

              {/* Tags, Thumbnail, Pinned comment */}
              <div className="space-y-4">
                <Card title="🏷️ SEO Qidiruv Teglari">
                  <div className="flex flex-wrap gap-2">
                    {seoResult.tags.map((tag, i) => (
                      <span
                        key={i}
                        className="rounded-lg bg-card px-3 py-1.5 text-xs font-medium text-foreground shadow-sm border border-border"
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>
                  <button
                    type="button"
                    onClick={() => copyToClipboard(seoResult.tags.join(", "), "tags")}
                    className="mt-3 text-xs text-accent underline"
                  >
                    {copiedKey === "tags" ? "✓ Vergul bilan nusxalandi" : "Barcha teglarni vergul bilan nusxalash"}
                  </button>
                </Card>

                <Card title="🖼️ Thumbnail (Muqova) Konsepsiyasi">
                  <div className="rounded-xl border border-border bg-background p-4 text-xs leading-relaxed text-foreground/90">
                    {seoResult.thumbnail_concept}
                  </div>
                </Card>

                <Card title="📌 Qadaladigan Birinchi Izoh (Pinned Comment)">
                  <div className="rounded-xl border border-border bg-background p-4 text-xs text-foreground/90">
                    {seoResult.pinned_comment}
                  </div>
                </Card>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: KANAL ANALITIKASI */}
      {tab === "analytics" && (
        <div className="space-y-6">
          <Card title="📊 YouTube Kanal Ko'rsatkichlari">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
              <input
                type="text"
                value={accessToken}
                onChange={(e) => setAccessToken(e.target.value)}
                placeholder="Google OAuth Access Token ni kiriting..."
                className="flex-1 rounded-xl border border-border bg-background px-4 py-2 text-sm focus:border-accent focus:outline-none"
              />
              <Button variant="primary" onClick={handleLoadChannel} loading={channelLoading}>
                Statistikani Yuklash
              </Button>
            </div>

            {channelError && <div className="mt-3"><ErrorBox error={channelError} /></div>}

            {channelData ? (
              <div className="mt-6 space-y-6">
                <div className="rounded-2xl border border-border bg-background p-5">
                  <h3 className="text-lg font-bold">{channelData.title}</h3>
                  <p className="text-xs text-muted">{channelData.description || "Tavsif mavjud emas"}</p>
                </div>

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                  <div className="rounded-2xl border border-border bg-card p-5 text-center shadow-sm">
                    <p className="text-xs uppercase text-muted font-semibold tracking-wider">Obunachilar</p>
                    <p className="mt-2 text-3xl font-extrabold text-accent">
                      {channelData.subscriber_count.toLocaleString()}
                    </p>
                  </div>
                  <div className="rounded-2xl border border-border bg-card p-5 text-center shadow-sm">
                    <p className="text-xs uppercase text-muted font-semibold tracking-wider">Umumiy Ko&apos;rishlar</p>
                    <p className="mt-2 text-3xl font-extrabold text-foreground">
                      {channelData.view_count.toLocaleString()}
                    </p>
                  </div>
                  <div className="rounded-2xl border border-border bg-card p-5 text-center shadow-sm">
                    <p className="text-xs uppercase text-muted font-semibold tracking-wider">Jami Videolar</p>
                    <p className="mt-2 text-3xl font-extrabold text-foreground">
                      {channelData.video_count.toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <p className="mt-4 text-xs text-muted">
                Kanal statistikasini ko&apos;rish uchun Google OAuth orqali hisobingizni ulang yoki yuqoridagi maydonga token kiriting.
              </p>
            )}
          </Card>
        </div>
      )}

      {/* TAB 4: SOZLAMALAR VA ULANISH */}
      {tab === "oauth" && (
        <Card title="⚙️ YouTube Data API v3 & Google Ulanish">
          <div className="space-y-4 text-sm text-foreground/90">
            <p>
              YouTube kanalga to&apos;g&apos;ridan-to&apos;g&apos;ri yuklash va rejalashtirish uchun Google Cloud Console orqali
              OAuth 2.0 ulanishi amalga oshiriladi.
            </p>

            <div className="rounded-xl border border-border bg-background p-4 space-y-2 text-xs">
              <p className="font-semibold text-foreground">Kerakli qadamlar:</p>
              <ol className="list-decimal list-inside space-y-1 text-muted">
                <li>Google Cloud Console (console.cloud.google.com) ga kiring.</li>
                <li>YouTube Data API v3 ni yoqing.</li>
                <li>OAuth 2.0 Client ID yarating va `.env` fayliga kiriting.</li>
                <li>
                  CLI orqali <code className="rounded bg-accent/20 px-1 py-0.5 text-accent">python youtube_agent.py auth</code> buyrug&apos;ini ishga tushiring.
                </li>
              </ol>
            </div>

            <div className="pt-2">
              <a
                href="https://console.cloud.google.com/apis/library/youtube.googleapis.com"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-2 rounded-xl bg-accent px-4 py-2 text-xs font-semibold text-accent-fg hover:opacity-90"
              >
                Google Cloud Console da ochish ↗
              </a>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
