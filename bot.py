import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes,  MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN") or "8221066430:AAHUm1PHLrydTWr5vVL2-tMLCMfglLbpzoc"
DJANGO_API = "http://localhost:8000/api/tournaments/"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def echo_chat_id(update, context):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Chat ID этой группы: {chat_id}")

def build_tournament_message(t):
    text = (
        f"Турнир №{t['id']}\n"
        f"Название: {t['name']}\n"
        f"Дата: {t['date']}\n"
        f"Место проведения: {t['location']}\n"
        f"Формат: {'Одиночный' if t['format']=='solo' else 'Парный'}\n"
        f"Взнос: {t['fee']}\n"
        f"Уровень: {t['level']}\n"
        f"Количество игроков: {t['players_count']}\n"
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
    for i in range(len(players) + 1, t['players_count'] + 1):
        text += f"{i}. [свободно]\n"
    return text

def build_buttons(t):
    if t['format'] == 'solo':
        buttons = [
            [InlineKeyboardButton("Вступить", callback_data=f"join_{t['id']}"),
             InlineKeyboardButton("Выписаться", callback_data=f"leave_{t['id']}")]
        ]
    elif t['format'] == 'pair':
        buttons = [
            [InlineKeyboardButton("Добавить игрока в пару", callback_data=f"addpair_{t['id']}"),
             InlineKeyboardButton("Добавиться в пару", callback_data=f"joinpair_{t['id']}")]
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
    r = requests.get(f"{DJANGO_API}{tournament_id}/").json()
    message_text = build_tournament_message(r)
    reply_markup = build_buttons(r)
    msg = await update.message.reply_text(message_text, reply_markup=reply_markup)
    # Можно записать msg.message_id и update.effective_chat.id в Django Tournament для автоматического редактирования

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username or query.from_user.first_name
    action, tournament_id = query.data.split("_", maxsplit=1)
    payload = {"telegram_id": user_id, "username": username, "tournament_id": tournament_id}

    # Действия пользователя
    if action == "join":
        requests.post(f"{DJANGO_API}{tournament_id}/join/", json=payload)
        await query.answer("Вы записались!")
    elif action == "leave":
        requests.post(f"{DJANGO_API}{tournament_id}/leave/", json=payload)
        await query.answer("Вы выписались!")
    elif action == "addpair":
        await query.answer("Функция пар скоро будет.")
    elif action == "joinpair":
        await query.answer("Функция пар скоро будет.")

    # Получаем обновлённые данные турнира и редактируем сообщение
    r = requests.get(f"{DJANGO_API}{tournament_id}/").json()
    message_text = build_tournament_message(r)
    reply_markup = build_buttons(r)
    try:
        await query.edit_message_text(text=message_text, reply_markup=reply_markup)
    except Exception as e:
        logger.warning(f"edit_message_text failed: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("announce_tournament", announce_tournament))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL, echo_chat_id))
    logger.info("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()