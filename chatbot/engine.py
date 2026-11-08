import json
import random
import re
from difflib import SequenceMatcher

THRESHOLD = 0.45

# kata tidak baku -> kata baku (tambahkan sesuai tema)
NORMALISASI = {
    "gmn": "bagaimana", "gimana": "bagaimana", "gmna": "bagaimana",
    "brp": "berapa", "gak": "tidak", "ga": "tidak", "nggak": "tidak",
    "tdk": "tidak", "udah": "sudah", "udh": "sudah", "kpn": "kapan",
    "utk": "untuk", "dgn": "dengan", "yg": "yang", "bs": "bisa",
    "aquarium": "akuarium", "kran": "keran", "makasi": "makasih",
    "airnya": "air", "ikannya": "ikan",
}

# kata umum yang tidak membantu membedakan intent
STOPWORDS = {
    "yang", "di", "ke", "dari", "itu", "ini", "dong", "deh", "ya", "sih",
    "kak", "min", "aku", "saya", "kamu", "apa", "aja", "nih", "tuh", "dan",
    "atau", "untuk", "dengan", "pada", "kalau", "ikan", "ikanku",
}


def load_theme(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def preprocess(teks):
    teks = re.sub(r"[^a-z0-9\s]", " ", teks.lower())
    tokens = []
    for kata in teks.split():
        for k in NORMALISASI.get(kata, kata).split():
            if k and k not in STOPWORDS:
                tokens.append(k)
    return tokens


def similarity(a, b):
    if not a or not b:
        return 0.0
    sa, sb = set(a), set(b)
    sama = len(sa & sb)
    jaccard = sama / len(sa | sb)
    fuzzy = SequenceMatcher(None, " ".join(a), " ".join(b)).ratio()
    cakupan = sama / len(sb)
    return 0.4 * jaccard + 0.3 * fuzzy + 0.3 * cakupan


class ChatbotEngine:
    def __init__(self, theme, threshold=THRESHOLD):
        self.theme = theme
        self.threshold = threshold
        self.pola = []        # (tag, token_pola, teks_pola)
        self.responses = {}   # tag -> daftar respons
        for intent in theme["intents"]:
            self.responses[intent["tag"]] = intent["responses"]
            for p in intent["patterns"]:
                self.pola.append((intent["tag"], preprocess(p), p))

    def scores(self, pesan):
        tokens = preprocess(pesan)
        terbaik = {}
        for tag, ptokens, p in self.pola:
            s = similarity(tokens, ptokens)
            if s > terbaik.get(tag, (0.0, ""))[0]:
                terbaik[tag] = (s, p)
        return sorted(((s, tag, p) for tag, (s, p) in terbaik.items()), reverse=True)

    def classify(self, pesan):
        ranking = self.scores(pesan)
        if not ranking:
            return None, 0.0
        skor, tag, _ = ranking[0]
        if skor >= self.threshold:
            return tag, round(skor, 2)
        return None, round(skor, 2)

    def reply(self, pesan):
        tag, skor = self.classify(pesan)
        pilihan = self.theme["fallback"] if tag is None else self.responses[tag]
        return {"reply": random.choice(pilihan), "intent": tag, "score": skor}