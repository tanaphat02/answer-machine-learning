"""Train โมเดลทาย intent จาก dataset แชทภาษาไทย"""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "data" / "tob-ngai-dee-ai-th-dataset-1200.csv"
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "intent_model_th.joblib"


def train_intent_model() -> None:
    """อ่าน dataset แล้ว train โมเดล intent classification"""
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"ไม่พบ dataset: {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH)
    required_columns = {"text", "intent"}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"dataset ต้องมี columns: {sorted(required_columns)}")

    df = df.dropna(subset=["text", "intent"]).copy()
    df["text"] = df["text"].astype(str).str.strip()
    df["intent"] = df["intent"].astype(str).str.strip()
    df = df[(df["text"] != "") & (df["intent"] != "")]

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"],
        df["intent"],
        test_size=0.2,
        random_state=42,
        stratify=df["intent"],
    )

    # ภาษาไทยไม่มีช่องว่างระหว่างคำชัดเจน จึงใช้ char n-gram แทนการตัดคำ
    model = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(analyzer="char", ngram_range=(2, 5))),
            ("clf", LogisticRegression(max_iter=2000)),
        ]
    )

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    print("Train rows:", len(X_train))
    print("Test rows:", len(X_test))
    print("\nClassification report")
    print(classification_report(y_test, predictions, zero_division=0))

    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"\nSaved model to: {MODEL_PATH}")


if __name__ == "__main__":
    train_intent_model()
