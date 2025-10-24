from pydantic import BaseModel, Field
from typing import List, Any, Optional


class HistoryPart(BaseModel):
    text: Optional[str] = None
    functionCall: Optional[dict] = Field(None, alias="function_call")
    functionResponse: Optional[dict] = Field(None, alias="function_response")


class HistoryItem(BaseModel):
    role: str = Field(...,
                      description="O papel na conversa (user, model, tool).")
    parts: List[dict] = Field(...,
                              description="O conteúdo da mensagem (principalmente o texto).")


class AgentRequest(BaseModel):
    prompt: str = Field(..., description="A nova mensagem do usuário.")
    history: Optional[List[dict]] = Field(
        None, description="Histórico da conversa anterior.")


class AgentResponse(BaseModel):
    response: str = Field(..., description="A resposta de texto do Agente.")
    history: List[dict] = Field(...,
                                description="Histórico completo e atualizado da conversa.")
