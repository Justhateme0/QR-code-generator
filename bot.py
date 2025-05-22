import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

from src.config import BOT_TOKEN, LOG_LEVEL, LOG_FILE
from src.database import Database
from src.locales import MESSAGES
from src.qr_generator import create_qr_code

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL),
    filename=LOG_FILE
)

logger = logging.getLogger(__name__)
db = Database()

def get_message(user_id: int, key: str) -> str:
    """Get localized message for user."""
    language = db.get_user_language(user_id)
    return MESSAGES[language][key]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message and language selection when the command /start is issued."""
    keyboard = [
        [
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Выберите язык / Choose language:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the command /help is issued."""
    help_text = get_message(update.effective_user.id, 'help')
    await update.message.reply_text(help_text)

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /language command."""
    keyboard = [
        [
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        get_message(update.effective_user.id, 'choose_language'),
        reply_markup=reply_markup
    )

async def style_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show available QR code styles."""
    user_id = update.effective_user.id
    language = db.get_user_language(user_id)
    style_names = MESSAGES[language]['styles']
    
    keyboard = [
        [
            InlineKeyboardButton(style_names['classic'], callback_data="style_classic"),
            InlineKeyboardButton(style_names['night'], callback_data="style_night"),
        ],
        [
            InlineKeyboardButton(style_names['blue'], callback_data="style_blue"),
            InlineKeyboardButton(style_names['purple'], callback_data="style_purple"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        get_message(user_id, 'choose_style'),
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if query.data.startswith("lang_"):
        language = query.data.split("_")[1]
        db.set_user_language(user_id, language)
        await query.edit_message_text(get_message(user_id, 'language_selected'))
        # Send welcome message in new language
        await query.message.reply_text(get_message(user_id, 'welcome'))
    
    elif query.data.startswith("style_"):
        style = query.data.split("_")[1]
        db.set_user_style(user_id, style)
        style_name = MESSAGES[db.get_user_language(user_id)]['styles'][style]
        await query.edit_message_text(
            get_message(user_id, 'style_selected').format(style_name)
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate QR code from text."""
    user_id = update.effective_user.id
    text = update.message.text
    style = db.get_user_style(user_id)
    
    # Send "generating" message
    message = await update.message.reply_text(get_message(user_id, 'generating'))
    
    # Create and send QR code
    qr_image = create_qr_code(text, style)
    style_name = MESSAGES[db.get_user_language(user_id)]['styles'][style]
    await update.message.reply_photo(
        photo=qr_image,
        caption=get_message(user_id, 'qr_ready').format(
            style_name,
            text[:50] + ('...' if len(text) > 50 else '')
        )
    )
    
    # Delete "generating" message
    await message.delete()

async def qr_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /qr command."""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text(get_message(user_id, 'provide_text'))
        return
    
    text = ' '.join(context.args)
    style = db.get_user_style(user_id)
    
    # Send "generating" message
    message = await update.message.reply_text(get_message(user_id, 'generating'))
    
    # Create and send QR code
    qr_image = create_qr_code(text, style)
    style_name = MESSAGES[db.get_user_language(user_id)]['styles'][style]
    await update.message.reply_photo(
        photo=qr_image,
        caption=get_message(user_id, 'qr_ready').format(
            style_name,
            text[:50] + ('...' if len(text) > 50 else '')
        )
    )
    
    # Delete "generating" message
    await message.delete()

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("style", style_command))
    application.add_handler(CommandHandler("qr", qr_command))
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 