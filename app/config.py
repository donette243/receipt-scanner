import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    APP_NAME = os.getenv(
        "APP_NAME",
        "Receipt Scanner",
    )

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:password@localhost:3306/receiptscanner",
    )

    UPLOAD_DIR = os.getenv(
        "UPLOAD_DIR",
        str(BASE_DIR / "uploads"),
    )

    OCR_LANG = os.getenv(
        "OCR_LANG",
        "rus+eng+fra",
    )

    TESSERACT_CMD = os.getenv(
        "TESSERACT_CMD",
        "",
    )

    MAX_FILE_SIZE_MB = int(
        os.getenv(
            "MAX_FILE_SIZE_MB",
            "10",
        )
    )

    LLM_ENABLED = (
        os.getenv(
            "LLM_ENABLED",
            "false",
        ).strip().lower()
        == "true"
    )

    OPENAI_API_KEY = os.getenv(
        "OPENAI_API_KEY",
        "",
    )

    LLM_MODEL = os.getenv(
        "LLM_MODEL",
        "gpt-4o-mini",
    )


settings = Settings()