"""สุ่มคำตอบแนะนำจาก dataset เต็ม หรือ fallback ไป template JSON"""

from __future__ import annotations

import csv
from difflib import SequenceMatcher
import json
import random
from functools import lru_cache
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = PROJECT_ROOT / "data" / "reply_templates_th.json"
DATASET_PATH = PROJECT_ROOT / "data" / "tob-ngai-dee-ai-th-dataset-1200.csv"
TONE_PROFILES = {"standard", "playful", "warm", "mature", "respectful"}


def load_reply_templates() -> dict[str, dict[str, list[str]]]:
    """โหลดไฟล์ template คำตอบจาก data/reply_templates_th.json"""
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(
            "ไม่พบไฟล์ data/reply_templates_th.json กรุณาตรวจสอบว่าอยู่ในโฟลเดอร์ data ของโปรเจกต์"
        )

    with TEMPLATE_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


@lru_cache(maxsize=1)
def load_reply_dataset() -> list[dict[str, str]]:
    """โหลด dataset เต็มที่มี suggested replies และ metadata เพิ่มเติม"""
    if not DATASET_PATH.exists():
        return []

    with DATASET_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def _normalize_for_match(text: str) -> str:
    """ทำข้อความให้เทียบความคล้ายได้ง่ายขึ้น"""
    return "".join(text.strip().lower().split())


def _similarity(left: str, right: str) -> float:
    """คำนวณคะแนนความคล้ายของข้อความ 0.0-1.0"""
    left_norm = _normalize_for_match(left)
    right_norm = _normalize_for_match(right)
    if not left_norm or not right_norm:
        return 0.0
    if left_norm == right_norm:
        return 1.0
    if left_norm in right_norm or right_norm in left_norm:
        return 0.9
    return SequenceMatcher(None, left_norm, right_norm).ratio()


def find_similar_dataset_texts(text: str, limit: int = 3) -> list[dict[str, str | float]]:
    """หา text ใน dataset ที่ใกล้เคียงกับข้อความผู้ใช้ที่สุด"""
    matches: list[dict[str, str | float]] = []

    for row in load_reply_dataset():
        dataset_text = row.get("text", "")
        score = _similarity(text, dataset_text)
        if score >= 0.58:
            matches.append(
                {
                    "text": dataset_text,
                    "intent": row.get("intent", "unknown"),
                    "score": round(score, 3),
                }
            )

    matches.sort(key=lambda item: item["score"], reverse=True)
    return matches[:limit]


def resolve_style_by_tone_profile(style: str, tone_profile: str = "standard") -> str:
    """ปรับ style ตามโทนการคุย โดยยังไม่ต้องเพิ่ม template แยกชุดใหญ่"""
    profile = tone_profile if tone_profile in TONE_PROFILES else "standard"

    if profile == "playful" and style in {"casual", "polite"}:
        return "funny"
    if profile == "warm" and style in {"cold", "polite"}:
        return "cute"
    if profile == "mature" and style in {"cute", "funny"}:
        return "casual"
    if profile == "respectful" and style in {"cute", "funny", "flirty", "cold"}:
        return "polite"

    return style


def _score_dataset_row(
    row: dict[str, str],
    *,
    style: str,
    relationship: str,
    tone_profile: str,
    persona_mode: str,
    profanity_level: str,
    age_group: str,
    message_type: str,
    preferred_text: str = "",
) -> int:
    """ให้คะแนนแถว dataset ตาม metadata ที่ตรงกับตัวเลือกของผู้ใช้"""
    score = 0
    weights = {
        "style": 3,
        "relationship": 2,
        "tone_profile": 2,
        "persona_mode": 2,
        "profanity_level": 3,
        "age_group": 1,
        "message_type": 2,
    }
    expected_values = {
        "style": style,
        "relationship": relationship,
        "tone_profile": tone_profile,
        "persona_mode": persona_mode,
        "profanity_level": profanity_level,
        "age_group": age_group,
        "message_type": message_type,
    }

    for column, expected in expected_values.items():
        if expected and expected != "auto" and row.get(column) == expected:
            score += weights[column]

    if preferred_text and row.get("text") == preferred_text:
        score += 2

    return score


def _unique_replies_from_rows(rows: list[dict[str, str]], amount: int) -> list[str]:
    """ดึง suggested_reply_1..3 แบบไม่ซ้ำจากแถวที่เลือกมา"""
    replies: list[str] = []
    seen: set[str] = set()

    for row in rows:
        for column in ("suggested_reply_1", "suggested_reply_2", "suggested_reply_3"):
            reply = row.get(column, "").strip()
            if reply and reply not in seen:
                replies.append(reply)
                seen.add(reply)

    if len(replies) <= amount:
        return replies

    return random.sample(replies, amount)


def _replies_from_exact_text(preferred_text: str) -> list[str]:
    """ดึงคำตอบ 3 อันจากแถว dataset ที่ text ตรงกับข้อความใกล้เคียงที่สุด"""
    if not preferred_text:
        return []

    for row in load_reply_dataset():
        if row.get("text") == preferred_text:
            return _unique_replies_from_rows([row], 3)

    return []


def _generate_from_dataset(
    intent: str,
    *,
    style: str,
    relationship: str,
    tone_profile: str,
    persona_mode: str,
    profanity_level: str,
    age_group: str,
    message_type: str,
    preferred_text: str = "",
    preferred_score: float = 0.0,
    amount: int,
) -> list[str]:
    """เลือกคำตอบจาก dataset เต็ม โดย match intent ก่อนแล้วค่อยจัดอันดับ metadata"""
    rows = [row for row in load_reply_dataset() if row.get("intent") == intent]
    if not rows:
        return []

    random.shuffle(rows)
    scored_rows = sorted(
        rows,
        key=lambda row: _score_dataset_row(
            row,
            style=style,
            relationship=relationship,
            tone_profile=tone_profile,
            persona_mode=persona_mode,
            profanity_level=profanity_level,
            age_group=age_group,
            message_type=message_type,
            preferred_text=preferred_text,
        ),
        reverse=True,
    )
    top_rows = scored_rows[: min(20, len(scored_rows))]
    metadata_replies = _unique_replies_from_rows(top_rows, amount)

    # ถ้า fuzzy/exact match ชัดมาก ให้ใช้คำตอบจากแถวนั้นก่อน 3 อัน
    # แล้วเติมอีก 3 อันจากแถวอื่น ก่อนสับตำแหน่งเพื่อให้ผลลัพธ์ไม่ตายตัว
    if preferred_text and preferred_score >= 0.8:
        exact_replies = _replies_from_exact_text(preferred_text)
        combined: list[str] = []
        seen: set[str] = set()

        for reply in exact_replies + metadata_replies:
            if reply and reply not in seen:
                combined.append(reply)
                seen.add(reply)

        if len(combined) >= 4:
            combined = combined[:6]
            random.shuffle(combined)
            return combined

    return metadata_replies



def _generate_from_template(
    intent: str,
    *,
    style: str,
    relationship: str,
    tone_profile: str,
    amount: int,
) -> list[str]:
    """fallback ไปใช้ JSON template เดิม"""
    templates = load_reply_templates()

    selected_intent = intent if intent in templates else "unknown"
    intent_templates = templates[selected_intent]
    adjusted_style = resolve_style_by_tone_profile(style, tone_profile)
    selected_style = adjusted_style if adjusted_style in intent_templates else "casual"
    replies = intent_templates[selected_style]

    # ตอนนี้ relationship ใช้ใน dataset เต็มแล้ว ส่วน fallback JSON ยังเก็บไว้เผื่อต่อยอด
    _ = relationship

    sample_size = min(max(amount, 0), len(replies))
    return random.sample(replies, sample_size)


def generate_reply_th(
    intent: str,
    style: str = "casual",
    relationship: str = "friend",
    amount: int = 3,
    tone_profile: str = "standard",
    persona_mode: str = "normal",
    profanity_level: str = "clean",
    age_group: str = "general",
    message_type: str = "auto",
    preferred_text: str = "",
    preferred_score: float = 0.0,
) -> list[str]:
    """เลือกคำตอบตาม intent และ metadata แล้วสุ่มคืนตามจำนวนที่ต้องการ"""
    dataset_replies = _generate_from_dataset(
        intent,
        style=style,
        relationship=relationship,
        tone_profile=tone_profile,
        persona_mode=persona_mode,
        profanity_level=profanity_level,
        age_group=age_group,
        message_type=message_type,
        preferred_text=preferred_text,
        preferred_score=preferred_score,
        amount=amount,
    )
    if dataset_replies:
        return dataset_replies

    return _generate_from_template(
        intent,
        style=style,
        relationship=relationship,
        tone_profile=tone_profile,
        amount=amount,
    )
