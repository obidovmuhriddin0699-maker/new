"""The exact caption text sent to Instagram.

One definition shared by the quality limits, the publish preview and the publisher, so
the 2,200-character check and what Meta receives can never disagree.
"""

from collections.abc import Sequence


def published_caption(
    *,
    hook: str | None,
    caption: str | None,
    cta: str | None,
    hashtags: Sequence[str],
    is_story: bool = False,
) -> str:
    """hook (unless the caption already opens with it) + caption + CTA + hashtags.

    Stories carry no caption on Instagram, so they return an empty string.
    """
    if is_story:
        return ""
    body = (caption or "").strip()
    opening = (hook or "").strip()
    parts = []
    if opening and not body.startswith(opening):
        parts.append(opening)
    parts += [body, (cta or "").strip(), " ".join(t.strip() for t in hashtags if t.strip())]
    return "\n\n".join(p for p in parts if p)
