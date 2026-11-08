import sys

from chatbot.engine import ChatbotEngine, load_theme

theme = load_theme("themes/ikan.json")
bot = ChatbotEngine(theme)
debug = "--debug" in sys.argv

print(f"{theme['bot_name']}: {theme['greeting']}  (ketik 'keluar' untuk berhenti)")
while True:
    pesan = input("Anda: ").strip()
    if pesan.lower() == "keluar":
        break
    if not pesan:
        continue
    hasil = bot.reply(pesan)
    print("Bot :", hasil["reply"])
    if debug:
        print(f"      [intent: {hasil['intent']} | skor {hasil['score']}]")
        for skor, tag, pola in bot.scores(pesan)[:3]:
            print(f"      - {tag:<18} {skor:.2f}  pola: \"{pola}\"")

# coba dulu di CLI