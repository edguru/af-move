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

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
VECTOR_DB_PATH = DATA_DIR / "vector_db"
DOCS_DIR = DATA_DIR / "docs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
VECTOR_DB_PATH.mkdir(exist_ok=True)
DOCS_DIR.mkdir(exist_ok=True)

# Twitter Configuration
TWEET_INTERVAL = 24 * 60 * 60  # 24 hours in seconds
MAX_TWEETS_TO_ANALYZE = 100
RELEVANT_HASHTAGS = [
    "#MoveLang",
    "#MovementLabs",
    "#Web3",
    "#Blockchain",
    "#DeFi"
]

# Telegram Configuration
MAX_RESPONSE_LENGTH = 4096  # Telegram message length limit
RESPONSE_TEMPERATURE = 0.7

# Documentation
GITHUB_REPOS = [
    "https://github.com/movementlabsxyz/movement",
    "https://github.com/movementlabsxyz/movement-docs"
]

# Vector Database
EMBEDDING_DIMENSION = 1536  # OpenAI ada-002 embedding dimension
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100
TOP_K_RESULTS = 3 