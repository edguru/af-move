# Move Cult AI Framework

A comprehensive AI framework for managing Movement Labs' social media presence and community engagement, powered by the Crew AI framework.

## Features

- **Twitter Agent**: A personality-driven agent that generates engaging content and manages interactions on Twitter
- **Idea Generator**: Processes trends and generates content ideas, storing them in an organized Excel file
- **Telegram Agent**: A documentation assistant using RAG (Retrieval-Augmented Generation) and LanceDB for accurate responses
- **Utilities**: Document processing and configuration management

## Prerequisites

- Python 3.10 or higher
- Virtual environment (recommended)
- Twitter Developer Account with API access
- Telegram Bot Token
- OpenAI API Key

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
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

4. Set up environment variables:
Create a `.env` file in the root directory with:
```
OPENAI_API_KEY=your_openai_api_key
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_GROUP_ID=your_telegram_group_id
```

## Project Structure

```
move-cult-ai/
├── src/
│   ├── agents/
│   │   ├── idea_generator.py
│   │   └── telegram_agent.py
│   ├── config/
│   │   └── settings.py
│   └── utils/
│       └── doc_processor.py
├── data/
│   └── vector_db/
├── requirements.txt
├── README.md
└── .env
```

## Usage

1. Start the Telegram bot and Twitter agent:
```bash
python src/main.py
```

The framework will:
- Generate and post tweets every 24 hours
- Monitor and respond to Twitter mentions
- Listen for and respond to Telegram messages in the specified group
- Process and store documentation for accurate responses

## Agents

### Twitter Agent
- Generates engaging content about Movement Labs and Move Language
- Posts tweets on a schedule
- Monitors and responds to mentions
- Tracks relevant hashtags and topics

### Idea Generator
- Analyzes Twitter trends
- Generates content ideas based on current discussions
- Maintains an organized repository of unused ideas
- Tracks used ideas to prevent duplication

### Telegram Agent
- Uses RAG for accurate documentation-based responses
- Maintains a vector database of documentation
- Provides helpful responses to technical questions
- Monitors group chat for queries

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 