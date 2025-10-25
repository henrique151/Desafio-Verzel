import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from app.services.pipefy_service import atualizar_card_com_reuniao

print(atualizar_card_com_reuniao("1244241864",
      "https://meet.link.ficticio/teste", "dia 9 de novembro às 20h"))