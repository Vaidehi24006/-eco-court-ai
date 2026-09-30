import requests

from .config import GEMINI_API_KEY, GEMINI_MODEL


class LLMError(Exception):
    pass


def generate(prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise LLMError("GEMINI_API_KEY is missing. Add it to the .env file and restart the backend.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 1500},
    }
    try:
        r = requests.post(url, json=body, timeout=90,
                          headers={"x-goog-api-key": GEMINI_API_KEY,
                                   "Content-Type": "application/json"})
    except requests.exceptions.RequestException as e:
        raise LLMError(f"Could not reach the Gemini API: {e}")

    if r.status_code in (400, 401, 403):
        raise LLMError(f"Gemini rejected the request ({r.status_code}). Check your API key and "
                       f"GEMINI_MODEL name. Details: {r.text[:300]}")
    if r.status_code == 404:
        raise LLMError(f"Model '{GEMINI_MODEL}' not found. Set GEMINI_MODEL in .env to a current "
                       f"model name from Google AI Studio.")
    if r.status_code == 429:
        raise LLMError("Gemini free-tier rate limit hit. Wait a minute and try again.")
    if r.status_code != 200:
        raise LLMError(f"Gemini error {r.status_code}: {r.text[:300]}")

    try:
        parts = r.json()["candidates"][0]["content"]["parts"]
        return "".join(p.get("text", "") for p in parts).strip()
    except (KeyError, IndexError):
        raise LLMError("Gemini returned no answer (it may have been blocked). Try rephrasing.")