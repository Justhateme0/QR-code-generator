import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'ru')

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///bot_data.db')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'bot.log')

# QR code style presets
QR_STYLES = {
    'classic': {'fill_color': 'black', 'back_color': 'white'},
    'night': {'fill_color': 'white', 'back_color': 'black'},
    'blue': {'fill_color': '#0066cc', 'back_color': 'white'},
    'purple': {'fill_color': '#6600cc', 'back_color': 'white'},
} 