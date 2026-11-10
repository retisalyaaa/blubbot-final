import pytest

from chatbot.engine import ChatbotEngine, load_theme, preprocess, similarity

theme = load_theme("themes/ikan.json")
engine = ChatbotEngine(theme)


def test_preprocess_normalisasi_dan_stopword():
    assert preprocess("Gmn cara ganti air, kak?") == ["bagaimana", "cara", "ganti", "air"]


def test_similarity_kalimat_sama_bernilai_satu():
    t = preprocess("ganti air")
    assert similarity(t, t) == pytest.approx(1.0)


def test_similarity_kalimat_berbeda_rendah():
    assert similarity(preprocess("ganti air"), preprocess("bintik putih")) < 0.3


def test_semua_intent_valid():
    for intent in theme["intents"]:
        assert len(intent["patterns"]) >= 5, intent["tag"]
        assert len(intent["responses"]) >= 2, intent["tag"]
    assert len(theme["intents"]) >= 10
    assert len(theme["suggestions"]) == 4


@pytest.mark.parametrize("pesan,harapan", [
    ("halo", "greeting"),
    ("jadwal makan ikan", "jadwal_makan"),
    ("gmn cara ganti air", "ganti_air"),
    ("air akuarium keruh", "air_keruh"),
    ("ikan megap megap", "ikan_megap_megap"),
    ("dosis obat ikan berapa", "tanya_obat_dosis"),
    ("makasih ya", "terima_kasih"),
])
def test_klasifikasi_intent(pesan, harapan):
    tag, _ = engine.classify(pesan)
    assert tag == harapan


def test_salah_ketik_masih_dikenali():
    tag, _ = engine.classify("jadwl makan ikan")
    assert tag == "jadwal_makan"


def test_pertanyaan_di_luar_tema_fallback():
    tag, skor = engine.classify("siapa presiden indonesia")
    assert tag is None
    assert skor < 0.45


def test_reply_fallback_dari_file_tema():
    hasil = engine.reply("resep nasi goreng")
    assert hasil["intent"] is None
    assert hasil["reply"] in theme["fallback"]