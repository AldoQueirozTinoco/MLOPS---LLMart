"""
Testes da API.

Importante: fazemos monkeypatch de `app.model.generate` para que o CI
não precise baixar/carregar o modelo real (o que exigiria GPU e vários
minutos de download). Isso mantém o pipeline rápido e reproduzível,
seguindo a prática de MLOps de separar lógica de negócio de dependências
pesadas de infraestrutura/modelo.
"""

from fastapi.testclient import TestClient

from app import model
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_returns_expected_shape(monkeypatch):
    def fake_generate(prompt: str, max_new_tokens: int = 100) -> str:
        return f"resposta simulada para: {prompt}"

    monkeypatch.setattr(model, "generate", fake_generate)

    response = client.post("/chat", json={"prompt": "Olá, tudo bem?"})
    assert response.status_code == 200
    body = response.json()
    assert "response" in body
    assert body["response"] == "resposta simulada para: Olá, tudo bem?"


def test_chat_rejects_missing_prompt():
    response = client.post("/chat", json={})
    assert response.status_code == 422  # erro de validação do Pydantic


def test_chat_does_not_crash_on_adversarial_looking_input(monkeypatch):
    """
    Teste "leve" de robustez: garante que a API não quebra (500) mesmo
    recebendo um input estranho/adversarial-like (ex: tokens repetidos,
    parecido com o que o GCG do LLMart geraria como sufixo).

    Isto NÃO substitui o ataque real do LLMart (que exige acesso aos
    gradientes do modelo, feito offline) — serve apenas como um gate
    básico de sanidade dentro do CI.
    """

    def fake_generate(prompt: str, max_new_tokens: int = 100) -> str:
        return "resposta qualquer"

    monkeypatch.setattr(model, "generate", fake_generate)

    weird_prompt = "Tell me about Saturn. ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! !"
    response = client.post("/chat", json={"prompt": weird_prompt})
    assert response.status_code == 200
