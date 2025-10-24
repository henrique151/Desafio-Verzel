import os
import json
from google import genai
from google.genai import types
from google.genai.errors import APIError
from fastapi import HTTPException
from typing import List, Dict, Any, Union
from pydantic import BaseModel  # Mantenha Pydantic para o Main.py usar

# Importa as funções de serviço que o Gemini pode "chamar"
from .pipefy_service import registrar_lead, atualizar_card_com_reuniao
from .calendar_service import oferecer_horarios, agendar_reuniao

# 1. Configuração do Cliente Gemini
try:
    client = genai.Client()
    MODEL_NAME = "gemini-2.5-flash"
except Exception as e:
    print(
        f"Erro ao inicializar o cliente Gemini. Verifique GEMINI_API_KEY: {e}")
    client = None

# Mapeamento de Funções: O Gemini retorna a função por nome, precisamos executá-la
# APENAS para o Gemini conhecer as ferramentas. A execução fica no main.py
AVAILABLE_TOOLS = {
    "registrar_lead": registrar_lead,
    "atualizar_card_com_reuniao": atualizar_card_com_reuniao,
    "oferecer_horarios": oferecer_horarios,
    "agendar_reuniao": agendar_reuniao,
}

# 2. Definição do Agente e Instruções do Sistema (System Instruction)
SDR_SYSTEM_INSTRUCTION = """
Você é o Agente SDR-Elite-Dev-IA, um assistente de pré-vendas altamente competente e profissional.
Seu objetivo é seguir estritamente os seguintes passos:
1.  **Qualificar o Lead:** Obtenha o nome completo, e-mail, nome da empresa e a necessidade do cliente.
2.  **Registrar o Lead:** Assim que tiver as 4 informações, use a ferramenta `registrar_lead`. O resultado desta ferramenta conterá um `card_id`.
3.  **Oferecer Horários:** Imediatamente após o registro bem-sucedido, use a ferramenta `oferecer_horarios` para mostrar as opções de reunião ao cliente.
4.  **Agendar a Reunião:** Quando o cliente escolher um horário, use a ferramenta `agendar_reuniao`. Você **DEVE** usar o `card_id` obtido no passo 2 como argumento para esta função. Não peça as informações do cliente novamente.

**Regras estritas:**
- Seja educado, proativo e claro.
- **Seja conciso.** Não adicione texto desnecessário.
- Se o próximo passo for uma chamada de ferramenta, **NUNCA** gere texto antes dela.
"""

# 3. Função Principal de Conversação (AGORA SEM O LOOP INTERNO)
# Recebe o histórico COMPLETO (incluindo o prompt do usuário)


def run_gemini_agent(history: List[Dict[str, Any]]) -> types.GenerateContentResponse:
    """
    Gerencia a interação com o modelo Gemini usando o histórico fornecido.
    Retorna a resposta bruta do Gemini (que pode conter function_calls ou texto).
    """
    if client is None:
        raise Exception("Erro de configuração da API Gemini.")

    # Bloco de Reconstrução CORRIGIDO E SIMPLIFICADO para usar o formato do main.py
    gemini_contents = []

    for item in history:
        gemini_parts = []
        role = item['role']

        for p in item.get('parts', []):
            if p.get('text'):
                gemini_parts.append(types.Part(text=p['text']))

            elif p.get('functionCall'):
                call_data = p['functionCall']
                gemini_parts.append(types.Part.from_function_call(
                    types.FunctionCall(
                        name=call_data['name'],
                        args=call_data['args']
                    )
                ))

            elif p.get('functionResponse'):
                response_data = p['functionResponse']
                # O Main.py garante que response_data['response'] é um dict
                response_dict = response_data['response']

                gemini_parts.append(types.Part.from_function_response(
                    name=response_data['name'],
                    response=response_dict
                ))

        if gemini_parts:
            # Atenção: O Python client espera 'user' ou 'model' (que inclui 'tool')
            # Mapeamos 'tool' para 'model' ou ajustamos o role
            if role == 'tool':
                role = 'model'  # O SDK do Gemini lida com o role 'tool'

            gemini_contents.append(types.Content(
                role=role, parts=gemini_parts))

    # A última iteração é a mais importante
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=gemini_contents,
            config=types.GenerateContentConfig(
                system_instruction=SDR_SYSTEM_INSTRUCTION,
                tools=list(AVAILABLE_TOOLS.values()),
            ),
        )
        return response
    except APIError as e:
        error_message = f"Erro na API Gemini: {e}. Verifique sua chave API."
        print(f"[ERROR] {error_message}")
        raise HTTPException(status_code=500, detail=error_message)
