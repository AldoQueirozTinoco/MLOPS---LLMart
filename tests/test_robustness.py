"""
Testa o guardrail de perplexidade contra exemplos adversariais
pré-escritos (fixtures/adversarial_examples.json).

Este teste carrega o modelo real (Qwen2.5-1.5B-Instruct) e roda em CPU
— não precisa de GPU, mas é mais lento que um teste comum (alguns
minutos, principalmente pelo download do modelo na primeira vez).
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from guardrail import is_adversarial  # noqa: E402

FIXTURES_PATH = Path(__file__).parent.parent / "fixtures" / "adversarial_examples.json"


def _load_fixtures() -> dict:
    with open(FIXTURES_PATH, encoding="utf-8") as f:
        return json.load(f)


fixtures = _load_fixtures()


@pytest.mark.parametrize(
    "attack",
    fixtures["known_attacks"],
    ids=[a["name"] for a in fixtures["known_attacks"]],
)
def test_known_adversarial_attack_is_detected(attack: dict):
    """Cada ataque conhecido deve ser sinalizado como adversarial."""
    malicious_prompt = attack["prompt"] + attack["adversarial_suffix"]

    assert is_adversarial(malicious_prompt), (
        f"O guardrail não detectou o ataque '{attack['name']}'. "
        f"Pode ser necessário ajustar o threshold em guardrail.py."
    )


@pytest.mark.parametrize("prompt", fixtures["benign_prompts"])
def test_benign_prompts_are_not_flagged(prompt: str):
    """Prompts legítimos não devem ser bloqueados (falso positivo)."""
    assert not is_adversarial(prompt), (
        f"Falso positivo: o guardrail bloqueou um prompt legítimo: '{prompt}'"
    )
