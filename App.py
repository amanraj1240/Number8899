from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)

# ==================== CONFIG =====================
YOUR_API_KEYS = ["GOKU"]
TARGET_API = "https://numberinfoanshapi.api-e3a.workers.dev/"
CACHE_TIME = 3600
cache = {}
# ================================================

def clean_text(value):
    if isinstance(value, str):
        return value.replace("@Urslash", "").strip()
    if isinstance(value, list):
        return [clean_text(v) for v in value]
    if isinstance(value, dict):
        return {k: clean_text(v) for k, v in value.items()}
    return value

@app.route("/", methods=["GET"])
def number_api():
    num = request.args.get("num")
    key = request.args.get("key")

    if not num or not key:
        return jsonify({"error": "missing parameters"}), 400

    if key not in YOUR_API_KEYS:
        return jsonify({"error": "invalid key"}), 403

    number = "".join(filter(str.isdigit, num))
    if len(number) < 10:
        return jsonify({"error": "invalid number"}), 400

    cached = cache.get(number)
    if cached and time.time() - cached["time"] < CACHE_TIME:
        return jsonify(cached["data"])

    try:
        r = requests.get(f"{TARGET_API}?num={number}", timeout=10)
        if r.status_code != 200:
            return jsonify({"error": "upstream failed"}), 502

        try:
            data = r.json()
            data = clean_text(data)
        except Exception:
            data = {"result": r.text}

        data["developer"] = "@Urslash"
        data["powered_by"] = "urslash-number-api"

        cache[number] = {"time": time.time(), "data": data}
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": "request failed", "details": str(e)}), 500
