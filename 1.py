import logging
from datetime import datetime
from telegram import Update, ChatPermissions
from telegram.ext import Updater, CommandHandler, CallbackContext
import pytz

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация бота
TOKEN = '8096719095:AAH94ss4nqnWEr0iLQaHAq2q5hdyJrr6J90'  # Замените на токен вашего бота
ADMIN_IDS = [nd1ce]   # ID администраторов, которые могут использовать бота
TIMEZONE = pytz.timezone('Europe/Moscow')  # Укажите свою временную зону

def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start"""
    if update.effective_user.id not in ADMIN_IDS:
        update.message.reply_text("У вас нет прав для использования этого бота.")
        return
    
    update.message.reply_text(
        "Привет! Я бот для очистки чата от старых сообщений.\n"
        "Используйте команду /cleanup YYYY-MM-DD чтобы удалить сообщения старше указанной даты.\n"
        "Пример: /cleanup 2023-01-01"
    )

def cleanup(update: Update, context: CallbackContext) -> None:
    """Удаление сообщений старше указанной даты"""
    if update.effective_user.id not in ADMIN_IDS:
        update.message.reply_text("У вас нет прав для использования этой команды.")
        return
    
    if not context.args:
        update.message.reply_text("Укажите дату в формате YYYY-MM-DD")
        return
    
    try:
        cutoff_date = datetime.strptime(context.args[0], "%Y-%m-%d").replace(tzinfo=TIMEZONE)
    except ValueError:
        update.message.reply_text("Неверный формат даты. Используйте YYYY-MM-DD")
        return
    
    chat_id = update.effective_chat.id
    message = update.message
    
    # Проверяем, что бот является администратором
    bot_member = context.bot.get_chat_member(chat_id, context.bot.id)
    if not bot_member.can_delete_messages:
        message.reply_text("У меня нет прав на удаление сообщений в этом чате.")
        return
    
    message.reply_text(f"Начинаю удаление сообщений старше {cutoff_date.date()}...")
    
    # Получаем ID последнего сообщения
    last_message = context.bot.get_chat(chat_id).pinned_message or message
    last_message_id = last_message.message_id
    
    deleted_count = 0
    error_count = 0
    
    # Удаляем сообщения по одному (Telegram API не позволяет массовое удаление по дате)
    current_message_id = 1  # Начинаем с самого первого сообщения
    
    while current_message_id <= last_message_id:
        try:
            msg = context.bot.get_chat_member(chat_id, current_message_id)
            if msg.date < cutoff_date:
                context.bot.delete_message(chat_id, current_message_id)
                deleted_count += 1
        except Exception as e:
            error_count += 1
            logger.error(f"Ошибка при обработке сообщения {current_message_id}: {e}")
        
        current_message_id += 1
    
    message.reply_text(
        f"Готово! Удалено сообщений: {deleted_count}\n"
        f"Ошибок: {error_count}"
    )

def main() -> None:
    """Запуск бота"""
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Регистрация обработчиков команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("cleanup", cleanup))

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
