# Minimal FastAPI App

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
export OPENAI_API_KEY="your_api_key_here"
uvicorn main:app --reload
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend URL: `http://127.0.0.1:5173`  
Backend URL: `http://127.0.0.1:8000`

## Endpoint

- `GET /` -> `{"message":"Hello World"}`
- `POST /upload` -> `{"filename":"...","text":"...","category":"Rechnung","response":"..."}`
