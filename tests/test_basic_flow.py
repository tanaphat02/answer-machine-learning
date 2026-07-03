from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.analyze_chat_th import analyze_chat_th
from src.detect_intent_th import detect_intent_th


def test_detect_greeting() -> None:
    assert detect_intent_th("หวัดดี") == "greeting"


def test_detect_daily_question() -> None:
    assert detect_intent_th("ทำไรอยู่") == "daily_question"


def test_detect_flirt() -> None:
    assert detect_intent_th("คิดถึง") == "flirt"


def test_detect_venting_statement() -> None:
    assert detect_intent_th("วันนี้เหนื่อยมากเลย") == "venting"


def test_analyze_chat_returns_expected_shape() -> None:
    result = analyze_chat_th("ทำไรอยู่", style="flirty", relationship="crush")

    assert "intent" in result
    assert "recommended_replies" in result
    assert "tone_profile" in result
    assert "persona_mode" in result
    assert "profanity_level" in result
    assert "age_group" in result
    assert "message_type" in result
    assert result["intent"] == "daily_question"
    assert isinstance(result["recommended_replies"], list)
    assert len(result["recommended_replies"]) > 0


def test_answer_mode_auto_maps_by_relationship() -> None:
    result = analyze_chat_th(
        "คิดถึง",
        relationship="friend",
        answer_mode="auto",
    )

    assert result["intent"] == "flirt"
    assert result["answer_mode"] == "funny_kathoey"
    assert result["persona_mode"] == "kathoey_diva"
    assert isinstance(result["recommended_replies"], list)


def test_dataset_metadata_flow() -> None:
    result = analyze_chat_th(
        "วันนี้เหนื่อยมากเลย",
        style="funny",
        relationship="friend",
        tone_profile="playful",
        persona_mode="kathoey_diva",
        profanity_level="spicy",
        age_group="university",
        message_type="statement",
    )

    assert result["intent"] == "venting"
    assert result["persona_mode"] == "kathoey_diva"
    assert len(result["recommended_replies"]) > 0


def test_exact_dataset_match_can_return_six_replies() -> None:
    result = analyze_chat_th(
        "ทำไรอยู่วะ",
        relationship="friend",
        answer_mode="auto",
    )

    assert result["matched_text"] == "ทำไรอยู่วะ"
    assert result["match_score"] >= 0.8
    assert len(result["recommended_replies"]) >= 4
    assert len(result["recommended_replies"]) <= 6


if __name__ == "__main__":
    test_detect_greeting()
    test_detect_daily_question()
    test_detect_flirt()
    test_detect_venting_statement()
    test_analyze_chat_returns_expected_shape()
    test_answer_mode_auto_maps_by_relationship()
    test_dataset_metadata_flow()
    test_exact_dataset_match_can_return_six_replies()
    print("basic flow tests passed")
