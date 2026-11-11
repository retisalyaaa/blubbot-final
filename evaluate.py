import csv
import sys

from chatbot.engine import ChatbotEngine, load_theme

theme = load_theme("themes/ikan.json")


def akurasi(threshold):
    bot = ChatbotEngine(theme, threshold)
    with open("evaluasi/ikan.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    benar, salah = 0, []
    for r in rows:
        tag, skor = bot.classify(r["kalimat"])
        hasil = tag or "fallback"
        if hasil == r["intent"]:
            benar += 1
        else:
            salah.append((r["kalimat"], r["intent"], hasil, skor))
    return benar, len(rows), salah


if "--sweep" in sys.argv:
    for t in (0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70):
        b, n, _ = akurasi(t)
        print(f"ambang {t:.2f}: {b}/{n} = {b / n * 100:.1f}%")
else:
    b, n, salah = akurasi(0.45)
    print(f"Akurasi: {b}/{n} = {b / n * 100:.1f}%")
    for kalimat, harus, hasil, skor in salah:
        print(f"  SALAH: '{kalimat}' harusnya {harus}, bot jawab {hasil} (skor {skor})")