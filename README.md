# CodeAlpha_LanguageTranslationTool

A simple language translation web app built for the **CodeAlpha AI Internship – Task 1**.

## Features
- Enter any text and pick source (with **Auto-detect**) and target languages from dropdowns (15 languages)
- Translation via a free, no-key service: Google Translate (through `deep-translator`), with **MyMemory** as automatic fallback
- Clear display of the translated text, with a **copy** button
- **Text-to-speech** playback of the translation (gTTS)
- Friendly handling of empty input and network/API errors

## Tech Stack
Python 3 · Streamlit · deep-translator · gTTS

## Setup
```bash
git clone https://github.com/x3r01432/CodeAlpha_LanguageTranslationTool.git
cd CodeAlpha_LanguageTranslationTool
pip install -r requirements.txt
streamlit run app.py
```
Run the quick test: `python test_translator.py` (needs internet).

## Project Structure
```
app.py              # Streamlit UI
translator.py       # translate() function + language list
test_translator.py  # sample translations + empty-input check
requirements.txt
LICENSE
```

## Using a paid API instead (optional)
All translation goes through `translate()` in `translator.py`. To use an official key-based API, replace its body, e.g.:
- **Google Cloud Translation:** `pip install google-cloud-translate`, set `GOOGLE_APPLICATION_CREDENTIALS`, then call `translate_v2.Client().translate(text, target_language=target)`.
- **Microsoft Translator:** `deep_translator.MicrosoftTranslator(api_key=os.environ["MS_TRANSLATOR_KEY"], source=..., target=...)`.

Keep keys in environment variables, never in the code.

## Author
[x3r01432](https://github.com/x3r01432)

## License
MIT – see [LICENSE](LICENSE).

## Security

This app was reviewed in [CodeAlpha_SecureCodingReview](https://github.com/x3r01432/CodeAlpha_SecureCodingReview), and these fixes are applied:

- Errors show a short generic message. Technical details go to the server log only.
- Every outside call has a time limit: Google Translate (20 s), MyMemory (5 s to connect, 15 s to read), and text-to-speech.
- Translations are shown as plain text, so Markdown or links from a translation service aren't rendered.
- Translate has a 3-second cooldown and Listen a 5-second cooldown per browser session.
- Input is limited to 2,000 characters. Long text sent to MyMemory is split into pieces of 450 characters or less to stay within its limit.
- Dependencies are pinned to exact tested versions in `requirements.txt`. deep-translator stays at 1.11.4 (see advisory PYSEC-2022-252 in the review).
