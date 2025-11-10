import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

API_URL = "http://localhost:8000/api/tournaments/"

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Здравствуйте! Используйте /tournaments для просмотра турниров.")

def tournaments_command(update: Update, context: CallbackContext):
    resp = requests.get(API_URL)
    tournaments = resp.json()['results']
    msg = "Турниры:\n"
    for t in tournaments:
        msg += f"{t['id']}: {t['name']} ({t['date']})\n"
    update.message.reply_text(msg)

def join_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = update.effective_user.id
    # Пример запроса для добавления участника - в реальном проекте потребуется аутентификация!
    # requests.post(...)
    query.answer("Вы добавлены в турнир (заглушка).")

updater = Updater("BOT_TOKEN")
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("tournaments", tournaments_command))
dp.add_handler(CallbackQueryHandler(join_callback))

if __name__ == "__main__":
    updater.start_polling()

"""from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
import requests

def create_tournament_message(tournament_data):
    text = (
        f"Турнир №{tournament_data['id']}\n"
        f"Название: {tournament_data['name']}\n"
        f"Дата: {tournament_data['date']}\n"
        f"Место: {tournament_data['location']}\n"
        f"Формат: {tournament_data['format_display']}\n"
        f"Взнос: {tournament_data['fee']}\n"
        f"Уровень: {tournament_data['level']}\n"
        f"Игроков: {tournament_data['players_count']}\n"
        f"----\n"
        f"Список игроков:\n"
        + "\n".join(tournament_data['players'])
    )
    buttons = []
    if tournament_data['format'] == "solo":
        buttons.append([InlineKeyboardButton("Вступить", callback_data="join"), InlineKeyboardButton("Выписаться", callback_data="leave")])
    elif tournament_data['format'] == "pair":
        buttons.append([InlineKeyboardButton("Добавить игрока в пару", callback_data="add_to_pair"), InlineKeyboardButton("Добавиться в пару", callback_data="join_pair")])
    return text, InlineKeyboardMarkup(buttons)

def tournament_handler(update: Update, context: CallbackContext):
    # tournament_data = ... get from Django API
    text, markup = create_tournament_message(tournament_data)
    update.message.reply_text(text, reply_markup=markup)

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = update.effective_user.id
    username = update.effective_user.username
    # Handle button click, call Django API to add/remove player, etc.
    # After change: edit message with new list of players!!

updater = Updater("BOT_TOKEN")
updater.dispatcher.add_handler(CommandHandler("tournament", tournament_handler))
updater.dispatcher.add_handler(CallbackQueryHandler(button_handler))
updater.start_polling()"""