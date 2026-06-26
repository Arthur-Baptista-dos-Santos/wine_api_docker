import pytest
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

AMOSTRA_VALIDA = {
    "alcohol": 13.2,
    "malic_acid": 1.78,
    "ash": 2.14,
    "alcalinity_of_ash": 11.2,
    "magnesium": 100.0,
    "total_phenols": 2.65,
    "flavanoids": 2.76,
    "nonflavanoid_phenols": 0.26,
    "proanthocyanins": 1.28,
    "color_intensity": 4.38,
    "hue": 1.05,
    "od280_od315": 3.40,
    "proline": 1050.0,
}


def test_status():
    resposta = client.get("/")
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "online"


def test_health():
    resposta = client.get("/health")
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "healthy"


def test_classificar_retorna_classe_valida():
    resposta = client.post("/classificar", json=AMOSTRA_VALIDA)
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["classe"] in [0, 1, 2]
    assert "descricao" in dados
    assert "probabilidades" in dados


def test_classificar_probabilidades_somam_um():
    resposta = client.post("/classificar", json=AMOSTRA_VALIDA)
    probs = resposta.json()["probabilidades"]
    total = sum(probs.values())
    assert abs(total - 1.0) < 0.01


def test_classificar_campo_faltando():
    amostra_incompleta = {k: v for k, v in AMOSTRA_VALIDA.items() if k != "alcohol"}
    resposta = client.post("/classificar", json=amostra_incompleta)
    assert resposta.status_code == 422
