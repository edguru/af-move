# Movement Labs AI Assistant

An AI-powered assistant for Movement Labs that provides technical support through Telegram and manages social media presence on Twitter.

## Features

- **Telegram Support Bot**:
  - Direct message support for technical queries
  - Context-aware conversations
  - Powered by RAG system using Movement Labs documentation
  - Maintains conversation history for better responses

- **Twitter Automation** (Production Mode):
  - Auto-retweets Movement Labs tweets
  - Responds to mentions and comments
  - Generates and posts regular content
  - Monitors trends and engagement

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/move-cult-ai.git
cd move-cult-ai
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy the example environment file and fill in your credentials:
```bash
cp .env.example .env
```

## Configuration

Edit the `.env` file with your credentials:

```env
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Twitter API Keys
TWITTER_API_KEY=your_twitter_api_key_here
TWITTER_API_SECRET=your_twitter_api_secret_here
TWITTER_ACCESS_TOKEN=your_twitter_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret_here
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here

# Twitter Account IDs
MOVEMENT_TWITTER_ID=movement_labs_account_id_here
BOT_TWITTER_ID=bot_account_id_here

# Twitter Automation Intervals (in hours)
TREND_FETCH_INTERVAL=12
TWEET_POST_INTERVAL=24
INTERACTION_CHECK_INTERVAL=4

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Test Mode Configuration
TEST_MODE=false
```

## Running the Bot

### Test Mode
Run in test mode to test functionality without Twitter integration:
```bash
TEST_MODE=true python src/main.py
```

In test mode:
- Only Telegram bot is active
- No Twitter posting/interaction
- Can test tweet generation via `/generate_tweet` command

### Production Mode
Run in production mode for full functionality:
```bash
python src/main.py
```

In production mode:
- Telegram bot handles user support
- Twitter automation is active
- All social media features are enabled

## Documentation Sources

The bot uses documentation from:
1. [Movement Docs](https://github.com/movementlabsxyz/movement-docs)
2. [MIP Repository](https://github.com/movementlabsxyz/MIP)
3. [Developer Portal](https://github.com/movementlabsxyz/developer-portal)

## Architecture

### Components

1. **DocProcessor**: 
   - Fetches and processes documentation
   - Handles markdown parsing and chunking
   - Manages vector database indexing

2. **TelegramAgent**:
   - Handles user interactions
   - Maintains conversation context
   - Uses RAG for accurate responses

3. **Twitter Automation**:
   - Manages social media presence
   - Handles interactions and content generation
   - Monitors trends and engagement

## Development

### Adding New Documentation Sources

1. Add repository URL to `GITHUB_REPOS` in `config/settings.py`
2. Update `DOC_PATHS` if documents are in a specific directory
3. Run the bot to reindex documentation

### Customizing Response Behavior

1. Adjust settings in `config/settings.py`:
   - `CHUNK_SIZE`: Size of document chunks
   - `MAX_DOCS_PER_QUERY`: Number of relevant docs to retrieve
   - `CHAT_CONTEXT_EXPIRY_HOURS`: How long to maintain chat context

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file for details 