"""
Camada de acesso ao modelo de linguagem.

Mantida separada do main.py de propósito: assim conseguimos "mockar"
essa camada nos testes (tests/test_api.py) sem precisar baixar/carregar
o modelo real durante o CI, o que seria lento e exigiria GPU.
"""

import os
from functools import lru_cache

# Nome do modelo pode ser sobrescrito por variável de ambiente.
# Default: modelo pequeno o suficiente para caber em 8GB de VRAM
# (mesmo modelo usado no ataque adversarial com LLMart, para que a
# demo seja consistente: o que quebra offline, quebra aqui também).
MODEL_NAME = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-1.5B-Instruct")
DEVICE = os.environ.get("MODEL_DEVICE", "cuda")  # "cuda" ou "cpu"


@lru_cache(maxsize=1)
def _get_pipeline():
    """
    Carrega o pipeline de geração de texto uma única vez (singleton via cache).
    Import feito dentro da função para não pesar o import do módulo em
    ambientes (como o CI) onde essa função nunca chega a ser chamada.
    """
    from transformers import pipeline

    return pipeline(
        "text-generation",
        model=MODEL_NAME,
        device_map=DEVICE if DEVICE == "cuda" else None,
    )


def generate(prompt: str, max_new_tokens: int = 100) -> str:
    """
    Gera uma resposta do modelo para o prompt informado.

    Esta é a função que os testes fazem monkeypatch para evitar
    carregar o modelo real durante o CI.
    """
    pipe = _get_pipeline()
    conversation = [{"role": "user", "content": prompt}]
    output = pipe(conversation, max_new_tokens=max_new_tokens, do_sample=False)

    # A estrutura de retorno do pipeline de chat do transformers
    # aninha o texto gerado dentro de generated_text -> lista de turnos.
    generated = output[0]["generated_text"]
    if isinstance(generated, list):
        return generated[-1]["content"]
    return str(generated)
