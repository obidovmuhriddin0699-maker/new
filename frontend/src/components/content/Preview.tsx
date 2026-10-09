"use client";

import type { Content, StructureItem } from "@/lib/types";

const RATIO_CLASS: Record<string, string> = {
  "4:5": "aspect-[4/5]",
  "1:1": "aspect-square",
  "16:9": "aspect-video",
  "9:16": "aspect-[9/16]",
};

export function MediaBox({ content }: { content: Content }) {
  const asset = content.assets.find((a) => a.public_url);
  const ratio = RATIO_CLASS[content.aspect_ratio ?? ""] ?? "aspect-[4/5]";
  return (
    <div className={`${ratio} mx-auto w-full max-w-xs overflow-hidden rounded-xl border border-border bg-background`}>
      {asset?.public_url ? (
        asset.kind === "VIDEO" ? (
          <video src={asset.public_url} controls className="h-full w-full object-cover" />
        ) : (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={asset.public_url} alt={content.structure?.alt_text ?? content.topic ?? ""} className="h-full w-full object-cover" />
        )
      ) : (
        <div className="flex h-full flex-col items-center justify-center gap-2 p-4 text-center text-xs text-muted">
          <span className="text-sm font-medium">Media hali yo‘q</span>
          <span>Rasm/video provayderi sozlanmagan (not_configured). Real media yaratilmagan.</span>
          {content.assets.length > 0 && <span>{content.assets.length} ta media metadata saqlangan</span>}
          <span className="mt-1 rounded border border-border px-2 py-0.5">{content.aspect_ratio ?? "—"}</span>
        </div>
      )}
    </div>
  );
}

function text(v: unknown): string {
  return v === null || v === undefined ? "" : String(v);
}

export function StructureView({ content }: { content: Content }) {
  const s = content.structure ?? {};
  if (s.slides?.length) {
    return (
      <ol className="space-y-2" data-testid="slides">
        {s.slides.map((slide: StructureItem, i) => (
          <li key={i} className="rounded-xl border border-border p-3">
            <p className="text-xs text-muted">Slayd {i + 1}</p>
            <p className="font-medium">{text(slide.heading)}</p>
            <p className="mt-1 whitespace-pre-line text-sm">{text(slide.body)}</p>
          </li>
        ))}
      </ol>
    );
  }
  if (s.scenes?.length) {
    return (
      <div>
        <p className="mb-2 text-sm text-muted">Taxminiy davomiylik: {s.approx_duration_seconds ?? "—"} soniya</p>
        <ol className="space-y-2" data-testid="scenes">
          {s.scenes.map((scene: StructureItem, i) => (
            <li key={i} className="rounded-xl border border-border p-3 text-sm">
              <p className="text-xs text-muted">
                Sahna {i + 1} · {text(scene.duration_seconds)} s
              </p>
              <p><span className="text-muted">Kadr:</span> {text(scene.visual)}</p>
              {scene.on_screen_text && <p><span className="text-muted">Ekrandagi matn:</span> {text(scene.on_screen_text)}</p>}
              {scene.narration && <p><span className="text-muted">Ovoz:</span> {text(scene.narration)}</p>}
            </li>
          ))}
        </ol>
      </div>
    );
  }
  if (s.frames?.length) {
    return (
      <ol className="space-y-2" data-testid="frames">
        {s.frames.map((frame: StructureItem, i) => (
          <li key={i} className="rounded-xl border border-border p-3 text-sm">
            <p className="text-xs text-muted">Kadr {i + 1}{frame.interactive_element && frame.interactive_element !== "none" ? ` · ${text(frame.interactive_element)}` : ""}</p>
            <p>{text(frame.visual)}</p>
            {frame.text && <p className="font-medium">{text(frame.text)}</p>}
          </li>
        ))}
      </ol>
    );
  }
  return null;
}

export function CaptionView({ content }: { content: Content }) {
  return (
    <div className="space-y-3 text-sm">
      {content.hook && (
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-muted">Hook</p>
          <p className="font-medium">{content.hook}</p>
        </div>
      )}
      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-muted">Caption</p>
        <p className="whitespace-pre-line break-words" data-testid="caption">{content.caption || <span className="text-muted">— (yo‘q)</span>}</p>
      </div>
      {content.cta && (
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-muted">CTA</p>
          <p>{content.cta}</p>
        </div>
      )}
      {content.hashtags.length > 0 && (
        <div className="flex flex-wrap gap-1.5" data-testid="hashtags">
          {content.hashtags.map((h) => (
            <span key={h} className="rounded-full bg-background px-2 py-0.5 text-xs text-muted">{h}</span>
          ))}
        </div>
      )}
      {content.script && !content.structure?.scenes?.length && !content.structure?.frames?.length && (
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-muted">Ssenariy</p>
          <p className="whitespace-pre-line">{content.script}</p>
        </div>
      )}
    </div>
  );
}
