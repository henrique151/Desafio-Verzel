import os
import json
import uuid
from datetime import datetime, timedelta
from app.utils.date_utils import normalizar_data
import random

CALENDAR_API_KEY = os.getenv("CALENDAR_API_KEY")
USE_SIMULATION = not CALENDAR_API_KEY  # se token vazio, ativa simulação


def _get_available_slots():
    """Simula ou pega horários reais (por enquanto simula)."""
    slots = []
    base_date = datetime.now() + timedelta(days=1)
    while len(slots) < 3:
        current_date = base_date + timedelta(days=len(slots))
        random_hour = random.randint(9, 17)
        random_minute = random.choice([0, 30])
        slot_datetime = current_date.replace(
            hour=random_hour, minute=random_minute, second=0, microsecond=0
        )
        if slot_datetime.weekday() < 5:
            slots.append(slot_datetime.isoformat())
    return slots


def oferecer_horarios() -> str:
    """Oferece horários disponíveis (simulados ou reais)."""
    if USE_SIMULATION:
        slots = _get_available_slots()
        return json.dumps({"slots": slots})
    else:
        # TODO: Aqui você chamaria a API do Calendly para buscar horários reais
        return json.dumps({
            "slots": ["2025-10-25T10:00:00", "2025-10-25T14:00:00"]
        })


def agendar_reuniao(slot_input: str, card_id: str) -> str:
    """
    Recebe data em linguagem natural (ex: 'dia 9 de novembro às 20h')
    e converte automaticamente para ISO antes de enviar ao Pipefy.
    """
    try:
        # 🔹 Converte automaticamente qualquer formato para ISO
        slot_iso_str = normalizar_data(slot_input)
    except Exception as e:
        return f"Erro ao interpretar data: {e}"

    meeting_id = str(uuid.uuid4())
    meeting_link = f"https://meet.link.ficticio/{meeting_id}"

    from .pipefy_service import atualizar_card_com_reuniao
    atualizar_card_com_reuniao(card_id, meeting_link, slot_iso_str)

    return f"Reunião agendada em {slot_iso_str}. Link: {meeting_link}"
