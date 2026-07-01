# Como rodar o LLMart

Guia passo a passo, do clone do repositório até rodar um ataque adversarial de exemplo.

Cobre dois cenários:
- **Máquina com GPU NVIDIA** (ex: Windows + RTX XXXX) — mais rápido, recomendado para ataques completos
- **Máquina sem GPU dedicada** (ex: Linux com GPU integrada) — mais lento, útil para demonstrações rápidas com poucos passos

---

## 1. Pré-requisitos

- [`uv`](https://docs.astral.sh/uv/) instalado
- Uma conta no [Hugging Face](https://huggingface.co) e um token de acesso (Read) gerado em [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

### Instalar o `uv`

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Confirme a instalação:
```bash
uv --version
```

---

## 2. Clonar o repositório

```bash
git clone https://github.com/IntelLabs/LLMart
cd LLMart
```

> ⚠️ **Windows:** evite clonar em caminhos com acentos ou caracteres especiais (ex: `Área de Trabalho`). Isso causa erros de `UnicodeDecodeError` no `uv`. Prefira um caminho simples, tipo `C:\sorbet\LLMart`.

---

## 2.5. Sobre ativar o ambiente virtual

Diferente do fluxo tradicional com `python -m venv` + `pip`, **você não precisa ativar o venv manualmente** para usar os comandos deste guia. Todo comando prefixado com `uv run` já executa automaticamente dentro do ambiente virtual do projeto (`.venv`), sem precisar de `source .venv/bin/activate` (Linux/macOS) ou `.venv\Scripts\Activate.ps1` (Windows) antes.

Isso só passa a importar se você quiser rodar comandos **sem** o prefixo `uv run` (por exemplo, digitar só `accelerate launch ...` ou `python ...` direto, sem `uv run` na frente). Nesse caso, ative o ambiente antes:

**Linux/macOS:**
```bash
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

Você saberá que está ativado quando o prompt do terminal mostrar `(.venv)` no início da linha. Se preferir esse fluxo, pode ativar uma vez por sessão de terminal e então omitir o `uv run` dos comandos abaixo (ex: `accelerate launch -m llmart ...` em vez de `uv run accelerate launch -m llmart ...`).

Este guia usa `uv run` em todos os comandos justamente para funcionar igual, ativado ou não.

---

## 3. Instalar as dependências

Isso muda dependendo do hardware disponível.

### Opção A — GPU NVIDIA (recomendado, ataques completos)

O `pyproject.toml` do projeto não vem com um índice CUDA explícito para o extra `gpu`, então o `uv` pode instalar a build **CPU-only** do PyTorch por engano. É necessário editar o arquivo antes de instalar.

Abra `pyproject.toml` e localize:
```toml
[tool.uv.sources]
torch = [
    { index = "pytorch-xpu", extra = "xpu" },
]
```

Substitua por (adicionando a entrada para CUDA):
```toml
[tool.uv.sources]
torch = [
    { index = "pytorch-cu126", extra = "gpu" },
    { index = "pytorch-xpu", extra = "xpu" },
]
```

E adicione um novo índice, próximo à definição do `pytorch-xpu`:
```toml
[[tool.uv.index]]
name = "pytorch-cu126"
url = "https://download.pytorch.org/whl/cu126"
explicit = true
```

Instale:
```bash
uv sync --extra gpu
```

Valide que a GPU foi reconhecida:
```bash
uv run python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
```
Deve aparecer algo como `2.8.0+cu126` e `True`.

### Opção B — GPU Intel (Arc ou Iris Xe — **não** funciona em UHD Graphics/gráficos integrados mais antigos)

```bash
uv sync --extra xpu
```

Valide:
```bash
uv run python -c "import torch; print(torch.__version__); print(torch.xpu.is_available())"
```

### Opção C — Sem GPU dedicada (CPU)

O projeto não tem um extra `cpu` pronto — é preciso instalar o `core` (dependências gerais) e o PyTorch CPU-only separadamente:

```bash
uv sync --extra core
uv pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cpu
```

Valide:
```bash
uv run python -c "import torch; print(torch.__version__)"
```
Deve aparecer `2.8.0+cpu`.

> ⚠️ Rodar em CPU é **muito mais lento** — inviável para um ataque completo (pode levar horas). Útil só para demonstrar o processo rodando, com poucos passos (`steps=5` a `steps=20`).

---

## 4. Configurar o token do Hugging Face

**Linux/macOS:**
```bash
export HF_TOKEN=hf_seu_token_aqui
```

**Windows (PowerShell):**
```powershell
$env:HF_TOKEN = "hf_seu_token_aqui"
```

> Isso vale só para a sessão atual do terminal. Repita sempre que abrir um terminal novo, ou defina como variável de ambiente permanente do sistema.

Se for usar um modelo "gated" (que exige aceite de licença, como o Llama-3), acesse a página do modelo no Hugging Face Hub e aceite os termos antes de rodar — caso contrário, dará erro `403 GatedRepoError`. Modelos abertos (como o usado no exemplo abaixo) não têm essa exigência.

---

## 5. Rodar um exemplo

O `data=basic` usa o exemplo padrão do repositório: forçar o modelo a responder "NO WAY JOSE" a uma pergunta sobre o planeta Saturno.

**Com GPU (NVIDIA ou Intel), ataque completo:**
```bash
uv run accelerate launch -m llmart model=custom model.name=Qwen/Qwen2.5-1.5B-Instruct model.revision=main data=basic
```

**Sem GPU (CPU), demo rápida:**
```bash
uv run accelerate launch -m llmart model=custom model.name=Qwen/Qwen2.5-1.5B-Instruct model.revision=main data=basic steps=5 model.device=cpu
```

> O modelo `Qwen/Qwen2.5-1.5B-Instruct` foi escolhido por ser pequeno (~3GB) e aberto (não-gated) — cabe confortavelmente em GPUs com 8GB de VRAM e não exige aprovação de licença.

### Parâmetros úteis

| Parâmetro | O que faz | Padrão |
|---|---|---|
| `steps` | Número de iterações de otimização do GCG | 500 |
| `model.device` | Força o dispositivo (`cuda`, `cpu`, `xpu`) | detecção automática |
| `per_device_bs` | Tamanho do batch (reduza se der erro de memória) | depende do modelo |
| `model.revision` | Commit/branch do modelo no Hugging Face (obrigatório com `model=custom`) | — |

---

## 6. Ver os resultados

Os resultados ficam salvos em `outputs/llmart/<data>/<hora>/`, como checkpoints `.pt` do PyTorch. O sufixo adversarial encontrado aparece nos próprios logs do terminal, no campo `prompt=` de cada bloco `TEST @ ...`.

Para visualizar a curva de loss ao longo dos passos:
```bash
uv run tensorboard --logdir=outputs/llmart
```
Depois abra `http://localhost:6006` no navegador.

---

## Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| `UnicodeDecodeError: 'charmap' codec...` | Caminho do projeto com acentos (Windows) | Clone em um caminho sem acentos/caracteres especiais |
| `AssertionError: Torch not compiled with CUDA enabled` | PyTorch instalado é CPU-only | Siga a Opção A da seção 3 (editar `pyproject.toml`) |
| `GatedRepoError: 403 Client Error` | Modelo exige aceite de licença no Hugging Face | Acesse a página do modelo e aceite os termos, ou use um modelo aberto |
| `error: Failed to spawn: accelerate` | Dependências não instaladas (extra errado ou sync não rodou) | Confirme que rodou `uv sync` com o extra certo para seu hardware |
| `curl: (22) ... 404` ao instalar o `uv` | URL de instalação incompleta | Use `https://astral.sh/uv/install.sh` (não esqueça o `/uv/`) |
