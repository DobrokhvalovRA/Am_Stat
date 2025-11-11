import requests
from django.conf import settings

def build_message(tournament, participants=None):
    text = (
        f"Турнир №{tournament.id}\n"
        f"Название: {tournament.name}\n"
        f"Дата: {tournament.date}\n"
        f"Место проведения: {tournament.location}\n"
        f"Формат: {'Одиночный' if tournament.format == 'solo' else 'Парный'}\n"
        f"Взнос: {tournament.fee}\n"
        f"Уровень: {tournament.level}\n"
        f"Количество игроков: {tournament.players_count}\n"
        "-----------------------------\n"
        "Список игроков:\n"
    )
    participants = participants or []
    for i, p in enumerate(participants, 1):
        first_name = getattr(p.user, "first_name", "")
        last_name = getattr(p.user, "last_name", "")
        telegram_id = getattr(p.user, "telegram_id", "")
        display_name = f"{first_name} {last_name}".strip() or getattr(p.user, "username", "")
        text += f"{i}. {display_name} ({telegram_id})\n"
    for i in range(len(participants)+1, tournament.players_count+1):
        text += f"{i}. [свободно]\n"
    return text

def update_tournament_message(tournament, participants):
    if not tournament.tg_chat_id or not tournament.tg_message_id:
        return  # невозможно обновить сообщение без этих данных

    TG_BOT_TOKEN = getattr(settings, "BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    MSG_API = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/editMessageText"

    message_text = build_message(tournament, participants)
    buttons = build_buttons(tournament)
    payload = {
        "chat_id": tournament.tg_chat_id,
        "message_id": int(tournament.tg_message_id),
        "text": message_text,
        "reply_markup": buttons,
        "parse_mode": "HTML"
    }
    try:
        resp = requests.post(MSG_API, json=payload)
        resp.raise_for_status()
    except Exception as e:
        print(f"Ошибка обновления сообщения турнира в Telegram: {e}")

def build_buttons(tournament):
    if tournament.format == 'solo':
        buttons = [
            [{"text": "Вступить", "callback_data": f"join_{tournament.id}"},
             {"text": "Выписаться", "callback_data": f"leave_{tournament.id}"}]
        ]
    elif tournament.format == 'pair':
        buttons = [
            [{"text": "Добавить игрока в пару", "callback_data": f"addpair_{tournament.id}"},
             {"text": "Добавиться в пару", "callback_data": f"joinpair_{tournament.id}"}]
        ]
    else:
        buttons = []
    return {"inline_keyboard": buttons}

def send_tournament_to_telegram(tournament, participants=None):
    TG_BOT_TOKEN = getattr(settings, "BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    TG_CHAT_ID = getattr(settings, "TG_GROUP_CHAT_ID", "YOUR_CHAT_ID_HERE")
    MSG_API = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    text = build_message(tournament, participants)
    buttons = build_buttons(tournament)
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "reply_markup": buttons,
        "parse_mode": "HTML"
    }
    resp = requests.post(MSG_API, json=payload)
    if resp.ok and resp.json().get("ok"):
        tournament.tg_chat_id = TG_CHAT_ID
        tournament.tg_message_id = str(resp.json()["result"]["message_id"])
        tournament.save(update_fields=["tg_chat_id", "tg_message_id"])


def delete_tournament_message(tournament):
    TG_BOT_TOKEN = getattr(settings, "BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    MSG_API = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/deleteMessage"
    chat_id = tournament.tg_chat_id
    message_id = tournament.tg_message_id
    if chat_id and message_id:
        payload = {
            "chat_id": chat_id,
            "message_id": int(message_id)
        }
        requests.post(MSG_API, json=payload)