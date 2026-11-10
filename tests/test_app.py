import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "t.db")})
    return app.test_client()


def test_halaman_utama(client):
    assert client.get("/").status_code == 200


def test_api_chat_berhasil(client):
    res = client.post("/api/chat", json={"message": "jadwal makan ikan"})
    assert res.status_code == 200
    assert res.get_json()["intent"] == "jadwal_makan"


@pytest.mark.parametrize("payload", [{}, {"message": ""}, {"message": "a" * 501}])
def test_input_tidak_valid_kode_400(client, payload):
    assert client.post("/api/chat", json=payload).status_code == 400


def test_riwayat_tersimpan_dan_bisa_dihapus(client):
    client.post("/api/chat", json={"message": "halo"})
    assert len(client.get("/api/history").get_json()) == 2
    client.delete("/api/history")
    assert client.get("/api/history").get_json() == []