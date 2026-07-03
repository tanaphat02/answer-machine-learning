# ตอบไงดี AI

โปรเจกต์ Machine Learning / NLP ภาษาไทยแบบ MVP สำหรับช่วยคิดคำตอบแชท ระบบจะรับข้อความจากเพื่อน คนคุย แฟน หรือเพื่อนร่วมงาน แล้วตรวจจับ intent แบบ rule-based ก่อนเลือก template คำตอบตาม intent, style และ relationship

## ภาพรวมโปรเจกต์

เวอร์ชันนี้ยังไม่ใช้ LLM และไม่ต่อ API ภายนอก เพื่อให้รันง่ายบนเครื่องทั่วไปหรือใน notebook ได้ เหมาะสำหรับเริ่มเรียนรู้ flow ของงาน NLP ภาษาไทย ก่อนต่อยอดเป็นโมเดล ML จริงในอนาคต

## Flow การทำงาน

ข้อความแชท -> detect intent -> เลือก template ตาม intent + style + relationship -> สุ่มคำตอบ -> แสดงผลลัพธ์

ตัวอย่าง:

```text
Input: ทำไรอยู่
relationship: crush
style: flirty

intent: daily_question
recommended replies:
1. กำลังคิดอยู่ว่าจะทักเธอดีไหมพอดี
2. ทำงานอยู่ แต่คุยกับเธอได้
3. ไม่ค่อยได้ทำไร รอคนบางคนทักมา
```

## โครงสร้างไฟล์

```text
chat-reply-ai-th/
├── README.md
├── requirements.txt
├── data/
│   ├── reply_templates_th.json
│   └── th_chat_intent_dataset.csv
├── notebooks/
│   └── experiment_th.ipynb
├── src/
│   ├── __init__.py
│   ├── detect_intent_th.py
│   ├── generate_reply_th.py
│   ├── analyze_chat_th.py
│   └── main_th.py
└── tests/
    └── test_basic_flow.py
```

## วิธีติดตั้ง

```bash
pip install -r requirements.txt
```

ต้องใช้ Python 3.10 ขึ้นไป

## วิธีรัน CLI

```bash
python src/main_th.py
```

โปรแกรมจะถาม 3 อย่าง:

- ข้อความที่เขาส่งมา
- ความสัมพันธ์: `friend`, `crush`, `girlfriend`, `coworker`
- โทนคำตอบ: `casual`, `cute`, `funny`, `flirty`, `polite`, `cold`
- โทนการคุย: `standard`, `playful`, `warm`, `mature`, `respectful`

ถ้ากด enter ว่างใน relationship, style หรือ tone profile ระบบจะใช้ค่าเริ่มต้นเป็น `friend`, `casual` และ `standard`

โทนการคุยใช้ปรับ style แบบเบา ๆ โดยไม่ต้องแยก template ชุดใหญ่:

- `standard`: ใช้ style ตามที่เลือก
- `playful`: ถ้าเลือก `casual` หรือ `polite` จะขยับไปใช้คำตอบแนวกวน ๆ
- `warm`: ถ้าเลือก `cold` หรือ `polite` จะขยับไปใช้คำตอบอบอุ่น/น่ารักขึ้น
- `mature`: ถ้าเลือก `cute` หรือ `funny` จะขยับไปเป็น `casual`
- `respectful`: ถ้าเลือก `cute`, `funny`, `flirty` หรือ `cold` จะขยับไปเป็น `polite`

## วิธีรันเป็นเว็บไซต์

ติดตั้ง dependency ก่อน:

```bash
python -m pip install -r requirements.txt
```

รันเว็บด้วย FastAPI:

```bash
python -m uvicorn src.api_th:app --reload
```

จากนั้นเปิด browser:

```text
http://127.0.0.1:8000
```

## วิธี deploy ขึ้น Vercel

โปรเจกต์นี้มีไฟล์สำหรับ Vercel แล้ว:

```text
api/index.py
vercel.json
.vercelignore
```

ขั้นตอน:

```bash
git add .
git commit -m "add vercel deployment"
git push
```

จากนั้นเข้า Vercel แล้ว Import GitHub repo นี้ได้เลย หรือใช้ Vercel CLI:

```bash
npm i -g vercel
vercel
```

ถ้า deploy production:

```bash
vercel --prod
```

Vercel จะติดตั้งจาก `requirements.txt` และเรียก FastAPI app จาก `api/index.py`

หมายเหตุ: ถ้า build fail เพราะ package ใหญ่เกินไป ให้ลบไฟล์/โฟลเดอร์ที่ไม่จำเป็นออกจาก deploy หรือพิจารณาไม่ deploy notebook ขนาดใหญ่

เว็บจะเรียก API นี้:

```text
POST /api/analyze
```

ตัวอย่าง request:

```json
{
  "text": "ทำไรอยู่",
  "style": "flirty",
  "relationship": "crush",
  "tone_profile": "standard"
}
```

ตัวอย่าง response:

```json
{
  "input_text": "ทำไรอยู่",
  "intent": "daily_question",
  "style": "flirty",
  "relationship": "crush",
  "tone_profile": "standard",
  "recommended_replies": [
    "กำลังคิดอยู่ว่าจะทักเธอดีไหมพอดี",
    "ทำงานอยู่ แต่คุยกับเธอได้",
    "ไม่ค่อยได้ทำไร รอคนบางคนทักมา"
  ]
}
```

## วิธีทดลองใน Jupyter Notebook

เปิดไฟล์:

```bash
jupyter notebook notebooks/experiment_th.ipynb
```

ใน notebook มีตัวอย่างเรียก `analyze_chat_th` หลายข้อความ และมี section ทดลอง train ML เบื้องต้นด้วย `TfidfVectorizer` แบบ char n-gram กับ `LogisticRegression`

## วิธี train โมเดล intent

รันคำสั่งนี้จาก root project:

```bash
python src/train_intent_model_th.py
```

สคริปต์จะอ่าน:

```text
data/tob-ngai-dee-ai-th-dataset-1200.csv
```

แล้ว save โมเดลไว้ที่:

```text
models/intent_model_th.joblib
```

เมื่อมีไฟล์โมเดลนี้ เว็บ/API จะลองใช้ ML ทาย intent ก่อน ถ้า confidence ยังไม่พอ ระบบจะ fallback ไปใช้ keyword และ fuzzy matching เดิม

## วิธีเพิ่ม intent ใหม่

สมมติอยากเพิ่ม intent ชื่อ `morning`

1. เพิ่ม keyword ใน [src/detect_intent_th.py](/d:/PRACTICE/machine/src/detect_intent_th.py)
2. เพิ่มกฎ `if` เพื่อ return `"morning"`
3. เพิ่ม template ของ `morning` ใน [data/reply_templates_th.json](/d:/PRACTICE/machine/data/reply_templates_th.json)
4. เพิ่มตัวอย่างข้อความ intent นี้ใน [data/th_chat_intent_dataset.csv](/d:/PRACTICE/machine/data/th_chat_intent_dataset.csv)
5. เพิ่ม test ใหม่ใน [tests/test_basic_flow.py](/d:/PRACTICE/machine/tests/test_basic_flow.py)

ถ้าเพิ่ม intent เช่น `jealous` ก็ทำ flow เดียวกัน

## วิธีเพิ่ม dataset

เพิ่มข้อมูลที่ [data/th_chat_intent_dataset.csv](/d:/PRACTICE/machine/data/th_chat_intent_dataset.csv) ในรูปแบบ:

```csv
text,intent
ทำไรอะ,daily_question
คิดถึงจัง,flirt
ขอโทดนะ,apology
```

หลักคิดเวลาเพิ่ม dataset:

- เพิ่มข้อความจริงหลายรูปแบบ เช่น พิมพ์สั้น พิมพ์ผิด คำวัยรุ่น คำสุภาพ
- ให้แต่ละ intent มีจำนวนใกล้เคียงกัน ไม่ควรมี intent หนึ่งเยอะกว่ามาก
- ถ้าเพิ่ม intent ใหม่ ต้องเพิ่มทั้ง dataset, keyword detector, template และ test
- ถ้าเพิ่มแค่ประโยคตัวอย่างของ intent เดิม แก้เฉพาะ CSV ได้เลย

จุดที่ต้องแก้ตามกรณี:

```text
เพิ่มข้อความ train ของ intent เดิม:
  data/th_chat_intent_dataset.csv

เพิ่ม dataset เต็มสำหรับเว็บและคำตอบตาม metadata:
  data/tob-ngai-dee-ai-th-dataset-1200.csv

เพิ่ม template คำตอบ:
  data/reply_templates_th.json

เพิ่ม intent ใหม่:
  src/detect_intent_th.py
  data/reply_templates_th.json
  data/th_chat_intent_dataset.csv
  tests/test_basic_flow.py

เพิ่ม style ใหม่:
  data/reply_templates_th.json
  src/main_th.py
  web/index.html
  README.md

เพิ่ม tone_profile ใหม่:
  src/generate_reply_th.py
  src/main_th.py
  src/api_th.py
  web/index.html
  README.md
  tests/test_basic_flow.py
```

## วิธีเพิ่ม template คำตอบใหม่

เปิด [data/reply_templates_th.json](/d:/PRACTICE/machine/data/reply_templates_th.json) แล้วเพิ่มประโยคใน intent และ style ที่ต้องการ เช่น:

```json
{
  "daily_question": {
    "flirty": [
      "กำลังคิดถึงเธออยู่พอดี"
    ]
  }
}
```

ในไฟล์จริงควรคง style ให้ครบ `casual`, `cute`, `funny`, `flirty`, `polite`, `cold` เพื่อให้ fallback ทำงานง่าย

## แนวทางต่อยอดเป็น ML จริง

- ใช้ dataset ใน `data/th_chat_intent_dataset.csv` เป็นจุดเริ่มต้น
- เพิ่มข้อมูลจริงให้หลากหลายขึ้นในแต่ละ intent
- train โมเดลด้วย `TfidfVectorizer(analyzer="char", ngram_range=(2, 5))`
- ใช้ `LogisticRegression` หรือโมเดล text classification อื่น
- บันทึกโมเดลด้วย `pickle` หรือ `joblib`
- แยก service เป็น API ด้วย FastAPI

ภาษาไทยไม่มีการเว้นวรรคคำชัดเจนเหมือนภาษาอังกฤษ การใช้ char n-gram ช่วยให้โมเดลจับ pattern จากตัวอักษรได้โดยไม่ต้องใช้ตัวตัดคำไทย

## ถ้าต่อยอดเป็น Next.js + FastAPI

แยก backend เป็น endpoint คร่าว ๆ แบบนี้:

- `POST /analyze`
- request body: `{ "text": "...", "style": "flirty", "relationship": "crush" }`
- response body: `{ "input_text": "...", "intent": "...", "recommended_replies": [...] }`

ฝั่ง Next.js ส่งข้อความจากฟอร์มไปที่ FastAPI แล้วนำคำตอบมาแสดงเป็นรายการให้ผู้ใช้เลือกคัดลอก
