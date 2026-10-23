import logging
import time
import streamlit as st
from translator import LANGUAGES, MAX_CHARS, translate, text_to_speech, TranslationError

log = logging.getLogger(__name__)
TRANSLATE_COOLDOWN = 3.0  # seconds, security review F5
LISTEN_COOLDOWN = 5.0


def rate_limited(key: str, min_interval: float) -> bool:
    """Simple per-session cooldown (F5). Returns True if the action should be skipped."""
    now = time.monotonic()
    if now - st.session_state.get(key, -1e9) < min_interval:
        return True
    st.session_state[key] = now
    return False


st.set_page_config(page_title="Language Translation Tool", page_icon="🌐")
st.title("🌐 Language Translation Tool")
st.caption("CodeAlpha AI Internship – Task 1")

names = list(LANGUAGES)
c1, c2 = st.columns(2)
src = c1.selectbox("From", names, index=0)
tgt = c2.selectbox("To", names[1:], index=1)
text = st.text_area("Enter text", height=150, max_chars=MAX_CHARS,
                    placeholder="Type something to translate...")

if st.button("Translate", type="primary"):
    if rate_limited("last_translate", TRANSLATE_COOLDOWN):
        st.warning("Please wait a few seconds between translations.")
    else:
        try:
            with st.spinner("Translating..."):
                out, provider = translate(text, LANGUAGES[src], LANGUAGES[tgt])
            st.session_state.result = (out, LANGUAGES[tgt], provider)
        except TranslationError as e:
            st.session_state.pop("result", None)
            st.warning(str(e))  # TranslationError messages are written for users (F1)

if "result" in st.session_state:
    out, code, provider = st.session_state.result
    st.subheader("Translation")
    # F3: third-party output is shown as plain text, never interpreted as Markdown
    st.text(out)
    st.caption(f"Copy it with the icon at the top-right of the box below · via {provider}")
    st.code(out, language=None)
    if st.button("🔊 Listen"):
        if rate_limited("last_tts", LISTEN_COOLDOWN):
            st.warning("Please wait a few seconds before playing it again.")
        else:
            try:
                with st.spinner("Generating audio..."):
                    audio = text_to_speech(out, code)
                st.audio(audio, format="audio/mp3")
            except Exception:
                log.exception("Text-to-speech failed")  # F1: details go to the server log only
                st.error("Text-to-speech is unavailable right now. Please try again later.")
