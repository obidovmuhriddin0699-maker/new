"""Rule-based quality evaluator (deterministic, transparent, testable).

Every check is a plain function over an ``EvaluationInput`` and produces
``QualityFinding`` objects with severity, field, message and suggestion.
The score is a heuristic summary of the findings — it does not verify facts
or predict performance, and a failing report never changes content status
beyond keeping it out of review submission. Humans always make the decision.
"""

import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from app.agents.schemas import (
    MAX_CAPTION,
    MAX_CAROUSEL_SLIDES,
    MAX_HASHTAGS,
    MAX_REELS_SECONDS,
    MIN_CAROUSEL_SLIDES,
    QualityFinding,
    QualityReport,
    Severity,
)
from app.core.caption import published_caption
from app.models import BrandProfile, Content
from app.models.enums import ContentType

PENALTY = {Severity.ERROR: 25, Severity.WARNING: 8, Severity.INFO: 2}

# Claims that need proof or are outright prohibited (uz / ru / en).
_GUARANTEE = re.compile(
    r"(100\s?%|kafolat|garantiya|гарант|guarantee[ds]?\b|\bguaranteed\b)", re.IGNORECASE
)
_PERCENT = re.compile(r"\b\d{1,3}(?:[.,]\d+)?\s?%")
_SUPERLATIVE = re.compile(
    r"(eng yaxshi|eng arzon|eng zo['‘’ʻ]r|1-raqamli|№\s?1|#1\b|самы[йе] лучш|лучший в|"
    r"best in\b|number one|\bthe best\b)",
    re.IGNORECASE,
)
_STATISTIC = re.compile(
    r"(statistika|tadqiqot(lar)? (ko['‘’ʻ]rsat|shuni)|статистик|исследовани[яе] показ|"
    r"studies show|research shows|according to (a )?stud)",
    re.IGNORECASE,
)
_TESTIMONIAL = re.compile(
    r"(mijoz(lar)?imiz (aytdi|fikri|yozdi)|отзыв[ы]? (наших|клиент)|client said|"
    r"customer review)",
    re.IGNORECASE,
)
_CYRILLIC = re.compile(r"[Ѐ-ӿ]")
_LATIN = re.compile(r"[A-Za-z]")
_UZ_MARKERS = re.compile(
    r"(o['‘’ʻ]|g['‘’ʻ]|\b(va|uchun|bilan|bu|emas|ham|sizning|qanday|xona|dizayn)\b)",
    re.IGNORECASE,
)
_EN_MARKERS = re.compile(r"\b(the|and|your|with|for|this|room|design|is|are)\b", re.IGNORECASE)
_WORD = re.compile(r"\w+", re.UNICODE)


@dataclass(slots=True)
class EvaluationInput:
    content_type: ContentType
    language: str
    hook: str | None = None
    caption: str | None = None
    cta: str | None = None
    hashtags: list[str] = field(default_factory=list)
    script: str | None = None
    structure: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_content(cls, content: Content) -> "EvaluationInput":
        return cls(
            content_type=content.content_type,
            language=content.language.value,
            hook=content.hook,
            caption=content.caption,
            cta=content.cta,
            hashtags=list(content.hashtags or []),
            script=content.script,
            structure=dict(content.structure or {}),
        )

    def all_text(self) -> str:
        parts = [self.hook, self.caption, self.cta, self.script]
        for slide in self.structure.get("slides", []) or []:
            parts += [slide.get("heading"), slide.get("body")]
        for scene in self.structure.get("scenes", []) or []:
            parts += [scene.get("on_screen_text"), scene.get("narration")]
        for frame in self.structure.get("frames", []) or []:
            parts += [frame.get("text")]
        return "\n".join(p for p in parts if p)


class QualityEvaluator:
    name = "quality_evaluator"

    def __init__(self, brand: BrandProfile | None = None, *, require_cta: bool = True) -> None:
        self.brand = brand
        self.require_cta = require_cta

    def evaluate(self, item: EvaluationInput, *, recent_texts: Iterable[str] = ()) -> QualityReport:
        findings: list[QualityFinding] = []
        checks = [
            "completeness",
            "format_structure",
            "cta",
            "length_limits",
            "hashtags",
            "readability",
            "repetition",
            "unsupported_claims",
            "brand_rules",
            "language",
        ]
        findings += self._completeness(item)
        findings += self._structure(item)
        findings += self._cta(item)
        findings += self._limits(item)
        findings += self._hashtags(item)
        findings += self._readability(item)
        findings += self._repetition(item, list(recent_texts))
        findings += self._claims(item)
        findings += self._brand(item)
        findings += self._language(item)
        score = max(0, 100 - sum(PENALTY[f.severity] for f in findings))
        passed = not any(f.severity == Severity.ERROR for f in findings)
        return QualityReport(passed=passed, score=score, findings=findings, checks=checks)

    # --------------------------------------------------------------- checks
    @staticmethod
    def _f(sev: Severity, code: str, fld: str, msg: str, fix: str | None = None) -> QualityFinding:
        return QualityFinding(severity=sev, code=code, field=fld, message=msg, suggestion=fix)

    def _completeness(self, item: EvaluationInput) -> list[QualityFinding]:
        out = []
        needs_caption = item.content_type in (
            ContentType.POST,
            ContentType.CAROUSEL,
            ContentType.REELS,
        )
        if needs_caption and not (item.caption or "").strip():
            out.append(
                self._f(
                    Severity.ERROR,
                    "missing_caption",
                    "caption",
                    "Caption is empty.",
                    "Write a caption.",
                )
            )
        if item.content_type in (ContentType.POST, ContentType.REELS) and not item.hook:
            out.append(
                self._f(
                    Severity.WARNING,
                    "missing_hook",
                    "hook",
                    "No hook (opening line).",
                    "Add a short opening line.",
                )
            )
        return out

    def _structure(self, item: EvaluationInput) -> list[QualityFinding]:
        out: list[QualityFinding] = []
        s = item.structure or {}
        if item.content_type == ContentType.CAROUSEL:
            slides = s.get("slides") or []
            if not (MIN_CAROUSEL_SLIDES <= len(slides) <= MAX_CAROUSEL_SLIDES):
                out.append(
                    self._f(
                        Severity.ERROR,
                        "carousel_slide_count",
                        "structure.slides",
                        f"Carousel has {len(slides)} slides; expected "
                        f"{MIN_CAROUSEL_SLIDES}-{MAX_CAROUSEL_SLIDES}.",
                        "Adjust the number of slides.",
                    )
                )
            headings = []
            for i, slide in enumerate(slides, 1):
                heading = (slide.get("heading") or "").strip()
                body = (slide.get("body") or "").strip()
                if not heading or not body:
                    out.append(
                        self._f(
                            Severity.ERROR,
                            "carousel_slide_incomplete",
                            f"structure.slides[{i}]",
                            f"Slide {i} needs a heading and body.",
                        )
                    )
                if len(heading.split()) > 10:
                    out.append(
                        self._f(
                            Severity.WARNING,
                            "carousel_heading_long",
                            f"structure.slides[{i}].heading",
                            f"Slide {i} heading is long ({len(heading.split())} words).",
                            "Keep headings under ~8 words.",
                        )
                    )
                headings.append(heading.lower())
            if len(set(headings)) < len(headings):
                out.append(
                    self._f(
                        Severity.WARNING,
                        "carousel_duplicate_heading",
                        "structure.slides",
                        "Some slide headings repeat.",
                    )
                )
        elif item.content_type == ContentType.REELS:
            scenes = s.get("scenes") or []
            if not scenes:
                out.append(
                    self._f(
                        Severity.ERROR,
                        "reels_no_scenes",
                        "structure.scenes",
                        "Reels script has no scenes.",
                    )
                )
            total = 0.0
            for i, scene in enumerate(scenes, 1):
                total += float(scene.get("duration_seconds") or 0)
                if not (scene.get("narration") or scene.get("on_screen_text")):
                    out.append(
                        self._f(
                            Severity.WARNING,
                            "reels_scene_empty",
                            f"structure.scenes[{i}]",
                            f"Scene {i} has neither narration nor on-screen text.",
                        )
                    )
            if total > MAX_REELS_SECONDS:
                out.append(
                    self._f(
                        Severity.ERROR,
                        "reels_too_long",
                        "structure.scenes",
                        f"Scenes total {total:.0f}s (max {MAX_REELS_SECONDS}s).",
                    )
                )
        elif item.content_type == ContentType.STORY:
            if not (s.get("frames") or item.script):
                out.append(
                    self._f(
                        Severity.ERROR,
                        "story_no_frames",
                        "structure.frames",
                        "Story concept has no frames.",
                    )
                )
        return out

    def _cta(self, item: EvaluationInput) -> list[QualityFinding]:
        if self.require_cta and item.content_type != ContentType.STORY and not item.cta:
            return [
                self._f(
                    Severity.ERROR,
                    "missing_cta",
                    "cta",
                    "Call to action is missing.",
                    "Add one clear CTA (e.g. from the brand's preferred CTAs).",
                )
            ]
        return []

    def _limits(self, item: EvaluationInput) -> list[QualityFinding]:
        assembled = published_caption(
            hook=item.hook,
            caption=item.caption,
            cta=item.cta,
            hashtags=item.hashtags,
            is_story=item.content_type == ContentType.STORY,
        )
        if len(assembled) > MAX_CAPTION:
            return [
                self._f(
                    Severity.ERROR,
                    "caption_too_long",
                    "caption",
                    f"Published caption (hook + caption + CTA + hashtags) is {len(assembled)} "
                    f"chars (limit {MAX_CAPTION}).",
                    "Shorten the caption.",
                )
            ]
        return []

    def _hashtags(self, item: EvaluationInput) -> list[QualityFinding]:
        out = []
        if len(item.hashtags) > MAX_HASHTAGS:
            out.append(
                self._f(
                    Severity.ERROR,
                    "too_many_hashtags",
                    "hashtags",
                    f"{len(item.hashtags)} hashtags (limit {MAX_HASHTAGS}).",
                )
            )
        bad = [t for t in item.hashtags if not re.fullmatch(r"#\w+", t, re.UNICODE)]
        if bad:
            out.append(
                self._f(
                    Severity.WARNING,
                    "invalid_hashtag",
                    "hashtags",
                    f"Invalid hashtags: {', '.join(bad[:5])}",
                    "Use # followed by letters, digits or underscores only.",
                )
            )
        if item.content_type != ContentType.STORY and not item.hashtags:
            out.append(self._f(Severity.INFO, "no_hashtags", "hashtags", "No hashtags."))
        return out

    def _readability(self, item: EvaluationInput) -> list[QualityFinding]:
        out = []
        caption = item.caption or ""
        sentences = [s for s in re.split(r"[.!?…]+\s", caption) if s.strip()]
        if sentences:
            avg = sum(len(s.split()) for s in sentences) / len(sentences)
            if avg > 28:
                out.append(
                    self._f(
                        Severity.WARNING,
                        "long_sentences",
                        "caption",
                        f"Average sentence length is {avg:.0f} words.",
                        "Split long sentences.",
                    )
                )
        if any(len(p) > 600 for p in caption.split("\n")):
            out.append(
                self._f(
                    Severity.WARNING,
                    "wall_of_text",
                    "caption",
                    "A paragraph is longer than 600 characters.",
                    "Break the caption into short paragraphs.",
                )
            )
        caps = [w for w in _WORD.findall(item.all_text()) if len(w) > 3 and w.isupper()]
        if len(caps) > 5:
            out.append(
                self._f(
                    Severity.WARNING,
                    "shouting",
                    "caption",
                    "Many words are in ALL CAPS.",
                    "Use normal capitalisation.",
                )
            )
        if item.all_text().count("!") > 5:
            out.append(
                self._f(
                    Severity.INFO,
                    "many_exclamations",
                    "caption",
                    "Many exclamation marks; may read as clickbait.",
                )
            )
        return out

    def _repetition(self, item: EvaluationInput, recent: list[str]) -> list[QualityFinding]:
        out = []
        lines = [ln.strip().lower() for ln in item.all_text().splitlines() if len(ln.strip()) > 15]
        if len(lines) != len(set(lines)):
            out.append(
                self._f(
                    Severity.WARNING,
                    "repeated_lines",
                    "caption",
                    "The same sentence/line appears more than once.",
                )
            )
        mine = _shingles(item.caption or item.all_text())
        if mine:
            for other in recent:
                sim = _jaccard(mine, _shingles(other))
                if sim >= 0.6:
                    out.append(
                        self._f(
                            Severity.WARNING,
                            "similar_to_recent",
                            "caption",
                            f"Very similar to recent content (similarity {sim:.2f}).",
                            "Choose a different angle or rewrite.",
                        )
                    )
                    break
        return out

    def _claims(self, item: EvaluationInput) -> list[QualityFinding]:
        text = item.all_text()
        out = []
        if m := _GUARANTEE.search(text):
            out.append(
                self._f(
                    Severity.ERROR,
                    "guarantee_claim",
                    "caption",
                    f"Guarantee-style claim: “{m.group(0)}”.",
                    "Remove guarantees; describe the approach instead.",
                )
            )
        if m := _STATISTIC.search(text):
            out.append(
                self._f(
                    Severity.WARNING,
                    "unsourced_statistic",
                    "caption",
                    f"Statistic/research claim without a source: “{m.group(0)}”.",
                    "Remove it or add a verifiable source.",
                )
            )
        if m := _PERCENT.search(text):
            if not _GUARANTEE.search(m.group(0)):
                out.append(
                    self._f(
                        Severity.WARNING,
                        "unverified_number",
                        "caption",
                        f"Percentage figure “{m.group(0)}” needs a source.",
                        "Verify the figure or remove it.",
                    )
                )
        if m := _SUPERLATIVE.search(text):
            out.append(
                self._f(
                    Severity.WARNING,
                    "superlative_claim",
                    "caption",
                    f"Unverifiable superlative: “{m.group(0)}”.",
                    "Use a specific, honest description.",
                )
            )
        if m := _TESTIMONIAL.search(text):
            out.append(
                self._f(
                    Severity.ERROR,
                    "testimonial_claim",
                    "caption",
                    f"Possible client testimonial: “{m.group(0)}”.",
                    "Only quote real, consented client feedback.",
                )
            )
        return out

    def _brand(self, item: EvaluationInput) -> list[QualityFinding]:
        if not self.brand:
            return []
        text = item.all_text().lower()
        return [
            self._f(
                Severity.ERROR,
                "banned_phrase",
                "caption",
                f"Brand-banned phrase used: “{phrase}”.",
                "Remove or rephrase it.",
            )
            for phrase in (self.brand.banned_phrases or [])
            if phrase and phrase.lower() in text
        ]

    def _language(self, item: EvaluationInput) -> list[QualityFinding]:
        text = item.all_text()
        letters = len(_CYRILLIC.findall(text)) + len(_LATIN.findall(text))
        if letters < 40:
            return []
        cyr = len(_CYRILLIC.findall(text)) / letters
        msg = None
        if item.language == "ru" and cyr < 0.5:
            msg = "Text does not look Russian (mostly Latin script)."
        elif item.language in ("uz", "en") and cyr > 0.3:
            msg = f"Text uses Cyrillic script but '{item.language}' (Latin) was requested."
        elif item.language == "uz":
            if len(_EN_MARKERS.findall(text)) > 2 * max(1, len(_UZ_MARKERS.findall(text))):
                msg = "Text looks English rather than Uzbek."
        elif item.language == "en":
            if len(_UZ_MARKERS.findall(text)) > 2 * max(1, len(_EN_MARKERS.findall(text))):
                msg = "Text looks Uzbek rather than English."
        if msg:
            return [
                self._f(
                    Severity.WARNING,
                    "language_mismatch",
                    "caption",
                    msg + " (heuristic check)",
                    "Regenerate in the requested language.",
                )
            ]
        return []


def _shingles(text: str, n: int = 3) -> set[tuple[str, ...]]:
    words = [w.lower() for w in _WORD.findall(text)]
    return {tuple(words[i : i + n]) for i in range(max(0, len(words) - n + 1))}


def _jaccard(a: set[Any], b: set[Any]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)
