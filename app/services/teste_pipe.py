from pipefy_service import registrar_lead

resposta = registrar_lead(
    nome="João",
    email="joao@exemplo.com",
    empresa="Exemplo Ltda",
    necessidade="Implementar IA"
)
print(resposta)
