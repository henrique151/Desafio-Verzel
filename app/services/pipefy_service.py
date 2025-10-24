import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

PIPEFY_URL = "https://api.pipefy.com/graphql"
ACCESS_TOKEN = os.getenv("PIPEFY_ACCESS_TOKEN")
PIPE_ID = os.getenv("PIPEFY_PRE_SALES_PIPE_ID")

# Cache para os IDs dos campos
_field_id_cache = {}

# Modo de simulação: ativo se não houver token ou contiver "SIMULACAO"
SIMULATION_MODE = not ACCESS_TOKEN or "SIMULACAO" in ACCESS_TOKEN.upper()


def _executar_query(query, variables=None):
    """Executa a requisição GraphQL no Pipefy"""
    if SIMULATION_MODE and "start_form_fields" not in query:
        print("[DEBUG] Modo de simulação ativo. Nenhuma chamada real ao Pipefy.")
        return {"data": {"createCard": {"card": {"id": "SIM_CARD_12345", "title": "Simulado"}}}}

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"query": query, "variables": variables or {}}

    try:
        response = requests.post(
            PIPEFY_URL, headers=headers, json=payload, timeout=10
        )
        response.raise_for_status()
        result = response.json()
        if "errors" in result:
            print("[ERROR] Pipefy retornou erros:",
                  json.dumps(result["errors"], indent=2))
        return result
    except Exception as e:
        print(f"[ERROR] Erro ao conectar com Pipefy: {e}")
        return {"error": str(e)}


def _get_field_ids():
    """Busca e cacheia os IDs dos campos do Start Form do Pipefy."""
    global _field_id_cache
    if _field_id_cache:
        return _field_id_cache

    query = """
    query GetPipeFields($pipeId: ID!) {
      pipe(id: $pipeId) {
        start_form_fields {
          id
          label
        }
      }
    }
    """
    variables = {"pipeId": PIPE_ID}
    result = _executar_query(query, variables)

    if result.get("error") or "errors" in result:
        raise Exception(
            "Não foi possível buscar os campos do Pipefy. Verifique o token e o ID do Pipe."
        )

    fields = result.get("data", {}).get(
        "pipe", {}).get("start_form_fields", [])
    if not fields:
        raise Exception("Nenhum campo encontrado no Start Form do Pipe.")

    # Mapeamento label -> key
    label_map = {
        "Nome": "nome",
        "Email": "email",
        "Empresa": "empresa",
        "Necessidade": "necessidade",
        "Interesse_confirmado": "interesse",
        "Meeting_link": "link_reuniao",
        "Data Reuniao": "data_reuniao"
    }

    for field in fields:
        label = field.get("label")
        internal_id = field.get("id")
        if label in label_map:
            key = label_map[label]
            _field_id_cache[key] = internal_id

    if len(_field_id_cache) < len(label_map):
        print("[WARNING] Nem todos os campos esperados foram encontrados no Pipefy. Funcionalidade pode ser limitada.")
        print(f"Campos encontrados: {list(_field_id_cache.keys())}")

    return _field_id_cache


def registrar_lead(nome: str, email: str, empresa: str, necessidade: str) -> str:
    """Cria um novo card (lead) no Pipefy."""
    if SIMULATION_MODE:
        simulated_card_id = "SIM_CARD_12345"
        return json.dumps({
            "status": "sucesso",
            "card_id": simulated_card_id,
            "email": email,
            "mensagem": "Lead registrado com sucesso (simulação)."
        })

    try:
        field_ids = _get_field_ids()
    except Exception as e:
        return str(e)

    # Validação do campo 'Necessidade' (select do Pipefy)
    necessidade_map = {
        "implementar ia": "Implementar IA",
        "automação": "Automação de Processos",
    }
    necessidade_value = necessidade_map.get(necessidade.lower())
    if not necessidade_value:
        return "Erro: Necessidade inválida. Escolha uma opção válida do Pipefy."

    # Campos do card
    fields = [
        {"field_id": field_ids["nome"], "field_value": nome},
        {"field_id": field_ids["email"], "field_value": email},
        {"field_id": field_ids["empresa"], "field_value": empresa},
        {"field_id": field_ids["necessidade"],
            "field_value": necessidade_value},
        {"field_id": field_ids["interesse"], "field_value": "Sim"},
    ]

    # Mutation GraphQL
    mutation = """
    mutation CreateCard($input: CreateCardInput!) {
      createCard(input: $input) {
        card {
          id
          title
        }
      }
    }
    """
    variables = {"input": {"pipe_id": PIPE_ID, "fields_attributes": fields}}
    result = _executar_query(mutation, variables)

    if result.get("data") and result["data"].get("createCard"):
        card_id = result["data"]["createCard"]["card"]["id"]
        return json.dumps({
            "status": "sucesso",
            "card_id": card_id,
            "email": email,
            "mensagem": "Lead registrado com sucesso. Próximo passo: oferecer horários de reunião."
        })
    else:
        return f"Falha ao criar card no Pipefy. Detalhes: {json.dumps(result)}"


def atualizar_card_com_reuniao(card_id: str, link: str, datetime_str: str) -> str:
    if SIMULATION_MODE:
        return json.dumps({
            "status": "sucesso",
            "card_id": card_id,
            "mensagem": f"Card {card_id} atualizado com link e data (simulação)."
        })

    try:
        field_ids = _get_field_ids()
    except Exception as e:
        return str(e)

    def atualizar_campo(field_id, value):
        mutation = """
        mutation UpdateCardField($input: UpdateCardFieldInput!) {
            updateCardField(input: $input) {
                card { id }
                success
            }
        }
        """
        variables = {"input": {"card_id": card_id,
                               "field_id": field_id, "new_value": value}}
        return _executar_query(mutation, variables)

    # Atualiza link da reunião
    res_link = atualizar_campo(field_ids["link_reuniao"], link)
    # Atualiza data da reunião
    res_data = atualizar_campo(field_ids["data_reuniao"], datetime_str)

    if res_link.get("data") and res_link["data"].get("updateCardField") and \
       res_data.get("data") and res_data["data"].get("updateCardField"):
        return f"Card {card_id} atualizado com link e data da reunião."
    else:
        return f"Falha ao atualizar card {card_id}. Detalhes: link={json.dumps(res_link)}, data={json.dumps(res_data)}"
