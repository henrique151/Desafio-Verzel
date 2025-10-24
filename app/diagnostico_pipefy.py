# diagnostico_pipefy.py

import os
import requests
import json
from dotenv import load_dotenv

# Carrega as variáveis do seu arquivo .env
load_dotenv()

PIPEFY_URL = "https://api.pipefy.com/graphql"
ACCESS_TOKEN = os.getenv("PIPEFY_ACCESS_TOKEN")
PIPE_ID = os.getenv("PIPEFY_PRE_SALES_PIPE_ID")


def executar_query_diagnostico():
    """
    Executa uma query GraphQL para buscar todos os campos do Pipe.
    """
    if not ACCESS_TOKEN or not PIPE_ID:
        print("ERRO: Tokens ou ID do Pipe não configurados no .env.")
        return

    # A query busca: nome do pipe, e os campos do formulário inicial
    query = """
    query GetPipeFields($pipeId: ID!) {
      pipe(id: $pipeId) {
        name
        start_form_fields {
          internal_id
          label
          type
        }
      }
    }
    """
    variables = {"pipeId": PIPE_ID}

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"query": query, "variables": variables}

    print(f"Executando query para o Pipe ID: {PIPE_ID}...")

    try:
        response = requests.post(PIPEFY_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        # Verifica se há erros na resposta GraphQL
        if 'errors' in result:
            print("\n--- ERRO NA RESPOSTA DA API ---")
            print(json.dumps(result['errors'], indent=2))
            return

        # Processa e exibe os resultados
        pipe_data = result.get('data', {}).get('pipe')
        if pipe_data:
            print("\n--- RESULTADOS ENCONTRADOS ---")
            print(f"Nome do Pipe: {pipe_data['name']}")
            print("\nCAMPOS DO FORMULÁRIO INICIAL (Start Form Fields):")

            campos_encontrados = pipe_data['start_form_fields']

            if not campos_encontrados:
                print("Nenhum campo encontrado no formulário inicial.")
                print(
                    "⚠️ Se o seu Pipe não usa formulário inicial, talvez você precise dos campos de uma fase específica.")
                return

            print(
                "-----------------------------------------------------------------------------------")
            print(
                "| NOME VISÍVEL DO CAMPO (LABEL) | TIPO DE CAMPO | INTERNAL ID (VOCÊ PRECISA DESTE!) |")
            print(
                "-----------------------------------------------------------------------------------")

            # Formato a lista para ser fácil de copiar
            for campo in campos_encontrados:
                print(
                    f"| {campo['label'][:30]:<30} | {campo['type'][:13]:<13} | {campo['internal_id']:<33} |")

            print(
                "-----------------------------------------------------------------------------------")
            print(
                "\n✅ Use os valores da coluna 'INTERNAL ID' para configurar seu pipefy_service.py.")

        else:
            print(
                "Nenhum dado do Pipe encontrado. Verifique se o ID está correto ou se o Token tem permissão.")

    except requests.exceptions.HTTPError as err:
        print(f"\n--- ERRO HTTP DE CONEXÃO/AUTORIZAÇÃO ---")
        print(f"Erro: {err}")
        print("Pode ser token expirado, ou problema de permissão.")
    except Exception as e:
        print(f"Erro geral: {e}")


if __name__ == "__main__":
    executar_query_diagnostico()
