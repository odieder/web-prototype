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

## Endpoint

- `GET /` -> `{"message":"Hello World"}`
- `POST /upload` -> `{"filename":"...","text":"...","category":"Rechnung"}`
