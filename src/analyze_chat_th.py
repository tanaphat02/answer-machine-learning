"""รวมขั้นตอนวิเคราะห์ข้อความและสร้างคำตอบแนะนำ"""

from __future__ import annotations

try:
    from .detect_intent_th import detect_intent_th
    from .generate_reply_th import find_similar_dataset_texts, generate_reply_th
    from .ml_intent_th import predict_intent_ml
except ImportError:
    from detect_intent_th import detect_intent_th
    from generate_reply_th import find_similar_dataset_texts, generate_reply_th
    from ml_intent_th import predict_intent_ml


ANSWER_MODE_CONFIG = {
    "auto": None,
    "cute_normal": {
        "style": "cute",
        "persona_mode": "normal",
        "profanity_level": "clean",
        "tone_profile": "warm",
    },
    "funny_normal": {
        "style": "funny",
        "persona_mode": "normal",
        "profanity_level": "raw",
        "tone_profile": "playful",
    },
    "cute_kathoey": {
        "style": "cute",
        "persona_mode": "kathoey_diva",
        "profanity_level": "soft",
        "tone_profile": "warm",
    },
    "funny_kathoey": {
        "style": "funny",
        "persona_mode": "kathoey_diva",
        "profanity_level": "raw",
        "tone_profile": "playful",
    },
}


def resolve_answer_mode(
    relationship: str,
    answer_mode: str = "auto",
    style: str = "casual",
    tone_profile: str = "standard",
    persona_mode: str = "normal",
    profanity_level: str = "clean",
) -> dict[str, str]:
    """แปลงโหมดคำตอบแบบง่ายบนหน้าเว็บให้เป็น metadata ที่ dataset ใช้ได้"""
    selected_mode = answer_mode if answer_mode in ANSWER_MODE_CONFIG else "auto"

    if selected_mode == "auto":
        selected_mode = "funny_kathoey" if relationship == "friend" else "cute_kathoey"

    config = ANSWER_MODE_CONFIG[selected_mode] or {}
    return {
        "answer_mode": selected_mode,
        "style": config.get("style", style),
        "tone_profile": config.get("tone_profile", tone_profile),
        "persona_mode": config.get("persona_mode", persona_mode),
        "profanity_level": config.get("profanity_level", profanity_level),
    }


def analyze_chat_th(
    text: str,
    style: str = "casual",
    relationship: str = "friend",
    tone_profile: str = "standard",
    persona_mode: str = "normal",
    profanity_level: str = "clean",
    age_group: str = "general",
    message_type: str = "auto",
    answer_mode: str = "auto",
) -> dict:
    """วิเคราะห์ข้อความแชทภาษาไทย แล้วคืน intent และคำตอบแนะนำ"""
    resolved = resolve_answer_mode(
        relationship=relationship,
        answer_mode=answer_mode,
        style=style,
        tone_profile=tone_profile,
        persona_mode=persona_mode,
        profanity_level=profanity_level,
    )
    style = resolved["style"]
    tone_profile = resolved["tone_profile"]
    persona_mode = resolved["persona_mode"]
    profanity_level = resolved["profanity_level"]
    answer_mode = resolved["answer_mode"]

    keyword_intent = detect_intent_th(text)
    ml_intent, ml_confidence = predict_intent_ml(text)
    intent_source = "keyword"
    intent = keyword_intent

    if ml_confidence >= 0.4:
        intent = ml_intent
        intent_source = "ml"

    similar_texts = find_similar_dataset_texts(text)
    best_match = similar_texts[0] if similar_texts else None
    matched_text = ""
    match_score = 0.0

    if best_match:
        matched_text = str(best_match["text"])
        match_score = float(best_match["score"])

        # ใช้ fuzzy intent เมื่อ rule-based ยังไม่มั่นใจ หรือ match ใกล้มากจนควรเชื่อ dataset
        if intent in {"unknown", "question_general"} or (intent_source != "ml" and match_score >= 0.86):
            intent = str(best_match["intent"])
            intent_source = "fuzzy"

    recommended_replies = generate_reply_th(
        intent,
        style=style,
        relationship=relationship,
        tone_profile=tone_profile,
        persona_mode=persona_mode,
        profanity_level=profanity_level,
        age_group=age_group,
        message_type=message_type,
        preferred_text=matched_text,
        preferred_score=match_score,
    )

    return {
        "input_text": text,
        "intent": intent,
        "intent_source": intent_source,
        "ml_intent": ml_intent,
        "ml_confidence": round(ml_confidence, 3),
        "style": style,
        "relationship": relationship,
        "answer_mode": answer_mode,
        "tone_profile": tone_profile,
        "persona_mode": persona_mode,
        "profanity_level": profanity_level,
        "age_group": age_group,
        "message_type": message_type,
        "matched_text": matched_text,
        "match_score": match_score,
        "similar_texts": similar_texts,
        "recommended_replies": recommended_replies,
    }
