from dotenv import load_dotenv
import os

# Load environment variables from a .env file if present
load_dotenv()

class Settings:
    """
    Centralized configuration for the AI Email Assistant.
    Reads values from environment variables with sensible defaults.
    """

    # Email (IMAP/SMTP)
    IMAP_HOST = os.getenv("IMAP_HOST", "imap.gmail.com")
    IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    # LLM
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL = os.getenv("MODEL", "gpt-4.1-mini")

    # App settings
    INBOX_LABEL = os.getenv("INBOX_LABEL", "INBOX")
    DRAFTS_FOLDER = os.getenv("DRAFTS_FOLDER", "Drafts")
    MAX_EMAILS = int(os.getenv("MAX_EMAILS", "25"))

# Export a singleton settings object
settings = Settings()