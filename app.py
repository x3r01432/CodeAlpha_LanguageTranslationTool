import io
import streamlit as st
from translator import LANGUAGES, translate, TranslationError

st.set_page_config(page_title="Language Translation Tool", page_icon="🌐")
st.title("🌐 Language Translation Tool")
st.caption("CodeAlpha AI Internship – Task 1")

names = list(LANGUAGES)
c1, c2 = st.columns(2)
src = c1.selectbox("From", names, index=0)
tgt = c2.selectbox("To", names[1:], index=1)
text = st.text_area("Enter text", height=150, placeholder="Type something to translate...")

if st.button("Translate", type="primary"):
    try:
        with st.spinner("Translating..."):
            out, provider = translate(text, LANGUAGES[src], LANGUAGES[tgt])
        st.session_state.result = (out, LANGUAGES[tgt], provider)
    except TranslationError as e:
        st.session_state.pop("result", None)
        st.warning(str(e))

if "result" in st.session_state:
    out, code, provider = st.session_state.result
    st.subheader("Translation")
    st.success(out)
    st.caption(f"Copy it with the icon at the top-right of the box below · via {provider}")
    st.code(out, language=None)
    if st.button("🔊 Listen"):
        try:
            from gtts import gTTS
            buf = io.BytesIO()
            gTTS(out, lang=code.split("-")[0] if code != "zh-CN" else "zh-CN").write_to_fp(buf)
            st.audio(buf.getvalue(), format="audio/mp3")
        except Exception as e:
            st.error(f"Text-to-speech unavailable: {e}")
