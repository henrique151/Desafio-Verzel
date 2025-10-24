from pipefy_service import atualizar_card_com_reuniao

card_id = "1243592775"  # ID do card do lead
link_reuniao = "https://meet.google.com/exemplo"  # caso tenha link
data_reuniao = "2025-10-25T14:00:00-03:00"  # horário escolhido

resultado = atualizar_card_com_reuniao(card_id, link_reuniao, data_reuniao)
print(resultado)
