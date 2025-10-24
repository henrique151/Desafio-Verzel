from pipefy_service import atualizar_card_com_reuniao

# ID do card que você acabou de criar
card_id = "1243575541"

# Link e data da reunião que você quer atualizar
link_reuniao = "https://meet.google.com/exemplo"
data_reuniao = "2025-11-01T15:00:00-03:00"  # Formato ISO 8601

resultado = atualizar_card_com_reuniao(card_id, link_reuniao, data_reuniao)
print(resultado)
