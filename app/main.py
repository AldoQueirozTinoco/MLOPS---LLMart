"""
API mínima que serve respostas de um LLM em um endpoint HTTP.

Rode localmente com:
    uvicorn app.main:app --reload

Endpoints:
    GET  /health          -> healthcheck simples
    POST /chat             -> {"prompt": "..."} -> {"response": "..."}
"""

from fastapi import FastAPI
from pydantic import BaseModel

from app import model

app = FastAPI(
    title="LLMart Demo API",
    description="API de demonstração para testar robustez adversarial com LLMart",
    version="1.0.0",
)


class ChatRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 100


class ChatResponse(BaseModel):
    response: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    reply = model.generate(request.prompt, max_new_tokens=request.max_new_tokens)
    return ChatResponse(response=reply)
