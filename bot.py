import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import logging
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Замените на свой токен бота, который будет храниться в переменной окружения
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Укажите здесь имя вашего канала или его ID
CHANNEL_ID = '@krinzhLesik'  # Для приватных каналов используйте числовой ID

# Уникальный ID пользователя, которому будут отправляться сообщения о том, кто написал в ЛС
TARGET_USER_ID = 7820690236  # Замените на ID пользователя @Zinker72

# Словарь для хранения истории сообщений пользователя
user_message_history = {}

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функция, обрабатывающая команду /start."""
    await update.message.reply_text(
        "Привет! Напиши что угодно, и я отправлю это в канал КРИНЖ ЛЕСИКА. Ты будешь анонимным!"
    )

async def forward_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функция, пересылающая сообщение в указанный канал анонимно и отправляющая ник в ЛС только пользователю @Zinker72."""
    user_message = update.message.text
    user_id = update.message.from_user.id
    user_name = update.message.from_user.username if update.message.from_user.username else "неизвестный"

    # Добавляем информацию о том, кто написал пользователю в личку
    if user_id not in user_message_history:
        user_message_history[user_id] = []

    # Получаем ник последнего отправителя
    sender_name = update.message.from_user.username if update.message.from_user.username else "неизвестный"
    user_message_history[user_id].append(sender_name)

    # Пересылаем сообщение анонимно в канал
    try:
        # Формируем текст для канала
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=f"Сообщение анонимно:\n\n{user_message}"
        )

        # Отправляем ники отправителей в личные сообщения только пользователю @Zinker72
        if user_id in user_message_history:
            last_senders = ", ".join(user_message_history[user_id])
            try:
                if user_id == TARGET_USER_ID:
                    # Отправляем список отправителей в ЛС только @Zinker72
                    await context.bot.send_message(
                        chat_id=TARGET_USER_ID,
                        text=f"Последние отправители сообщений тебе: {last_senders}"
                    )
            except Exception as e:
                logger.error(f"Ошибка при отправке никнеймов в ЛС пользователю @Zinker72: {e}")

        # Подтверждение для пользователя с его ником
        await update.message.reply_text(f"Сообщение отправлено анонимно в канал КРИНЖ ЛЕСИКА!")
    except Exception as e:
        # Если возникла ошибка, вывести её в лог и уведомить пользователя
        logger.error(f"Ошибка при отправке сообщения в канал: {e}")
        await update.message.reply_text(f"Ошибка при отправке сообщения: {e}")

def main():
    """Основная функция для запуска бота."""
    # Создаём приложение
    app = ApplicationBuilder().token(TOKEN).build()

    # Добавляем обработчики команд и сообщений
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_channel))

    # Запускаем бот
    try:
        print("Бот запущен и готов к работе!")
        app.run_polling(timeout=30)  # Убираем read_latency, оставляем только timeout
    except Exception as e:
        logger.error(f"Не удалось запустить бота: {e}")

if __name__ == '__main__':
    main()
