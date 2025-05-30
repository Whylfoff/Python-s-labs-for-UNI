import os
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from windrose import WindroseAxes
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
RUMBS_TO_DEGREES = {
    "С": 0,
    "ССВ": 22.5,
    "СВ": 45,
    "ВСВ": 67.5,
    "В": 90,
    "ВЮВ": 112.5,
    "ЮВ": 135,
    "ЮЮВ": 157.5,
    "Ю": 180,
    "ЮЮЗ": 202.5,
    "ЮЗ": 225,
    "ЗЮЗ": 247.5,
    "З": 270,
    "ЗСЗ": 292.5,
    "СЗ": 315,
    "ССЗ": 337.5,
    "Штиль": None,

    "Ветер, дующий с севера": 0,
    "Ветер, дующий с северо-северо-востока": 22.5,
    "Ветер, дующий с северо-востока": 45,
    "Ветер, дующий с востоко-северо-востока": 67.5,
    "Ветер, дующий с востока": 90,
    "Ветер, дующий с востоко-юго-востока": 112.5,
    "Ветер, дующий с юго-востока": 135,
    "Ветер, дующий с юго-юго-востока": 157.5,
    "Ветер, дующий с юга": 180,
    "Ветер, дующий с юго-юго-запада": 202.5,
    "Ветер, дующий с юго-запада": 225,
    "Ветер, дующий с западо-юго-запада": 247.5,
    "Ветер, дующий с запада": 270,
    "Ветер, дующий с западо-северо-запада": 292.5,
    "Ветер, дующий с северо-запада": 315,
    "Ветер, дующий с северо-северо-запада": 337.5
}

TELEGRAM_TOKEN = "YOUR_TELEGRAM_TOKEN_HERE"


def get_start_keyboard():
    """Create a keyboard with Start button"""
    keyboard = [[KeyboardButton('Построить розу ветров')]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text(
        'Привет! Я могу построить розу ветров по данным с RP5.ru.\n'
        'Отправь мне CSV-файл с данными о ветре, и я все сделаю!',
        reply_markup=get_start_keyboard()
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        'Отправьте мне CSV-файл с данными о ветре с сайта RP5.ru для аэропорта Храброво.\n'
        'Я построю розу ветров и отправлю вам изображение.\n\n'
        'Файл должен содержать столбцы DD (направление ветра) и Ff (скорость ветра).',
        reply_markup=get_start_keyboard()
    )


def button_handler(update: Update, context: CallbackContext) -> None:
    """Handle button presses"""
    if update.message.text == 'Построить розу ветров':
        update.message.reply_text(
            'Пожалуйста, отправьте мне CSV-файл с данными о ветре с сайта RP5.ru',
            reply_markup=get_start_keyboard()
        )


def process_csv_file(update: Update, context: CallbackContext) -> None:
    """Process the CSV file and generate a wind rose."""
    # Get the file
    file = update.message.document
    if not file.file_name.endswith('.csv'):
        update.message.reply_text('Пожалуйста, отправьте файл в формате CSV.')
        return

    update.message.reply_text('Получил ваш файл. Обрабатываю данные...')

    file_info = context.bot.get_file(file.file_id)
    file_path = f"temp_{file.file_name}"
    file_info.download(file_path)

    try:
        encoding = 'utf-8'

        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            first_lines = [f.readline() for _ in range(10)]

        header_line = 0
        for i, line in enumerate(first_lines):
            if 'DD' in line and 'Ff' in line:
                header_line = i
                break

        delimiter = ';'
        if ',' in first_lines[header_line] and ';' not in first_lines[header_line]:
            delimiter = ','

        df = pd.read_csv(file_path, sep=delimiter, encoding=encoding,
                         skiprows=header_line, on_bad_lines='warn')

        if 'DD' not in df.columns or 'Ff' not in df.columns:
            direction_cols = [col for col in df.columns if 'направлен' in col.lower() or 'dd' in col.lower()]
            speed_cols = [col for col in df.columns if 'скорост' in col.lower() or 'ff' in col.lower()]

            if direction_cols and speed_cols:
                df = df.rename(columns={direction_cols[0]: 'DD', speed_cols[0]: 'Ff'})
            else:
                update.message.reply_text(
                    'В файле не найдены необходимые столбцы DD (направление) и Ff (скорость ветра).')
                os.remove(file_path)
                return

        df['wind_direction'] = df['DD'].map(RUMBS_TO_DEGREES)

        df['Ff'] = df['Ff'].astype(str)
        df['Ff'] = df['Ff'].str.replace(',', '.')
        df['wind_speed'] = pd.to_numeric(df['Ff'], errors='coerce')

        df = df.dropna(subset=['wind_direction', 'wind_speed'])

        if len(df) == 0:
            update.message.reply_text('После обработки данных не осталось корректных записей.')
            os.remove(file_path)
            return

        ax = WindroseAxes.from_ax()
        ax.bar(df['wind_direction'], df['wind_speed'], normed=True, opening=0.8, edgecolor='white')
        ax.set_legend(title="м/с")
        plt.title('Роза ветров для аэропорта Храброво')

        image_path = "wind_rose.png"
        plt.savefig(image_path, dpi=300, bbox_inches='tight')

        with open(image_path, 'rb') as photo:
            update.message.reply_photo(photo=photo)
            update.message.reply_text(f'Роза ветров построена по {len(df)} записям.', reply_markup=get_start_keyboard())

        os.remove(file_path)
        os.remove(image_path)

    except Exception as e:
        logger.error(f"Error processing file: {e}")
        update.message.reply_text(f'Произошла ошибка при обработке файла: {str(e)}', reply_markup=get_start_keyboard())
        if os.path.exists(file_path):
            os.remove(file_path)


def main() -> None:
    """Start the bot."""
    token = "YOUR_TELEGRAM_TOKEN_HERE"

    updater = Updater(token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(MessageHandler(Filters.document, process_csv_file))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, button_handler))
    updater.start_polling()
    logger.info("Bot started. Press Ctrl+C to stop.")
    updater.idle()


if __name__ == '__main__':
    main()