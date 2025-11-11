import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes,  MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN") or "8221066430:AAHUm1PHLrydTWr5vVL2-tMLCMfglLbpzoc"
DJANGO_API = "http://localhost:8000/api/tournaments/"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_json_response(resp):
    try:
        return resp.json()
    except Exception as exc:
        logger.error(f"Ошибка чтения JSON: {exc}. Ответ: {resp.text}")
        return {}

def build_tournament_message(t):
    text = (
        f"Турнир №{t.get('id','?')}\n"
        f"Название: {t.get('name','?')}\n"
        f"Дата: {t.get('date','?')}\n"
        f"Место проведения: {t.get('location','?')}\n"
        f"Формат: {'Одиночный' if t.get('format','solo')=='solo' else 'Парный'}\n"
        f"Взнос: {t.get('fee','?')}\n"
        f"Уровень: {t.get('level','?')}\n"
        f"Количество игроков: {t.get('players_count','?')}\n"
        "-----------------------------\n"
        "Список игроков:\n"
    )
    players = t.get('participants', [])
    for i, p in enumerate(players, 1):
        user_data = p.get('user', {})
        first_name = user_data.get('first_name', '')
        last_name = user_data.get('last_name', '')
        telegram_id = user_data.get('telegram_id', '')
        phone = user_data.get('phone_number', '')
        display_name = " ".join(part for part in [first_name, last_name, phone] if part).strip()
        if not display_name:
            display_name = user_data.get('username', 'Пользователь')
        text += f"{i}. {display_name} ({telegram_id})\n"
    for i in range(len(players) + 1, t.get('players_count', 0) + 1):
        text += f"{i}. [свободно]\n"
    return text

def build_buttons(t):
    tournament_id = t.get('id', '?')
    if t.get('format', 'solo') == 'solo':
        buttons = [
            [InlineKeyboardButton("Вступить", callback_data=f"join_{tournament_id}"),
             InlineKeyboardButton("Выписаться", callback_data=f"leave_{tournament_id}")]
        ]
    elif t.get('format') == 'pair':
        buttons = [
            [InlineKeyboardButton("Добавить игрока в пару", callback_data=f"addpair_{tournament_id}"),
             InlineKeyboardButton("Добавиться в пару", callback_data=f"joinpair_{tournament_id}")]
        ]
    else:
        buttons = []
    return InlineKeyboardMarkup(buttons)

async def announce_tournament(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Укажите id турнира, например: /announce_tournament 1")
        return
    tournament_id = args[0]
    resp = requests.get(f"{DJANGO_API}{tournament_id}/")
    r = safe_json_response(resp)
    if not r:
        await update.message.reply_text("Ошибка получения информации о турнире")
        return
    message_text = build_tournament_message(r)
    reply_markup = build_buttons(r)
    msg = await update.message.reply_text(message_text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username or query.from_user.first_name or "Пользователь"
    action, tournament_id = query.data.split("_", maxsplit=1)
    payload = {"telegram_id": user_id, "username": username, "tournament_id": tournament_id}

    # Обработка действий пользователя
    if action == "join":
        resp = requests.post(f"{DJANGO_API}{tournament_id}/join/", json=payload)
        await query.answer("Вы записались!")
    elif action == "leave":
        resp = requests.post(f"{DJANGO_API}{tournament_id}/leave/", json=payload)
        await query.answer("Вы выписались!")
    elif action == "addpair":
        await query.answer("Функция пар скоро будет.")
    elif action == "joinpair":
        await query.answer("Функция пар скоро будет.")

    # Получаем обновлённые данные турнира и редактируем сообщение
    resp = requests.get(f"{DJANGO_API}{tournament_id}/")
    r = safe_json_response(resp)
    if not r:
        try:
            await query.edit_message_text(text="Ошибка получения данных турнира")
        except Exception as e:
            logger.warning(f"edit_message_text failed: {e}")
        return
    message_text = build_tournament_message(r)
    reply_markup = build_buttons(r)
    try:
        await query.edit_message_text(text=message_text, reply_markup=reply_markup)
    except Exception as e:
        logger.warning(f"edit_message_text failed: {e}")

async def echo_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Chat ID этой группы: {chat_id}")

async def error_handler(update, context):
    logger.error(f"Exception: {context.error}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("announce_tournament", announce_tournament))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL, echo_chat_id))
    app.add_error_handler(error_handler)
    logger.info("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()