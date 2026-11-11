"""Uji integrasi route Flask menggunakan test client."""
import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    # Database sementara agar pengujian tidak mengotori data asli
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})
    return app.test_client()


def test_halaman_utama_adalah_landing_page(client):
    res = client.get("/")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "BlubBot" in html
    assert 'href="/chat/ikan"' in html          # tombol menuju chat
    assert "Pilih Tema" not in html             # tidak ada pilihan tema


def test_halaman_chat(client):
    res = client.get("/chat/ikan")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "BlubBot" in html
    assert "Mode belajar" in html              # checkbox mode belajar ada
    assert "Praktikum" not in html             # footer sudah dihapus
    assert "Statistik" not in html             # tombol statistik sudah dihapus


def test_tema_tidak_ada_404(client):
    assert client.get("/chat/tidak-ada").status_code == 404
    assert client.get("/api/history/tidak-ada").status_code == 404


def test_api_themes(client):
    data = client.get("/api/themes").get_json()
    assert [t["id"] for t in data] == ["ikan"]


def test_api_chat_berhasil(client):
    res = client.post("/api/chat", json={"message": "kenapa air akuarium keruh", "theme": "ikan"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["intent"] == "air_keruh"
    assert data["reply"]


@pytest.mark.parametrize("payload", [
    {"message": "", "theme": "ikan"},
    {"message": "halo", "theme": "salah"},
    {"message": "a" * 501, "theme": "ikan"},
    {},
])
def test_api_chat_input_tidak_valid(client, payload):
    assert client.post("/api/chat", json=payload).status_code == 400


def test_riwayat_tersimpan_dan_bisa_dihapus(client):
    client.post("/api/chat", json={"message": "halo", "theme": "ikan"})
    riwayat = client.get("/api/history/ikan").get_json()
    assert [r["sender"] for r in riwayat] == ["user", "bot"]

    client.delete("/api/history/ikan")
    assert client.get("/api/history/ikan").get_json() == []


def test_statistik_intent(client):
    client.post("/api/chat", json={"message": "halo", "theme": "ikan"})
    stats = client.get("/api/stats/ikan").get_json()
    assert stats[0]["intent"] == "greeting"


def test_api_explain(client):
    data = client.post("/api/explain", json={"message": "kenapa air akuarium keruh", "theme": "ikan"}).get_json()
    assert data["threshold"] == 0.45
    assert data["candidates"][0]["intent"] == "air_keruh"


def test_halaman_admin_menampilkan_pertanyaan_tak_dikenali(client):
    client.post("/api/chat", json={"message": "harga bensin berapa", "theme": "ikan"})
    html = client.get("/admin/ikan").get_data(as_text=True)
    assert "harga bensin berapa" in html
    assert "tidak dikenali" in html


def test_admin_key_melindungi_halaman_admin(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "t.db"), "ADMIN_KEY": "rahasia"})
    c = app.test_client()
    assert c.get("/admin/ikan").status_code == 403
    assert c.get("/api/stats/ikan").status_code == 403
    assert c.get("/admin/ikan?key=rahasia").status_code == 200


def test_logo_dan_aset_statis_tersedia(client):
    assert client.get("/static/img/logo.svg").status_code == 200
    assert client.get("/static/css/style.css").status_code == 200
    assert client.get("/static/js/chat.js").status_code == 200
    assert client.get("/static/js/dekorasi.js").status_code == 200
