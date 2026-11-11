"""Uji unit untuk mesin chatbot (tanpa Flask)."""
from pathlib import Path

import pytest

from chatbot.engine import ChatbotEngine, load_themes, preprocess, similarity

THEMES = load_themes(Path(__file__).resolve().parent.parent / "themes")


def test_preprocess_normalisasi_dan_stopword():
    # "gimana"->"bagaimana", "kak" dan "ya" dibuang, "ikan" termasuk stopword tema ini
    assert preprocess("Gimana cara ganti air ikan, kak?") == ["bagaimana", "cara", "ganti", "air"]


def test_preprocess_kata_gaul_tema_ikan():
    assert preprocess("airnya keruh nggak?") == ["air", "keruh", "tidak"]


def test_similarity_kalimat_sama_bernilai_satu():
    t = ["ganti", "air"]
    assert similarity(t, t) == 1.0


def test_similarity_kalimat_berbeda_rendah():
    assert similarity(["cupang"], ["ganti", "air"]) < 0.3


def test_tema_ikan_termuat():
    assert "ikan" in THEMES
    assert THEMES["ikan"]["bot_name"] == "BlubBot"


@pytest.mark.parametrize("pesan, intent", [
    ("halo blubbot", "greeting"),
    ("ikan hias apa yang gampang dipelihara", "pilih_ikan_pemula"),
    ("akuarium berapa liter yang cukup buat cupang", "ukuran_akuarium"),
    ("jadwal makan ikan hias", "jadwal_makan"),
    ("pakan yang bagus buat guppy apa", "jenis_pakan"),
    ("seminggu berapa kali ganti air", "ganti_air"),
    ("boleh pakai air keran buat ikan", "air_keran"),
    ("kenapa air akuarium jadi keruh", "air_keruh"),
    ("suhu air yang pas buat cupang berapa", "suhu_air"),
    ("ikan megap megap di permukaan", "ikan_megap_megap"),
    ("ikanku ada bintik putih di badan", "bintik_putih"),
    ("cupang boleh digabung sama guppy", "campur_ikan"),
    ("dosis obat buat ikan berapa", "tanya_obat_dosis"),
    ("makasih banyak ya bot", "terima_kasih"),
])
def test_klasifikasi_intent(pesan, intent):
    engine = ChatbotEngine(THEMES["ikan"])
    tag, _ = engine.classify(pesan)
    assert tag == intent


def test_setiap_pola_dikenali_sebagai_intent_sendiri():
    """Setiap pola di ikan.json harus menghasilkan intent tempat ia ditulis."""
    engine = ChatbotEngine(THEMES["ikan"])
    for intent in THEMES["ikan"]["intents"]:
        for pola in intent["patterns"]:
            assert engine.classify(pola)[0] == intent["tag"], pola


def test_salah_ketik_masih_dikenali():
    engine = ChatbotEngine(THEMES["ikan"])
    tag, _ = engine.classify("jadwl makan ikan")
    assert tag == "jadwal_makan"


def test_pertanyaan_di_luar_tema_memberi_fallback():
    engine = ChatbotEngine(THEMES["ikan"])
    hasil = engine.reply("siapa presiden indonesia")
    assert hasil["intent"] is None
    assert hasil["reply"] in THEMES["ikan"]["fallback"]


def test_pesan_kosong_tidak_error():
    hasil = ChatbotEngine(THEMES["ikan"]).reply("   ")
    assert hasil["intent"] is None and hasil["score"] == 0.0


def test_jawaban_berasal_dari_daftar_respons_intent():
    tema = THEMES["ikan"]
    engine = ChatbotEngine(tema)
    hasil = engine.reply("kenapa air akuarium jadi keruh")
    respons = next(i["responses"] for i in tema["intents"] if i["tag"] == "air_keruh")
    assert hasil["reply"] in respons


def test_explain_mengurutkan_kandidat_dari_skor_tertinggi():
    engine = ChatbotEngine(THEMES["ikan"])
    kandidat = engine.explain("kenapa air akuarium jadi keruh")
    assert kandidat[0]["intent"] == "air_keruh"
    skor = [k["score"] for k in kandidat]
    assert skor == sorted(skor, reverse=True)
    assert len(kandidat) == 3


def test_validate_theme_menemukan_kesalahan():
    from chatbot.engine import validate_theme
    rusak = {"id": "x", "name": "X", "bot_name": "B", "avatar": "*", "color": "#000",
             "description": "d", "greeting": "g", "suggestions": [], "fallback": ["f"],
             "intents": [{"tag": "a", "patterns": ["halo"], "responses": ["hai"]},
                         {"tag": "b", "patterns": ["halo"], "responses": []}]}
    masalah = validate_theme(rusak)
    assert any("responses kosong" in m for m in masalah)
    assert any("'a' dan 'b'" in m for m in masalah)


def test_tema_ikan_valid():
    from chatbot.engine import validate_theme
    assert validate_theme(THEMES["ikan"]) == []


def test_tema_ikan_punya_cukup_intent_dan_respons():
    intents = THEMES["ikan"]["intents"]
    assert len(intents) >= 10
    for intent in intents:
        assert len(intent["responses"]) >= 2, intent["tag"]


def test_akurasi_data_uji_ikan_minimal_90_persen():
    from evaluate import baca_data, evaluasi
    akurasi, _ = evaluasi(THEMES["ikan"], baca_data("ikan"), 0.45)
    assert akurasi >= 0.9
