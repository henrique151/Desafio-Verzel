import json
from pipefy_service import atualizar_card_com_reuniao, registrar_lead

res = registrar_lead(
    nome="Vitor3",
    email="Vitor233@gmail.com",
    empresa="332Vitores",
    necessidade="Implementar IA"
)
card_id = json.loads(res)["card_id"]

resultado = atualizar_card_com_reuniao(
    card_id=card_id,
    link="https://meet.google.com/exemplo",
    datetime_str="2025-10-25 10:00"
)
print(resultado)
