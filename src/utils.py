import os
from openai import OpenAI

def validate_openai_key(api_key: str):
    """Return (True, '') for a usable key, otherwise (False, friendly error)."""
    if not api_key or not api_key.strip():
        return False, "Please enter your OpenAI API key."

    try:
        client = OpenAI(api_key=api_key.strip())
        client.models.list()
        return True, ""
    except Exception as exc:
        msg = str(exc)
        if "401" in msg or "invalid_api_key" in msg.lower() or "authentication" in msg.lower():
            return False, "Invalid OpenAI API key. Please check the key and try again."
        if "429" in msg:
            return False, "The API key is valid, but the account is rate-limited or has no available quota."
        return False, "We couldn't connect to OpenAI. Check the key, network, and account access."

def human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}"
        size /= 1024
