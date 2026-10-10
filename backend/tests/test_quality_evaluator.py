import pytest

from app.agents.quality import EvaluationInput, QualityEvaluator
from app.agents.schemas import Severity
from app.models.enums import ContentType

GOOD = dict(
    content_type=ContentType.POST,
    language="uz",
    hook="Kichik xona ham keng ko‘rinishi mumkin.",
    caption="Minimalizm bu to‘g‘ri tanlov. Ochiq ranglar va tabiiy yorug‘lik xonani "
    "kengroq ko‘rsatadi.\n\nYashirin saqlash joylari tartib beradi.",
    cta="Saqlab qo‘ying.",
    hashtags=["#interiordesign", "#minimalism"],
)


def codes(report):
    return {f.code for f in report.findings}


def test_good_post_passes():
    report = QualityEvaluator().evaluate(EvaluationInput(**GOOD))
    assert report.passed and report.score == 100 and report.findings == []
    assert "not verify factual accuracy" in report.disclaimer


def test_missing_fields():
    report = QualityEvaluator().evaluate(
        EvaluationInput(content_type=ContentType.POST, language="uz")
    )
    assert {"missing_caption", "missing_cta", "missing_hook"} <= codes(report)
    assert not report.passed and report.score < 50
    f = next(f for f in report.findings if f.code == "missing_cta")
    assert f.severity == Severity.ERROR and f.field == "cta" and f.suggestion


def test_cta_optional_when_not_required():
    item = EvaluationInput(**{**GOOD, "cta": None})
    assert "missing_cta" not in codes(QualityEvaluator(require_cta=False).evaluate(item))


@pytest.mark.parametrize(
    ("text", "code", "severity"),
    [
        ("Natija 100% kafolatlanadi.", "guarantee_claim", Severity.ERROR),
        ("We guarantee results.", "guarantee_claim", Severity.ERROR),
        ("Mijozlarning 87% mamnun.", "unverified_number", Severity.WARNING),
        ("Statistika shuni ko‘rsatadiki dizayn muhim.", "unsourced_statistic", Severity.WARNING),
        ("Biz Toshkentdagi eng yaxshi studiyamiz.", "superlative_claim", Severity.WARNING),
        ("Mijozimiz aytdi: ajoyib!", "testimonial_claim", Severity.ERROR),
    ],
)
def test_unsupported_claims(text, code, severity):
    report = QualityEvaluator().evaluate(EvaluationInput(**{**GOOD, "caption": text}))
    found = [f for f in report.findings if f.code == code]
    assert found and found[0].severity == severity


def test_brand_banned_phrase(brand):
    item = EvaluationInput(**{**GOOD, "cta": "100% KAFOLAT bilan buyurtma bering"})
    report = QualityEvaluator(brand).evaluate(item)
    assert "banned_phrase" in codes(report) and not report.passed


def test_carousel_structure_checks():
    base = {**GOOD, "content_type": ContentType.CAROUSEL}
    one = EvaluationInput(**base, structure={"slides": [{"heading": "A", "body": "b"}]})
    assert "carousel_slide_count" in codes(QualityEvaluator().evaluate(one))
    dup = EvaluationInput(
        **base,
        structure={
            "slides": [
                {"heading": "Same", "body": "b"},
                {"heading": "same", "body": "c"},
                {"heading": "x " * 12, "body": ""},
            ]
        },
    )
    c = codes(QualityEvaluator().evaluate(dup))
    assert {"carousel_duplicate_heading", "carousel_heading_long", "carousel_slide_incomplete"} <= c


def test_reels_structure_checks():
    base = {**GOOD, "content_type": ContentType.REELS}
    assert "reels_no_scenes" in codes(
        QualityEvaluator().evaluate(EvaluationInput(**base, structure={"scenes": []}))
    )
    long = EvaluationInput(
        **base,
        structure={
            "scenes": [
                {"duration_seconds": 100, "visual": "v"},
                {"duration_seconds": 100, "visual": "v", "narration": "n"},
            ]
        },
    )
    c = codes(QualityEvaluator().evaluate(long))
    assert {"reels_too_long", "reels_scene_empty"} <= c


def test_story_without_frames():
    item = EvaluationInput(content_type=ContentType.STORY, language="uz")
    assert "story_no_frames" in codes(QualityEvaluator().evaluate(item))


def test_limits_and_hashtags():
    item = EvaluationInput(
        **{
            **GOOD,
            "caption": "So‘z. " * 500,
            "hashtags": [f"#t{i}" for i in range(31)] + ["#bad tag"],
        }
    )
    c = codes(QualityEvaluator().evaluate(item))
    assert {"caption_too_long", "too_many_hashtags", "invalid_hashtag"} <= c


def test_readability():
    long_sentence = " ".join(["so‘z"] * 40) + "."
    item = EvaluationInput(
        **{
            **GOOD,
            "caption": long_sentence
            + " "
            + long_sentence
            + " DIQQAT JUDA MUHIM YANGI CHEGIRMA HOZIROQ OLING!!!!!!",
        }
    )
    c = codes(QualityEvaluator().evaluate(item))
    assert {"long_sentences", "shouting", "many_exclamations"} <= c


def test_repetition_inside_and_against_recent():
    line = "Bu jumla bir necha marta takrorlanadi albatta."
    item = EvaluationInput(**{**GOOD, "caption": f"{line}\n{line}"})
    assert "repeated_lines" in codes(QualityEvaluator().evaluate(item))
    report = QualityEvaluator().evaluate(EvaluationInput(**GOOD), recent_texts=[GOOD["caption"]])
    assert "similar_to_recent" in codes(report)


@pytest.mark.parametrize(
    ("language", "caption", "flag"),
    [
        ("ru", "Minimalizm bu to‘g‘ri tanlov va xonani kengroq ko‘rsatadi uchun bilan.", True),
        ("uz", "Минимализм — это правильный выбор для небольшой квартиры и дома.", True),
        ("uz", "This is the best room design for your home and the light is great.", True),
        ("uz", GOOD["caption"], False),
    ],
)
def test_language_heuristic(language, caption, flag):
    item = EvaluationInput(**{**GOOD, "language": language, "caption": caption})
    assert ("language_mismatch" in codes(QualityEvaluator().evaluate(item))) is flag
