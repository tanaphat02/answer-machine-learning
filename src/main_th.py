"""CLI สำหรับทดลองระบบตอบไงดี AI ภาษาไทย"""

from __future__ import annotations

import sys

try:
    from .analyze_chat_th import analyze_chat_th
except ImportError:
    from analyze_chat_th import analyze_chat_th


VALID_RELATIONSHIPS = {"friend", "crush", "girlfriend", "coworker"}
VALID_STYLES = {"casual", "cute", "funny", "flirty", "polite", "cold"}
VALID_TONE_PROFILES = {"standard", "playful", "warm", "mature", "respectful"}
VALID_PERSONA_MODES = {"normal", "kathoey_diva", "soft_girl", "bestie", "savage"}
VALID_PROFANITY_LEVELS = {"clean", "soft", "spicy", "raw"}
VALID_AGE_GROUPS = {"general", "teen", "university", "working_adult", "adult"}
VALID_MESSAGE_TYPES = {"auto", "question", "statement"}


def _configure_utf8_console() -> None:
    """พยายามตั้งค่า console เป็น UTF-8 เพื่อให้พิมพ์ภาษาไทยบน Windows ได้ดีขึ้น"""
    for stream in (sys.stdin, sys.stdout):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def _read_choice(prompt: str, valid_values: set[str], default: str) -> str:
    """อ่านค่าจากผู้ใช้ ถ้ากด enter ว่างให้ใช้ค่า default"""
    value = input(prompt).strip().lower()
    if not value:
        return default
    if value not in valid_values:
        print(f"ไม่รู้จักค่า '{value}' จึงใช้ค่าเริ่มต้นเป็น {default}")
        return default
    return value


def main() -> None:
    """เริ่มต้น CLI แบบง่ายสำหรับรับข้อความและแสดงคำตอบแนะนำ"""
    _configure_utf8_console()
    print("ตอบไงดี AI - ระบบช่วยแนะนำคำตอบแชทภาษาไทย")
    text = input("ข้อความที่เขาส่งมา: ").strip()

    relationship = _read_choice(
        "ความสัมพันธ์ (friend / crush / girlfriend / coworker) [friend]: ",
        VALID_RELATIONSHIPS,
        "friend",
    )
    style = _read_choice(
        "โทนคำตอบ (casual / cute / funny / flirty / polite / cold) [casual]: ",
        VALID_STYLES,
        "casual",
    )
    tone_profile = _read_choice(
        "โทนการคุย (standard / playful / warm / mature / respectful) [standard]: ",
        VALID_TONE_PROFILES,
        "standard",
    )
    persona_mode = _read_choice(
        "โหมดบุคลิก (normal / kathoey_diva / soft_girl / bestie / savage) [normal]: ",
        VALID_PERSONA_MODES,
        "normal",
    )
    profanity_level = _read_choice(
        "ระดับคำแรง (clean / soft / spicy / raw) [clean]: ",
        VALID_PROFANITY_LEVELS,
        "clean",
    )
    age_group = _read_choice(
        "ช่วงวัยภาษา (general / teen / university / working_adult / adult) [general]: ",
        VALID_AGE_GROUPS,
        "general",
    )
    message_type = _read_choice(
        "รูปแบบข้อความ (auto / question / statement) [auto]: ",
        VALID_MESSAGE_TYPES,
        "auto",
    )

    result = analyze_chat_th(
        text,
        style=style,
        relationship=relationship,
        tone_profile=tone_profile,
        persona_mode=persona_mode,
        profanity_level=profanity_level,
        age_group=age_group,
        message_type=message_type,
    )

    print("\nผลลัพธ์")
    print(f"ข้อความต้นฉบับ: {result['input_text']}")
    print(f"intent: {result['intent']}")
    print(f"style: {result['style']}")
    print(f"relationship: {result['relationship']}")
    print(f"tone_profile: {result['tone_profile']}")
    print(f"persona_mode: {result['persona_mode']}")
    print(f"profanity_level: {result['profanity_level']}")
    print(f"age_group: {result['age_group']}")
    print(f"message_type: {result['message_type']}")
    print("คำตอบที่แนะนำ:")
    for index, reply in enumerate(result["recommended_replies"], start=1):
        print(f"{index}. {reply}")


if __name__ == "__main__":
    main()
