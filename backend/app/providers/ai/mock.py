"""Deterministic AI provider for automated tests and offline demos.

It never pretends to be a real model: ``name`` is "mock" and every response's
metadata says so, and it is refused when ``APP_ENV=production``. Responses are
either scripted (a queue or a callable) or produced by a small built-in
generator that returns schema-valid JSON for each pipeline task.
"""

import json
from collections import deque
from collections.abc import Callable, Iterable
from typing import Any

from app.providers.ai.base import AIProvider, AIResponse, ProviderStatus

Responder = Callable[[str, str | None], str]


class MockAIProvider(AIProvider):
    name = "mock"

    def __init__(
        self,
        responses: Iterable[str | Exception] | None = None,
        *,
        responder: Responder | None = None,
        model: str = "mock-deterministic",
    ) -> None:
        self.model = model
        self._queue: deque[str | Exception] = deque(responses or [])
        self._responder = responder
        self.calls: list[dict[str, Any]] = []

    async def generate_text(
        self,
        prompt: str,
        *,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> AIResponse:
        self.calls.append({"prompt": prompt, "system": system, "json_mode": json_mode})
        if self._queue:
            item = self._queue.popleft()
            if isinstance(item, Exception):
                raise item
            text = item
        elif self._responder is not None:
            text = self._responder(prompt, system)
        else:
            text = builtin_response(prompt)
        return AIResponse(text=text, model=self.model, provider=self.name, raw={"mock": True})

    async def health(self) -> ProviderStatus:
        return ProviderStatus(
            self.name, self.model, True, True, None, "Deterministic mock provider"
        )


# ---------------------------------------------------------------- built-in generator
def _task(prompt: str) -> str:
    for line in prompt.splitlines():
        if line.startswith("TASK:"):
            return line.removeprefix("TASK:").strip()
    return ""


def builtin_response(prompt: str) -> str:
    task = _task(prompt)
    payload: dict[str, Any]
    if task == "strategy":
        payload = {
            "summary": "Ta'limiy va portfolio kontentini muvozanatlash.",
            "pillars": [
                {"name": "Dizayn ta'limi", "rationale": "Mijozlarga qaror qabul qilishda yordam"},
                {"name": "Portfolio", "rationale": "Tajribani ko'rsatish"},
            ],
            "recommendations": ["Har hafta kamida bitta ta'limiy karusel"],
            "risks": ["Natijalar hali o'lchanmagan"],
        }
    elif task == "ideas":
        payload = {
            "ideas": [
                {
                    "title": f"G'oya {i + 1}: minimalist yotoqxona",
                    "format": ["CAROUSEL", "REELS", "POST"][i % 3],
                    "objective": ["EDUCATE", "ENGAGE", "SHOWCASE"][i % 3],
                    "topic": "Minimalism",
                    "hook": "Kichik xonani kattaroq ko'rsatish mumkinmi?",
                    "summary": "Yorug'lik va rang tanlash bo'yicha amaliy maslahatlar.",
                }
                for i in range(3)
            ]
        }
    elif task == "content_plan":
        payload = {
            "items": [
                {"day_offset": d, "format": f, "objective": o, "topic": t, "title": f"{t} — reja"}
                for d, f, o, t in [
                    (0, "CAROUSEL", "EDUCATE", "Minimalism"),
                    (2, "REELS", "ENGAGE", "Lighting"),
                    (4, "POST", "SHOWCASE", "3D Visualization"),
                ]
            ],
            "notes": "Kunlar taxminiy; akkaunt analitikasi hali yo'q.",
        }
    elif task == "post":
        payload = {
            "hook": "Minimalizm — bu bo'shliq emas.",
            "caption": "Minimalizm to'g'ri tanlovdan boshlanadi.\n\nOchiq ranglar va tabiiy "
            "yorug'lik xonani kengroq ko'rsatadi.",
            "cta": "Foydali bo'lsa, saqlab qo'ying.",
            "hashtags": ["#interiordesign", "#minimalism"],
            "alt_text": "Och bej rangli minimalist yashash xonasi",
            "visual_prompt": "Minimalist living room, warm beige palette, natural light",
        }
    elif task == "carousel":
        payload = {
            "title": "Minimalist yotoqxona: 3 qoida",
            "slides": [
                {"heading": "1. Ochiq ranglar", "body": "Bej va oq ranglar xonani kengaytiradi."},
                {"heading": "2. Yashirin saqlash", "body": "Ko'rinadigan buyumlar kam bo'lsin."},
                {"heading": "3. Tabiiy yorug'lik", "body": "Pardalarni yengil tanlang."},
            ],
            "caption": "Minimalist yotoqxona uchun uchta oddiy qoida.",
            "cta": "Qaysi qoida sizga yoqdi? Izohda yozing.",
            "hashtags": ["#interiordesign", "#minimalism", "#bedroom"],
        }
    elif task == "reels":
        payload = {
            "hook": "Bu xona 12 kvadrat metr. Ishonasizmi?",
            "scenes": [
                {
                    "duration_seconds": 3,
                    "visual": "Umumiy plan",
                    "on_screen_text": "12 m²",
                    "narration": "Bu xona atigi 12 kvadrat metr.",
                },
                {
                    "duration_seconds": 6,
                    "visual": "Yorug'lik detallari",
                    "on_screen_text": "Yashirin LED",
                    "narration": "Yashirin yoritish chuqurlik beradi.",
                },
                {
                    "duration_seconds": 6,
                    "visual": "Mebel yaqin plan",
                    "on_screen_text": "Kam, lekin sifatli",
                    "narration": "Har bir buyum o'z joyida.",
                },
            ],
            "cta": "Ko'proq g'oyalar uchun obuna bo'ling.",
            "caption": "Kichik xona ham premium ko'rinishi mumkin.",
            "hashtags": ["#interiordesign", "#reels"],
            "approx_duration_seconds": 15,
        }
    elif task == "story":
        payload = {
            "title": "Qaysi uslub sizga yaqin?",
            "frames": [
                {"visual": "Minimalist xona", "text": "Minimalizm"},
                {
                    "visual": "Neo klassik xona",
                    "text": "Neo klassika",
                    "interactive_element": "poll",
                },
            ],
            "cta": "Ovoz bering!",
        }
    elif task == "hashtags":
        payload = {"hashtags": ["#interiordesign", "#minimalism", "#3dvisualization"]}
    elif task == "weekly_analytics_report":
        # Deliberately number-free: the mock never invents statistics.
        payload = {
            "summary": "Hafta natijalari faqat sinxronlangan Meta statistikasi asosida "
            "ko'rib chiqildi. Ta'limiy kontent eng barqaror natija berdi.",
            "highlights": [],
            "recommendations": [
                "Eng yaxshi natija bergan mavzuni davom ettiring.",
                "Statistika to'liq bo'lmagan formatlarni yana sinab ko'ring.",
            ],
        }
    else:
        payload = {"error": "unknown task"}
    return json.dumps(payload, ensure_ascii=False)
