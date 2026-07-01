"""
Script de calibração: imprime a perplexidade real de cada exemplo
(adversarial e benigno) para ajudar a escolher um threshold correto.

Rode com:
    uv run python calibrate_threshold.py
"""

import json
from pathlib import Path

from guardrail import compute_perplexity

fixtures = json.loads(
    (Path(__file__).parent / "fixtures" / "adversarial_examples.json").read_text(encoding="utf-8")
)

print("=== Prompts ADVERSARIAIS (deveriam ter perplexidade ALTA) ===")
results_adv = []
for attack in fixtures["known_attacks"]:
    text = attack["prompt"] + attack["adversarial_suffix"]
    ppl = compute_perplexity(text)
    results_adv.append(ppl)
    print(f"{attack['name']:30s} perplexity = {ppl:.2f}")

print("\n=== Prompts BENIGNOS (deveriam ter perplexidade BAIXA) ===")
results_benign = []
for prompt in fixtures["benign_prompts"]:
    ppl = compute_perplexity(prompt)
    results_benign.append(ppl)
    print(f"{prompt[:40]:40s} perplexity = {ppl:.2f}")

print("\n=== Sugestão ===")
min_adv = min(results_adv)
max_benign = max(results_benign)
print(f"Menor perplexidade adversarial: {min_adv:.2f}")
print(f"Maior perplexidade benigna:     {max_benign:.2f}")

if min_adv > max_benign:
    suggested = (min_adv + max_benign) / 2
    print(f"\nOK! Há separação clara. Threshold sugerido: {suggested:.1f}")
else:
    print(
        "\nXX_XX Os grupos se sobrepõem — não existe um único threshold que "
        "separe perfeitamente todos os exemplos atuais. Considere trocar "
        "o exemplo mais fraco por outro com perplexidade mais alta."
    )
