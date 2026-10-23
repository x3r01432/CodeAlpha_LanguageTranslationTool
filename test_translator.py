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
