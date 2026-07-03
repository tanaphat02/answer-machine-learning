"""โหลดและใช้โมเดล ML สำหรับทาย intent ภาษาไทย"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import joblib


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "intent_model_th.joblib"


@lru_cache(maxsize=1)
def load_intent_model():
    """โหลดโมเดลจาก models/intent_model_th.joblib ถ้ามี"""
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)


def predict_intent_ml(text: str) -> tuple[str, float]:
    """ทาย intent ด้วย ML และคืน confidence ถ้าไม่มีโมเดลจะคืน unknown"""
    model = load_intent_model()
    if model is None:
        return "unknown", 0.0

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba([text])[0]
        best_index = int(probabilities.argmax())
        intent = str(model.classes_[best_index])
        confidence = float(probabilities[best_index])
        return intent, confidence

    return str(model.predict([text])[0]), 0.0
