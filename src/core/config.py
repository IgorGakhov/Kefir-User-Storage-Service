"""Server settings for project."""

import os
from pathlib import Path

from dotenv import load_dotenv


# Создавайте пути внутри проекта следующим образом: BASE_DIR / 'subdir'.
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

load_dotenv(os.path.join(BASE_DIR, '.env'))


# ПРЕДУПРЕЖДЕНИЕ ОБ БЕЗОПАСНОСТИ:
# не запускайте с включенной отладкой в продакшен среде!
DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'


# Аутентификация.

AUTH_JWT_SECRET_KEY: str = os.getenv('AUTH_JWT_SECRET_KEY')


# Базы данных.

DATABASES_DIR: str = os.path.join(BASE_DIR, 'databases')

if DEBUG:
    os.makedirs(DATABASES_DIR, exist_ok=True)
    db_name = 'app.db'
    db_file_path = os.path.join(DATABASES_DIR, db_name)
    db_engine_settings = f'sqlite:///{db_file_path}'
else:
    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    host = os.getenv('HOST')
    port = os.getenv('PORT')
    database = os.getenv('DATABASE')
    connection_params = f'{user}:{password}@{host}:{port}/{database}'
    db_engine_settings = f'postgresql://{connection_params}'
