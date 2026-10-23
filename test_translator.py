from translator import translate, TranslationError
cases = [("Hello, how are you?", "en", "es"), ("Good morning, my friend", "auto", "fr"),
         ("Wo ist der Bahnhof?", "auto", "en"), ("I love learning languages", "en", "ja")]
for t, s, d in cases:
    out, p = translate(t, s, d)
    print(f"[{s}->{d}] {t!r} -> {out!r} ({p})")
    assert out and out.strip()
try:
    translate("   ", "en", "es"); raise SystemExit("empty input not rejected")
except TranslationError as e:
    print("Empty input handled:", e)
print("ALL TESTS PASSED")

# Security review checks (F1, F6)
try:
    translate("a" * 2001, "en", "es"); raise SystemExit("long input not rejected")
except TranslationError as e:
    print("Long input handled:", e)
from translator import _chunks, _mymemory
long_text = "This is a sentence about learning languages. " * 20
assert all(len(c) <= 450 for c in _chunks(long_text)) and len(_chunks(long_text)) > 1
out = _mymemory(long_text.strip(), "en", "es")
print("Long MyMemory text (%d chars, %d chunks) ->" % (len(long_text), len(_chunks(long_text))), out[:60] + "...")
assert out.strip()
print("SECURITY TESTS PASSED")
