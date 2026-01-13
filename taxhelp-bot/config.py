import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram Bot
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

    # AWS S3
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    S3_BUCKET = os.getenv('S3_BUCKET', 'taxhelp-documents')

    # OCR
    TESSERACT_PATH = os.getenv('TESSERACT_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe')

    # Tax Rules
    TAX_YEAR = 2024
    FEDERAL_STANDARD_DEDUCTION = {
        'single': 13850,
        'married_filing_jointly': 27700,
        'married_filing_separately': 13850,
        'head_of_household': 20800,
        'qualifying_widow': 27700
    }

    # Tax Brackets (2024)
    FEDERAL_TAX_BRACKETS = {
        'single': [
            (0, 11000, 0.10),
            (11000, 44725, 0.12),
            (44725, 95375, 0.22),
            (95375, 182100, 0.24),
            (182100, 231250, 0.32),
            (231250, 578125, 0.35),
            (578125, float('inf'), 0.37)
        ],
        'married_filing_jointly': [
            (0, 22000, 0.10),
            (22000, 89450, 0.12),
            (89450, 190750, 0.22),
            (190750, 364200, 0.24),
            (364200, 462500, 0.32),
            (462500, 693750, 0.35),
            (693750, float('inf'), 0.37)
        ]
    }

    # Supported Languages
    SUPPORTED_LANGUAGES = ['en', 'es', 'ru', 'ar']

    # File size limits
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    # Encryption
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'your-encryption-key-here')

    # Retention
    DATA_RETENTION_DAYS = 365
