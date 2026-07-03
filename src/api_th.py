"""FastAPI backend สำหรับใช้งานระบบตอบไงดี AI ผ่านเว็บไซต์"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

try:
    from .analyze_chat_th import analyze_chat_th
except ImportError:
    from analyze_chat_th import analyze_chat_th


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = PROJECT_ROOT / "web"

app = FastAPI(title="ตอบไงดี AI", version="0.1.0")
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


class AnalyzeRequest(BaseModel):
    """ข้อมูลที่ frontend ส่งมาให้ backend วิเคราะห์"""

    text: str = Field(..., min_length=1)
    style: str = "casual"
    relationship: str = "friend"
    tone_profile: str = "standard"
    persona_mode: str = "normal"
    profanity_level: str = "clean"
    age_group: str = "general"
    message_type: str = "auto"
    answer_mode: str = "auto"


class AnalyzeResponse(BaseModel):
    """รูปแบบผลลัพธ์ที่ backend ส่งกลับไปให้ frontend"""

    input_text: str
    intent: str
    intent_source: str
    ml_intent: str
    ml_confidence: float
    style: str
    relationship: str
    answer_mode: str
    tone_profile: str
    persona_mode: str
    profanity_level: str
    age_group: str
    message_type: str
    matched_text: str
    match_score: float
    similar_texts: list[dict]
    recommended_replies: list[str]


@app.get("/")
def home() -> FileResponse:
    """ส่งหน้าเว็บไซต์หลักกลับไปให้ browser"""
    return FileResponse(WEB_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    """endpoint ตรวจสุขภาพ server แบบง่าย"""
    return {"status": "ok"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> dict:
    """วิเคราะห์ข้อความและส่งคำตอบแนะนำกลับไปเป็น JSON"""
    return analyze_chat_th(
        text=request.text,
        style=request.style,
        relationship=request.relationship,
        tone_profile=request.tone_profile,
        persona_mode=request.persona_mode,
        profanity_level=request.profanity_level,
        age_group=request.age_group,
        message_type=request.message_type,
        answer_mode=request.answer_mode,
    )
