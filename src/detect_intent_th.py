"""ตรวจจับ intent ของข้อความแชทภาษาไทยด้วย keyword matching"""


def _has_keyword(text: str, keywords: list[str]) -> bool:
    """คืนค่า True ถ้าข้อความมี keyword ใด keyword หนึ่งอยู่ข้างใน"""
    return any(word in text for word in keywords)


def detect_intent_th(text: str) -> str:
    """ตรวจจับ intent แบบ rule-based จากข้อความภาษาไทย"""
    normalized_text = text.strip().lower()

    greeting_keywords = ["หวัดดี", "สวัสดี", "ดีครับ", "ดีค่ะ", "ดีจ้า", "ทัก", "ฮัลโหล", "hello", "hi"]
    morning_keywords = ["อรุณสวัสดิ์", "มอนิ่ง", "morning", "เช้านี้", "ตื่นยัง", "ตื่นรึยัง", "เช้าแล้ว"]
    daily_question_keywords = ["ทำไรอยู่", "ทำอะไรอยู่", "กินข้าวยัง", "ถึงบ้านยัง", "นอนยัง", "วันนี้ทำอะไร", "เลิกงานยัง"]
    ask_status_keywords = ["เป็นไงบ้าง", "ช่วงนี้เป็นไง", "โอเคไหม", "สบายดีไหม", "ไหวไหม", "เหนื่อยไหม", "เป็นอะไรไหม"]
    compliment_keywords = ["น่ารัก", "สวย", "หล่อ", "เก่ง", "เท่", "ดีมาก", "สุดยอด", "ภูมิใจ", "จึ้ง", "ปัง"]
    flirt_keywords = ["คิดถึง", "อยากเจอ", "รักนะ", "เป็นห่วง", "ชอบ", "คุยด้วยแล้วดี", "ใจบาง", "จีบ"]
    invite_keywords = ["ไปกิน", "ไปเที่ยว", "ไปดูหนัง", "ไปด้วยกัน", "ว่างไหม", "เจอกันไหม", "นัด", "ไปปะ"]
    apology_keywords = ["ขอโทษ", "โทษที", "ขออภัย", "พูดแรง", "ไม่ได้ตั้งใจ", "ขอโทด"]
    angry_keywords = ["เอาที่สบายใจ", "ไม่ต้องยุ่ง", "ช่างมัน", "พอเถอะ", "รำคาญ", "ไม่อยากคุย", "อย่ามายุ่ง"]
    dry_reply_keywords = ["อืม", "เค", "โอเค", "จ้า", "ครับ", "ค่ะ", "อ่อ", "อ่า", "อื้ม", "แล้วแต่"]
    comfort_keywords = ["ไม่เป็นไรนะ", "สู้ๆ", "สู้ ๆ", "กอดๆ", "พักบ้าง", "เดี๋ยวก็ดีขึ้น", "อยู่ข้างๆ", "ทำดีที่สุดแล้ว"]
    goodnight_keywords = ["ฝันดี", "นอนละ", "นอนก่อน", "ราตรีสวัสดิ์", "หลับฝันดี", "ไปนอนแล้ว"]
    thanks_keywords = ["ขอบคุณ", "ขอบใจ", "แต๊ง", "thank", "ซึ้งใจ"]
    agree_keywords = ["เห็นด้วย", "เอาด้วย", "ตามนั้น", "ได้เลย", "โอเคเลย", "ใช่เลย"]
    disagree_keywords = ["ไม่เห็นด้วย", "ไม่เอา", "ไม่โอเค", "ไม่ใช่", "ขอผ่าน", "ไม่สะดวก"]
    busy_keywords = ["ยุ่ง", "ไม่ว่าง", "ติดงาน", "ประชุม", "งานเยอะ", "เดี๋ยวตอบ"]
    bored_keywords = ["เบื่อ", "เซ็ง", "ไม่มีไรทำ", "ว่างเกิน", "น่าเบื่อ"]
    venting_keywords = ["เหนื่อย", "เครียด", "ท้อ", "ไม่ไหว", "หมดแรง", "แย่มาก", "หนักมาก", "ร้องไห้"]
    sharing_keywords = ["วันนี้ไป", "เมื่อกี้", "เพิ่ง", "ได้มา", "เจอมา", "งานเสร็จ", "เล่าให้ฟัง"]
    jealous_keywords = ["หึง", "น้อยใจ", "ไปคุยกับเขา", "สำคัญกว่า", "ไม่สนใจเรา", "คนอื่น"]
    missed_reply_keywords = ["ทำไมไม่ตอบ", "หายไปไหน", "ไม่อ่าน", "ไม่ตอบ", "ตอบช้า", "หายเลย"]
    question_general_keywords = ["คืออะไร", "ยังไง", "ทำไม", "ได้ไหม", "แบบไหน", "อันนี้"]

    if not normalized_text:
        return "unknown"

    # เช็กกลุ่มที่เฉพาะเจาะจงก่อน เพื่อไม่ให้ไปตก intent กว้าง ๆ
    if _has_keyword(normalized_text, missed_reply_keywords):
        return "missed_reply"
    if _has_keyword(normalized_text, jealous_keywords):
        return "jealous"
    if _has_keyword(normalized_text, morning_keywords):
        return "morning"
    if _has_keyword(normalized_text, greeting_keywords):
        return "greeting"
    if _has_keyword(normalized_text, thanks_keywords):
        return "thanks"

    # daily_question มาก่อน ask_status เพราะ "ทำไรอยู่" เป็นคำถามประจำวัน
    if _has_keyword(normalized_text, daily_question_keywords):
        return "daily_question"
    if _has_keyword(normalized_text, ask_status_keywords):
        return "ask_status"

    if _has_keyword(normalized_text, compliment_keywords):
        return "compliment"
    if _has_keyword(normalized_text, flirt_keywords):
        return "flirt"
    if _has_keyword(normalized_text, invite_keywords):
        return "invite"
    if _has_keyword(normalized_text, apology_keywords):
        return "apology"
    if _has_keyword(normalized_text, comfort_keywords):
        return "comfort"
    if _has_keyword(normalized_text, goodnight_keywords):
        return "goodnight"

    # angry มาก่อน dry_reply เพราะคำสั้นบางคำมีอารมณ์ตัดบทชัดเจน
    if _has_keyword(normalized_text, angry_keywords):
        return "angry"
    if normalized_text in dry_reply_keywords or len(normalized_text) <= 3:
        return "dry_reply"

    if _has_keyword(normalized_text, agree_keywords):
        return "agree"
    if _has_keyword(normalized_text, disagree_keywords):
        return "disagree"
    if _has_keyword(normalized_text, busy_keywords):
        return "busy"
    if _has_keyword(normalized_text, bored_keywords):
        return "bored"
    if _has_keyword(normalized_text, venting_keywords):
        return "venting"
    if _has_keyword(normalized_text, sharing_keywords):
        return "sharing"
    if _has_keyword(normalized_text, question_general_keywords) or normalized_text.endswith("?"):
        return "question_general"

    return "unknown"
