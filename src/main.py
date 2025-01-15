"""
Main script for the Move Cult AI Framework.
"""

import os
import asyncio
from dotenv import load_dotenv
from pathlib import Path
from telegram.ext import Application, MessageHandler, filters, CommandHandler
import tweepy

from config.settings import (
    OPENAI_API_KEY,
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    TWITTER_BEARER_TOKEN,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_GROUP_ID,
    GITHUB_REPOS,
    VECTOR_DB_PATH
)

from agents.idea_generator import IdeaGeneratorAgent
from agents.telegram_agent import TelegramAgent
from utils.doc_processor import DocProcessor

# Initialize agents
idea_generator = IdeaGeneratorAgent()
telegram_agent = TelegramAgent()

# Initialize Twitter client
twitter_client = tweepy.Client(
    bearer_token=TWITTER_BEARER_TOKEN,
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
)

async def init_vector_db():
    """Initialize vector database with documentation."""
    if not Path(VECTOR_DB_PATH).exists():
        print("Initializing vector database...")
        
        # Process each repository
        for repo_url in GITHUB_REPOS:
            processor = DocProcessor(repo_url)
            try:
                # Fetch documentation
                docs = processor.fetch_docs()
                
                # Save locally
                processor.save_docs_locally(docs)
                
                # Add to vector database
                telegram_agent.add_documents(docs)
                
            except Exception as e:
                print(f"Error processing {repo_url}: {e}")
                
        print("Vector database initialization complete.")

async def handle_telegram_message(update, context):
    """Handle incoming Telegram messages."""
    # Only respond in specified group
    if str(update.message.chat_id) != TELEGRAM_GROUP_ID:
        return
        
    # Don't respond to bot messages
    if update.message.from_user.is_bot:
        return
        
    message = update.message.text
    response = telegram_agent.process_message(message)
    
    await update.message.reply_text(response)

async def start_telegram_bot():
    """Start the Telegram bot."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_telegram_message))
    
    # Start bot
    await application.initialize()
    await application.start()
    await application.run_polling()

async def generate_and_post_tweet():
    """Generate and post a tweet."""
    # Get recent tweets about Movement Labs
    tweets = twitter_client.search_recent_tweets(
        query="MovementLabs OR MoveLang",
        max_results=100
    )
    
    # Generate new content idea
    idea = idea_generator.get_unused_idea()
    if not idea:
        # Generate new ideas if none available
        idea_generator.process_trends(tweets.data)
        idea = idea_generator.get_unused_idea()
        
    # Post tweet
    if idea:
        tweet_text = f"{idea['title']}\n\n{idea['key_points']}\n\n#MovementLabs #MoveLang"
        twitter_client.create_tweet(text=tweet_text)

async def run_twitter_loop():
    """Run the Twitter posting loop."""
    while True:
        try:
            await generate_and_post_tweet()
        except Exception as e:
            print(f"Error in Twitter loop: {e}")
            
        # Wait 24 hours
        await asyncio.sleep(24 * 60 * 60)

async def main():
    """Main function to run the framework."""
    # Load environment variables
    load_dotenv()
    
    # Initialize vector database if needed
    await init_vector_db()
    
    # Run Telegram bot and Twitter loop concurrently
    await asyncio.gather(
        start_telegram_bot(),
        run_twitter_loop()
    )

if __name__ == "__main__":
    asyncio.run(main()) 