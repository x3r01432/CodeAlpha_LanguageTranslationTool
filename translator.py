"""Translation backend. Swap providers by editing translate()."""
import concurrent.futures as cf
import logging
import re

import requests
from deep_translator import GoogleTranslator

log = logging.getLogger(__name__)

MAX_CHARS = 2000            # security review F6: max input length
MYMEMORY_MAX_CHARS = 450    # F6: MyMemory's free API accepts ~500 bytes per query
HTTP_TIMEOUT = (5, 15)      # F2: (connect, read) seconds for direct requests calls
CALL_TIMEOUT = 20           # F2: hard limit for library calls without their own timeout
_pool = cf.ThreadPoolExecutor(max_workers=4)

LANGUAGES = {
    "Auto-detect": "auto", "English": "en", "Spanish": "es", "French": "fr",
    "German": "de", "Italian": "it", "Portuguese": "pt", "Russian": "ru",
    "Chinese (Simplified)": "zh-CN", "Japanese": "ja", "Korean": "ko",
    "Arabic": "ar", "Hindi": "hi", "Turkish": "tr", "Dutch": "nl", "Urdu": "ur",
}
MYMEMORY_CODES = {"en": "en-GB", "es": "es-ES", "fr": "fr-FR", "de": "de-DE", "it": "it-IT",
    "pt": "pt-PT", "ru": "ru-RU", "zh-CN": "zh-CN", "ja": "ja-JP", "ko": "ko-KR",
    "ar": "ar-SA", "hi": "hi-IN", "tr": "tr-TR", "nl": "nl-NL", "ur": "ur-PK"}


class TranslationError(Exception):
    pass


def run_with_timeout(fn, *args, timeout=CALL_TIMEOUT, **kwargs):
    """Run fn in a worker thread and stop waiting after `timeout` seconds (F2)."""
    return _pool.submit(fn, *args, **kwargs).result(timeout=timeout)


def translate(text: str, source: str = "auto", target: str = "en") -> tuple[str, str]:
    """Translate text. Returns (translated_text, provider_name)."""
    text = (text or "").strip()
    if not text:
        raise TranslationError("Please enter some text to translate.")
    if len(text) > MAX_CHARS:
        raise TranslationError(f"Text is too long (max {MAX_CHARS} characters).")
    try:
        # F2: deep-translator calls requests.get() without a timeout, so bound it here
        out = run_with_timeout(GoogleTranslator(source=source, target=target).translate, text)
        if isinstance(out, str) and out.strip():
            return out, "Google Translate (free)"
        raise RuntimeError("empty response")
    except Exception:
        log.warning("Google provider failed", exc_info=True)  # F1: details go to the log only
    try:
        return _mymemory(text, source, target), "MyMemory"
    except Exception:
        log.warning("MyMemory provider failed", exc_info=True)
    # F1: generic message for users, no internal error details
    raise TranslationError("The translation service is unavailable right now. Please try again in a moment.")


def _chunks(text: str, limit: int = MYMEMORY_MAX_CHARS) -> list[str]:
    """Split text into pieces of at most `limit` chars, preferring sentence/word breaks (F6)."""
    pieces, current = [], ""
    for part in re.split(r"(?<=[.!?。！？\n])\s*", text):
        while len(part) > limit:
            cut = part.rfind(" ", 0, limit)
            cut = cut if cut > 0 else limit
            if current:
                pieces.append(current); current = ""
            pieces.append(part[:cut].strip()); part = part[cut:].strip()
        if current and len(current) + 1 + len(part) > limit:
            pieces.append(current); current = part
        else:
            current = f"{current} {part}".strip() if current else part
    if current:
        pieces.append(current)
    return [p for p in pieces if p]


def _mymemory(text: str, source: str, target: str) -> str:
    """Free MyMemory API over HTTPS (supports auto-detect). Long text is sent in chunks."""
    return " ".join(_mymemory_one(piece, source, target) for piece in _chunks(text))


def _mymemory_one(text: str, source: str, target: str) -> str:
    src = "autodetect" if source == "auto" else MYMEMORY_CODES.get(source, source)
    r = requests.get("https://api.mymemory.translated.net/get",
                     params={"q": text, "langpair": f"{src}|{MYMEMORY_CODES.get(target, target)}"},
                     timeout=HTTP_TIMEOUT)
    r.raise_for_status()
    data = r.json()
    if int(data.get("responseStatus", 200)) != 200:
        raise RuntimeError(data.get("responseDetails", "unknown error"))
    out = (data.get("responseData") or {}).get("translatedText")
    if not isinstance(out, str) or not out.strip():  # F3: validate the untrusted response
        raise RuntimeError("unexpected MyMemory response")
    return out


def text_to_speech(text: str, code: str) -> bytes:
    """Return MP3 bytes for text using gTTS, with timeouts (F2)."""
    import io
    from gtts import gTTS

    def _run():
        buf = io.BytesIO()
        gTTS(text, lang=code.split("-")[0] if code != "zh-CN" else "zh-CN",
             timeout=HTTP_TIMEOUT).write_to_fp(buf)
        return buf.getvalue()
    return run_with_timeout(_run, timeout=CALL_TIMEOUT * 2)
