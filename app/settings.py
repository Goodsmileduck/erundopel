# Basic settings
import os
from envparse import env


DB_HOST = env('DB_HOST', default='mongo-mongodb.mongo')
DB_PORT = env('DB_PORT', cast=int, default=27017)
DB_NAME = env('DB_NAME', default='erundopel')
DB_MAX_POOL_SIZE = env('DB_MAX_POOL_SIZE', cast=int, default=300)

WEBHOOK_URL_PATH = '/'  # webhook endpoint
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = 5000

LOG_LEVEL = env('LOG_LEVEL', default='DEBUG')
WORDS_COUNT = env('WORDS_COUNT', default=5)
WORDS_COUNT_TEXT = env('WORDS_COUNT', default="пять")
