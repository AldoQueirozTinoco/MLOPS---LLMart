"""
Guardrail baseado em perplexidade.

Referência conceitual: Alon & Kamfonas (2023), "Detecting Language Model
Attacks with Perplexity" — sufixos otimizados por GCG (como os que o
LLMart gera) tendem a ter perplexidade muito mais alta que texto humano
natural, porque são sequências de tokens escolhidas para maximizar um
gradiente, não para fazer sentido linguístico.

Este módulo é independente de qualquer API — só a lógica de detecção,
para poder ser testada isoladamente e rapidamente no CI.
"""

import os
from functools import lru_cache

MODEL_NAME = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-1.5B-Instruct")


@lru_cache(maxsize=1)
def _get_scoring_model():
    """Carrega tokenizer + modelo uma única vez (cache/singleton)."""
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    model.eval()
    return tokenizer, model


def compute_perplexity(text: str) -> float:
    """Calcula a perplexidade de `text` sob o modelo local."""
    import torch

    tokenizer, model = _get_scoring_model()

    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs, labels=inputs["input_ids"])

    return torch.exp(outputs.loss).item()


def is_adversarial(text: str, threshold: float = 100.0) -> bool:
    """
    Retorna True se o texto for suspeito de conter um sufixo
    adversarial (perplexidade acima do limiar).

    ⚠️ O valor threshold=100.0 é um ponto de partida. Rode os testes
    localmente (pytest tests/ -v) antes da apresentação para confirmar
    que ele separa bem os exemplos de fixtures/adversarial_examples.json
    — se algum teste falhar, ajuste o threshold aqui.
    """
    return compute_perplexity(text) > threshold
