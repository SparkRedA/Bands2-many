
import os
from dotenv import load_dotenv

load_dotenv()


class DevelopmentConfig:
    SECRET_KEY = os.getenv(
        'SECRET_KEY',
        'development-secret-key'
    )

    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///bands_collaboration.db'
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
