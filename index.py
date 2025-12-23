from fastapi import FastAPI, Query, HTTPException
import requests
import time
import os

app = FastAPI()

# ==================== CONFIG =====================
YOUR_API_KEYS = os.getenv("API_KEYS", "GOKU").split(",")
TARGET_API = "https://numberinfoanshapi.api-e3a.workers.dev/"
CACHE_TIME = 3600
# ================================================

cache = {}

def clean_text(value):
    if isinstance(value, str):
        return value.replace("@Gaurav_Cyber", "").strip()
    if isinstance(value, list):
        return [clean_text(v) for v in value]
    if isinstance(value, dict):
        return {k: clean_text(v) for k, v in value.items()}
    return value


@app.get("/")   # 👈 ROOT ROUTE MUST EXIST
def root(
    num: str = Query(None),
    key: str = Query(None)
):
    if not num or not key:
        return {
            "status": "ok",
            "usage": "?num=Number&key=API_KEY",
            "developer": "@Urslash"
        }

    if key not in YOUR_API_KEYS:
        raise HTTPException(status_code=403, detail="invalid key")

    number = "".join(filter(str.isdigit, num))
    if len(number) < 10:
        raise HTTPException(status_code=400, detail="invalid number")

    cached = cache.get(number)
    if cached and time.time() - cached["time"] < CACHE_TIME:
        return cached["data"]

    r = requests.get(f"{TARGET_API}?num={number}", timeout=10)
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail="upstream failed")

    try:
        data = r.json()
        data = clean_text(data)
    except Exception:
        data = {"result": r.text}

    data["developer"] = "@Urslash"
    data["powered_by"] = "urslash-number-api"

    cache[number] = {"time": time.time(), "data": data}
    return data
