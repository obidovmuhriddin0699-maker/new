import json

import pytest
from pydantic import ValidationError

from app.agents.schemas import (
    CarouselOutput,
    HashtagOutput,
    IdeasOutput,
    PlanDraftOutput,
    PostOutput,
    ReelsScriptOutput,
    StoryOutput,
)
from app.agents.structured import extract_json, generate_structured
from app.providers.ai.base import AIOutputValidationError, AIProviderUnavailableError
from app.providers.ai.mock import MockAIProvider

POST = {"hook": "Hook", "caption": "Caption", "cta": "Save it", "hashtags": ["design"]}


def test_extract_json_variants():
    assert extract_json('{"a": 1}') == {"a": 1}
    assert extract_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert extract_json('Here you go: {"a": {"b": 2}} thanks') == {"a": {"b": 2}}
    with pytest.raises(ValueError):
        extract_json("no json here")


async def test_valid_output_first_try():
    provider = MockAIProvider([json.dumps(POST)])
    result, meta = await generate_structured(
        provider, task="post", system="s", prompt="p", schema=PostOutput
    )
    assert result.hashtags == ["#design"]
    assert meta.attempts == 1 and meta.provider == "mock"
    assert len(meta.prompt_sha256) == 64
    assert "p" not in meta.as_dict().values()  # prompt itself is never stored
    assert provider.calls[0]["json_mode"] is True


async def test_repair_attempt_then_success():
    provider = MockAIProvider(["not json", json.dumps(POST)])
    result, meta = await generate_structured(
        provider, task="post", system="s", prompt="p", schema=PostOutput
    )
    assert meta.attempts == 2
    assert "YOUR PREVIOUS ANSWER WAS INVALID" in provider.calls[1]["prompt"]


async def test_invalid_output_fails_without_fabrication():
    bad = json.dumps({"hook": "x"})  # missing caption/cta
    provider = MockAIProvider([bad, bad])
    with pytest.raises(AIOutputValidationError) as exc:
        await generate_structured(provider, task="post", system="s", prompt="p", schema=PostOutput)
    assert exc.value.category == "invalid_output"
    assert any("caption" in e for e in exc.value.errors)


async def test_non_object_json_rejected():
    provider = MockAIProvider(["[1, 2]", "[3]"])
    with pytest.raises(AIOutputValidationError):
        await generate_structured(provider, task="post", system="s", prompt="p", schema=PostOutput)


async def test_provider_errors_propagate_unchanged():
    provider = MockAIProvider([AIProviderUnavailableError("down")])
    with pytest.raises(AIProviderUnavailableError):
        await generate_structured(provider, task="post", system="s", prompt="p", schema=PostOutput)


def test_hashtag_normalisation_and_limit():
    out = PostOutput.model_validate({**POST, "hashtags": "design, #Design #interior"})
    assert out.hashtags == ["#design", "#interior"]  # comma/space split, case-insensitive dedupe
    out = PostOutput.model_validate({**POST, "hashtags": ["inter ior", "", "#" + "x" * 80]})
    assert out.hashtags == ["#interior"]  # spaces removed, empty and oversized dropped
    with pytest.raises(ValidationError):
        PostOutput.model_validate({**POST, "hashtags": [f"t{i}" for i in range(31)]})
    with pytest.raises(ValidationError):
        HashtagOutput.model_validate({"hashtags": []})


def test_control_characters_stripped():
    out = PostOutput.model_validate({**POST, "caption": "Hi\x00\x07 there\nok"})
    assert out.caption == "Hi there\nok"


def test_caption_length_limit():
    with pytest.raises(ValidationError):
        PostOutput.model_validate({**POST, "caption": "x" * 2201})


def test_carousel_structure():
    slide = {"heading": "H", "body": "B"}
    ok = CarouselOutput.model_validate(
        {"title": "T", "slides": [slide, slide], "caption": "c", "cta": "x"}
    )
    assert len(ok.slides) == 2
    for n in (1, 11):
        with pytest.raises(ValidationError):
            CarouselOutput.model_validate(
                {"title": "T", "slides": [slide] * n, "caption": "c", "cta": "x"}
            )
    with pytest.raises(ValidationError):
        CarouselOutput.model_validate(
            {"title": "T", "slides": [{"heading": "", "body": "b"}] * 2, "caption": "c", "cta": "x"}
        )


def test_reels_structure_and_duration():
    scene = {"duration_seconds": 5, "visual": "v", "on_screen_text": "t", "narration": "n"}
    out = ReelsScriptOutput.model_validate(
        {
            "hook": "h",
            "scenes": [scene, scene],
            "cta": "c",
            "caption": "c",
            "approx_duration_seconds": 99,
        }
    )
    assert out.approx_duration_seconds == 10  # server-computed, model estimate replaced
    with pytest.raises(ValidationError):
        ReelsScriptOutput.model_validate(
            {
                "hook": "h",
                "scenes": [{**scene, "duration_seconds": 60}] * 4,
                "cta": "c",
                "caption": "c",
            }
        )
    with pytest.raises(ValidationError):
        ReelsScriptOutput.model_validate({"hook": "h", "scenes": [], "cta": "c", "caption": "c"})


def test_story_and_ideas_and_plan_schemas():
    StoryOutput.model_validate(
        {"title": "t", "frames": [{"visual": "v", "interactive_element": "poll"}]}
    )
    with pytest.raises(ValidationError):
        StoryOutput.model_validate(
            {"title": "t", "frames": [{"visual": "v", "interactive_element": "link"}]}
        )
    with pytest.raises(ValidationError):
        IdeasOutput.model_validate(
            {
                "ideas": [
                    {
                        "title": "t",
                        "format": "TWEET",
                        "objective": "EDUCATE",
                        "topic": "x",
                        "hook": "h",
                        "summary": "s",
                    }
                ]
            }
        )
    with pytest.raises(ValidationError):
        PlanDraftOutput.model_validate(
            {
                "items": [
                    {
                        "day_offset": 45,
                        "format": "POST",
                        "objective": "EDUCATE",
                        "topic": "t",
                        "title": "t",
                    }
                ]
            }
        )
