# Basic settings
from envparse import env
DB_HOST = env('DB_HOST', default='localhost')
DB_PORT = env('DB_PORT', cast=int, default=27017)
DB_NAME = env('DB_NAME', default='neuroslav')
VERSION = env('VERSION', default='0.0.1')
CHATBASE_API_KEY = env('CHATBASE_API_KEY', default='6f36ad77-b9d9-415c-bed7-6ee68943d64d')
CHATBASE_BOT_PLATFORM = env('CHATBASE_BOT_PLATFORM', default='alisa')
SEND_TO_CHATBASE = env('SEND_TO_CHATBASE', default=False)
MAX_ATTEMPTS = 2
WELCOME_IMAGE = '965417/253f8b23ad1182b886c8'
CHEATS = ['яндекс']