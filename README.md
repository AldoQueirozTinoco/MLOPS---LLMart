# LLMart Demo API

API mínima em FastAPI que serve respostas de um LLM em um endpoint HTTP,
usada como caso prático para demonstrar o **LLMart** (LLM Adversarial
Robustness Toolkit) em uma apresentação de MLOps.

## Rodando localmente

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
pip install -r requirements.txt

uvicorn app.main:app --reload
```

Testar o endpoint:

```bash
curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d "{\"prompt\": \"Me fale sobre o planeta Saturno.\"}"
```

## Rodando os testes

```bash
pytest tests/ -v
```

Os testes usam `monkeypatch` para simular a resposta do modelo — o CI
não baixa nem carrega o modelo real, então roda em segundos e sem GPU.

## Roteiro da demonstração (MLOps + LLMart)

O objetivo é mostrar como um teste de robustez adversarial se encaixa
num pipeline real de MLOps, não só como um script isolado.

1. **Suba a API localmente** e mostre o endpoint `/chat` respondendo
   normalmente a um prompt comum (ex: pergunta sobre Saturno).

2. **Rode o LLMart separadamente**, atacando o **mesmo modelo**
   (`MODEL_NAME` neste projeto deve ser o mesmo usado no comando do
   LLMart) para gerar um sufixo adversarial:

   ```bash
   uv run accelerate launch -m llmart model=custom model.name=Qwen/Qwen2.5-1.5B-Instruct model.revision=<hash> data=basic
   ```

   > Importante para explicar na apresentação: o LLMart ataca o modelo
   > **localmente**, com acesso direto aos pesos/gradientes (ataque
   > *white-box*). Ele não ataca a API por fora — isso não seria
   > possível, já que uma API só expõe texto, não gradientes.

3. **Pegue o sufixo adversarial** que o LLMart encontrou (algo tipo
   `Tell me about Saturn. ! ! ! ! ...` otimizado) e envie esse mesmo
   prompt para a API rodando (`/chat`), mostrando ao vivo que o
   comportamento indesejado também aparece no serviço "em produção".
   Isso demonstra a *transferência* do ataque do ambiente offline para
   o serviço real.

4. **Altere algo no código** (ex: o prompt de sistema em `app/main.py`,
   ou adicione uma checagem simples de input) como tentativa de
   mitigação.

5. **Dê push** e mostre o **workflow do GitHub Actions** rodando os
   testes automaticamente (`.github/workflows/ci.yml`), fechando o
   ciclo: mudança de código → validação automática → confiança para
   deploy.

## Estrutura

```
llmart-demo-api/
├── app/
│   ├── main.py     # endpoints FastAPI
│   └── model.py    # carregamento do modelo (lazy, mockável em testes)
├── tests/
│   └── test_api.py
├── .github/workflows/ci.yml
└── requirements.txt
```
