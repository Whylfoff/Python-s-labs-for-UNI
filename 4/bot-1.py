import logging
import random
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Dictionary to store user statistics
stats = {}

# Game choices
CHOICES = ["rock", "paper", "scissors"]


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user

    keyboard = [
        ['Играть'],
        ['Статистика']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    update.message.reply_text(
        f'Привет, {user.first_name}! хочешь поиграть в "Камень, ножницы, бумага"?\n\n'
        'Тогда, используй кнопки меню или команды:\n'
        '/play - начать игру\n'
        '/stats - посмотреть статистику',
        reply_markup=reply_markup
    )


def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle messages with text buttons."""
    text = update.message.text

    if text == 'Играть':
        play(update, context)
    elif text == 'Статистика':
        show_stats(update, context)


def play(update: Update, context: CallbackContext) -> None:
    """Send message with inline keyboard for game choices."""
    keyboard = [
        [
            InlineKeyboardButton("🪨", callback_data="rock"),
            InlineKeyboardButton("✂️", callback_data="scissors"),
            InlineKeyboardButton("📄", callback_data="paper"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Функция может быть вызвана как по команде, так и по нажатию кнопки
    if update.message:
        update.message.reply_text('Выбери свой ход:', reply_markup=reply_markup)
    else:
        # Если функция вызвана из обработчика колбэков, используем другой метод
        update.callback_query.message.reply_text('Выбери свой ход:', reply_markup=reply_markup)


def button(update: Update, context: CallbackContext) -> None:
    """Handle the button press."""
    query = update.callback_query
    query.answer()

    if query.data in CHOICES:
        handle_game_choice(query)
    elif query.data == "play_again":
        play(update, context)
    elif query.data == "show_stats":
        show_stats(update, context)


def handle_game_choice(query):
    """Handle game choice and show results."""
    user_id = str(query.from_user.id)
    user_choice = query.data
    bot_choice = random.choice(CHOICES)

    if user_id not in stats:
        stats[user_id] = {"wins": 0, "losses": 0, "draws": 0}

    result = determine_winner(user_choice, bot_choice)

    if result == "win":
        stats[user_id]["wins"] += 1
        result_text = "Ты выиграл! 🎉"
    elif result == "loss":
        stats[user_id]["losses"] += 1
        result_text = "Ты проиграл! 😢"
    else:  # draw
        stats[user_id]["draws"] += 1
        result_text = "Ничья! 🤝"

    emoji_map = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
    user_emoji = emoji_map[user_choice]
    bot_emoji = emoji_map[bot_choice]

    choices_ru = {"rock": "Камень", "paper": "Бумага", "scissors": "Ножницы"}
    user_choice_ru = choices_ru[user_choice]
    bot_choice_ru = choices_ru[bot_choice]

    keyboard = [
        [
            InlineKeyboardButton("Играть ещё раз", callback_data="play_again"),
            InlineKeyboardButton("Статистика", callback_data="show_stats"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(
        f"Твой выбор: {user_choice_ru} {user_emoji}\n"
        f"Мой выбор: {bot_choice_ru} {bot_emoji}\n\n"
        f"{result_text}",
        reply_markup=reply_markup
    )


def determine_winner(user_choice, bot_choice):
    """Determine the winner based on game rules."""
    if user_choice == bot_choice:
        return "draw"

    winning_combinations = {
        "rock": "scissors",
        "scissors": "paper",
        "paper": "rock"
    }

    if winning_combinations[user_choice] == bot_choice:
        return "win"
    else:
        return "loss"


def show_stats(update: Update, context: CallbackContext) -> None:
    """Show user statistics."""
    if update.message:
        user_id = str(update.effective_user.id)
        reply_method = update.message.reply_text
    else:
        user_id = str(update.callback_query.from_user.id)
        reply_method = update.callback_query.message.reply_text
        update.callback_query.answer()

    if user_id not in stats:
        reply_method('У вас пока нет статистики. Сыграйте в игру!')
        return

    user_stats = stats[user_id]
    reply_method(
        'Ваша статистика:\n'
        f'Побед: {user_stats["wins"]}\n'
        f'Поражений: {user_stats["losses"]}\n'
        f'Ничьих: {user_stats["draws"]}'
    )


def main() -> None:
    """Start the bot."""
    updater = Updater("YOUR_TELEGRAM_TOKEN_HERE")

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("play", play))
    dispatcher.add_handler(CommandHandler("stats", show_stats))

    dispatcher.add_handler(CallbackQueryHandler(button))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()