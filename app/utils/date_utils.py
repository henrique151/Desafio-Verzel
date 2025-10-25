import dateparser
from datetime import datetime


def normalizar_data(texto_data: str) -> str:
    """
    Converte uma data escrita de forma natural (ex: '21/10/2025 às 19:00')
    para o formato ISO 8601 aceito pelo Pipefy.
    """

    if not texto_data or not isinstance(texto_data, str):
        raise ValueError("Data inválida ou vazia.")

    # Substitui 'às' por um espaço para facilitar a interpretação de hora
    texto_para_parse = texto_data.replace('às', ' ')

    # Usa dateparser para interpretar a data em português
    parsed_date = dateparser.parse(
        texto_para_parse,
        languages=['pt'],
        settings={
            'TIMEZONE': 'America/Sao_Paulo',
            'RETURN_AS_TIMEZONE_AWARE': False,
            'PREFER_DATES_FROM': 'future'
        }
    )

    if not parsed_date:
        raise ValueError(f"Não foi possível interpretar a data: {texto_data}")

    # Retorna no formato ISO padrão aceito pelo Pipefy
    return parsed_date.strftime("%Y-%m-%dT%H:%M:%S")