import os
import json
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from google.genai.errors import APIError

# Serviços
from app.services.pipefy_service import registrar_lead, atualizar_card_com_reuniao
from app.services.calendar_service import oferecer_horarios, agendar_reuniao

# 🔹 Inicialização FastAPI
app = FastAPI(title="SDR Elite Dev API")

# 🔹 Modelos Pydantic


class AgentRequest(BaseModel):
    prompt: str
    history: Optional[List[Dict[str, Any]]] = None


class AgentResponse(BaseModel):
    response: str
    history: List[Dict[str, Any]]


# 🔹 Configuração Gemini
try:
    client = genai.Client()
    MODEL_NAME = "gemini-2.0-flash"
except Exception as e:
    print(f"Erro ao inicializar Gemini: {e}")
    client = None

AVAILABLE_TOOLS = {
    "registrar_lead": registrar_lead,
    "atualizar_card_com_reuniao": atualizar_card_com_reuniao,
    "oferecer_horarios": oferecer_horarios,
    "agendar_reuniao": agendar_reuniao,
}

SDR_SYSTEM_INSTRUCTION = """
Você é o Agente SDR-Elite-Dev-IA...
"""

# 🔹 Função principal


def run_gemini_agent(history: List[Dict[str, Any]]) -> types.GenerateContentResponse:
    if client is None:
        raise Exception("Cliente Gemini não configurado.")

    gemini_contents = []
    for item in history:
        role = item.get("role", "user")
        parts_data = item.get("parts", [])
        gemini_parts = [types.Part(text=p["text"]) for p in parts_data if isinstance(
            p, dict) and p.get("text")]
        final_role = "model" if role == "tool" else role
        gemini_contents.append(types.Content(
            role=final_role, parts=gemini_parts))

    try:
        print("[DEBUG] Enviando requisição ao Gemini...")
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=gemini_contents,
            config=types.GenerateContentConfig(
                system_instruction=SDR_SYSTEM_INSTRUCTION,
                tools=list(AVAILABLE_TOOLS.values()),
            ),
        )
        print("[DEBUG] Gemini respondeu com sucesso.")
        return response
    except APIError as e:
        print(f"[ERROR] Falha na API Gemini: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na API Gemini: {e}")
    except Exception as e:
        print(f"[ERROR] Erro geral em run_gemini_agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 🔹 Rotas


@app.get("/")
def root():
    return {"message": "API SDR-Elite-Dev-IA está rodando 🚀"}


@app.post("/chat", response_model=AgentResponse)
def chat(request: AgentRequest):
    history = request.history or []
    history.append({"role": "user", "parts": [{"text": request.prompt}]})

    try:
        response = run_gemini_agent(history)
        reply_text = None

        if hasattr(response, "text") and response.text:
            reply_text = response.text
        elif getattr(response, "candidates", None):
            reply_text = response.candidates[0].content.parts[0].text
        else:
            reply_text = "[ERRO] Resposta vazia do Gemini."

        history.append({"role": "model", "parts": [{"text": reply_text}]})
        return AgentResponse(response=reply_text, history=history)

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"[ERROR] Exceção inesperada: {e}")
        raise HTTPException(status_code=500, detail=str(e))
