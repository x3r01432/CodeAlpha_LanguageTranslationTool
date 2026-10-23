"""Translation backend. Swap providers by editing translate()."""
import requests
from deep_translator import GoogleTranslator

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


def translate(text: str, source: str = "auto", target: str = "en") -> tuple[str, str]:
    """Translate text. Returns (translated_text, provider_name)."""
    text = (text or "").strip()
    if not text:
        raise TranslationError("Please enter some text to translate.")
    if len(text) > 4900:
        raise TranslationError("Text is too long (max ~4900 characters).")
    errors = []
    try:
        return GoogleTranslator(source=source, target=target).translate(text), "Google Translate (free)"
    except Exception as e:
        errors.append(f"Google: {e}")
    try:
        return _mymemory(text, source, target), "MyMemory"
    except Exception as e:
        errors.append(f"MyMemory: {e}")
    raise TranslationError("Translation failed. " + " | ".join(errors))


def _mymemory(text: str, source: str, target: str) -> str:
    """Free MyMemory API over HTTPS (supports auto-detect)."""
    src = "autodetect" if source == "auto" else MYMEMORY_CODES.get(source, source)
    r = requests.get("https://api.mymemory.translated.net/get",
                     params={"q": text, "langpair": f"{src}|{MYMEMORY_CODES.get(target, target)}"},
                     timeout=15)
    r.raise_for_status()
    data = r.json()
    if int(data.get("responseStatus", 200)) != 200:
        raise RuntimeError(data.get("responseDetails", "unknown error"))
    return data["responseData"]["translatedText"]
