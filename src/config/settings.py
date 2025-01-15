"""
Configuration settings for the Move Cult AI Framework.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")

# Twitter Account IDs
MOVEMENT_TWITTER_ID = os.getenv("MOVEMENT_TWITTER_ID")
BOT_TWITTER_ID = os.getenv("BOT_TWITTER_ID")

# Twitter Automation Intervals (in seconds)
TREND_FETCH_INTERVAL = int(os.getenv("TREND_FETCH_INTERVAL", "12")) * 3600  # Convert hours to seconds
TWEET_POST_INTERVAL = int(os.getenv("TWEET_POST_INTERVAL", "24")) * 3600
INTERACTION_CHECK_INTERVAL = int(os.getenv("INTERACTION_CHECK_INTERVAL", "4")) * 3600

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
VECTOR_DB_PATH = DATA_DIR / "vector_db"
DOCS_DIR = DATA_DIR / "docs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
VECTOR_DB_PATH.mkdir(exist_ok=True)
DOCS_DIR.mkdir(exist_ok=True)

# Documentation Repositories
GITHUB_REPOS = [
    "https://github.com/movementlabsxyz/movement-docs",
    "https://github.com/movementlabsxyz/MIP",
    "https://github.com/movementlabsxyz/developer-portal"
]

# Documentation Paths
DOC_PATHS = {
    "movement-docs": "docs",
    "MIP": "",  # Root directory for MIP
    "developer-portal": "content/Learning-Paths"
}

# LangChain Settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100
MAX_DOCS_PER_QUERY = 3
MODEL_NAME = "gpt-4-turbo-preview"  # Model for CrewAI agents

# Vector Database
EMBEDDING_DIMENSION = 1536  # OpenAI ada-002 embedding dimension

# Store last checked timestamps
LAST_CHECKED_FILE = DATA_DIR / "last_checked.json"

# Telegram Configuration
MAX_RESPONSE_LENGTH = 4096  # Telegram message length limit
RESPONSE_TEMPERATURE = 0.7

# Chat Context
CHAT_CONTEXT_EXPIRY_HOURS = 24  # Chat context expires after 24 hours
MAX_CHAT_HISTORY = 10  # Maximum number of messages to keep in chat history
IMMEDIATE_CONTEXT_SIZE = 3  # Number of recent messages to use for immediate context 