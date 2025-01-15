"""
Main script for the Move Cult AI Framework.
"""

import os
import asyncio
from dotenv import load_dotenv
from pathlib import Path
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes
from telegram import Update
import tweepy
import json
from datetime import datetime
import lancedb

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
    VECTOR_DB_PATH,
    MOVEMENT_TWITTER_ID,
    BOT_TWITTER_ID,
    LAST_CHECKED_FILE,
    TREND_FETCH_INTERVAL,
    INTERACTION_CHECK_INTERVAL,
    TWEET_POST_INTERVAL
)

from agents.idea_generator import IdeaGeneratorAgent
from agents.telegram_agent import TelegramAgent
from utils.doc_processor import DocProcessor

# Initialize agents
idea_generator = IdeaGeneratorAgent()
telegram_agent = TelegramAgent()

# Check if running in test mode
TEST_MODE = os.getenv('TEST_MODE', 'false').lower() == 'true'

# Initialize Twitter client in production mode
if not TEST_MODE:
    twitter_client = tweepy.Client(
        bearer_token=TWITTER_BEARER_TOKEN,
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True
    )
    print("Running in production mode - Twitter automation enabled")
else:
    print("Running in test mode - Twitter posting disabled")

# Create data directory for storing trends
TRENDS_FILE = "data/twitter_trends.json"
Path("data").mkdir(exist_ok=True)

async def init_vector_db():
    """Initialize vector database with documentation."""
    db = lancedb.connect(VECTOR_DB_PATH)
    try:
        # Try to open the documents table
        table = db.open_table("documents")
        print("Vector database already initialized.")
    except Exception:
        print("Initializing vector database...")
        
        all_documents = []
        # Process each repository
        for repo_url in GITHUB_REPOS:
            processor = DocProcessor(repo_url)
            try:
                # Fetch and process documentation
                docs = processor.fetch_docs()
                
                # Save locally
                processor.save_docs_locally(docs)
                
                # Collect all documents
                all_documents.extend(docs)
                
            except Exception as e:
                print(f"Error processing {repo_url}: {e}")
                
        # Index all documents in vector database
        if all_documents:
            processor.index_documents(all_documents, str(VECTOR_DB_PATH))
            print(f"Indexed {len(all_documents)} documents in vector database")
        
        print("Vector database initialization complete.")

async def handle_telegram_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming Telegram messages."""
    # Only handle DM messages
    if update.effective_chat.type != 'private':
        return
    
    # Don't respond to bot messages
    if update.effective_user.is_bot:
        return
        
    # Get user ID for tracking conversations
    user_id = str(update.effective_user.id)
    message = update.message.text
    
    try:
        response = await telegram_agent.process_message(message, user_id)
        
        # Split long responses if needed
        if len(response) > 4096:  # Telegram message length limit
            parts = [response[i:i+4096] for i in range(0, len(response), 4096)]
            for part in parts:
                await update.message.reply_text(part)
        else:
            await update.message.reply_text(response)
    except Exception as e:
        error_message = "I apologize, but I encountered an error processing your request. Please try again."
        await update.message.reply_text(error_message)
        print(f"Error processing message from user {user_id}: {e}")

async def handle_generate_tweet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test command to generate a tweet without posting."""
    if not TEST_MODE:
        await update.message.reply_text("Tweet generation is only available in test mode")
        return
        
    # Only allow in DMs
    if update.effective_chat.type != 'private':
        return
        
    # Generate new content idea using existing idea generator
    idea = idea_generator.get_unused_idea()
    if idea:
        tweet_text = f"{idea['title']}\n\n{idea['key_points']}\n\n#MovementLabs #MoveLang"
        await update.message.reply_text(
            f"Generated tweet (not posted):\n\n{tweet_text}"
        )
    else:
        await update.message.reply_text("No new ideas available at the moment")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command in DMs."""
    if update.effective_chat.type != 'private':
        return
        
    user_id = str(update.effective_user.id)
    welcome_message = f"""
Welcome to the Movement Labs AI assistant! 👋

I'm here to help you understand Move Language and Movement Labs technology. You can ask me questions about:

1. Move Language features and concepts
2. Movement Labs' technology stack
3. Technical documentation and guides
4. Development best practices

Feel free to ask any questions! I'll remember our conversation context to provide better assistance.
"""
    if TEST_MODE:
        welcome_message += "\nℹ️ In test mode, you can also use /generate_tweet to test content generation."
        
    await update.message.reply_text(welcome_message)

async def fetch_and_store_trends():
    """Fetch and store Twitter trends."""
    if TEST_MODE:
        return
        
    try:
        # Get recent tweets about Movement Labs
        tweets = twitter_client.search_recent_tweets(
            query="MovementLabs OR MoveLang",
            max_results=100
        )
        
        # Process trends
        idea_generator.process_trends(tweets.data)
        
        # Store trends data
        trends_data = {
            'timestamp': datetime.now().isoformat(),
            'tweets': [tweet.data for tweet in tweets.data] if tweets.data else []
        }
        
        with open(TRENDS_FILE, 'w') as f:
            json.dump(trends_data, f)
            
        print(f"Stored {len(trends_data['tweets'])} trends")
        
    except Exception as e:
        print(f"Error fetching trends: {e}")

async def check_and_retweet_movement():
    """Check and retweet Movement Labs tweets."""
    if TEST_MODE:
        return
        
    try:
        # Get Movement Labs tweets
        tweets = twitter_client.get_users_tweets(
            id=MOVEMENT_TWITTER_ID,
            max_results=100,
            exclude=['retweets', 'replies']
        )
        
        if tweets.data:
            for tweet in tweets.data:
                try:
                    # Retweet
                    twitter_client.retweet(tweet.id)
                    print(f"Retweeted tweet {tweet.id}")
                except Exception as e:
                    if "You have already retweeted this Tweet" not in str(e):
                        print(f"Error retweeting {tweet.id}: {e}")
                    
    except Exception as e:
        print(f"Error fetching Movement Labs tweets: {e}")

async def handle_interactions():
    """Handle all Twitter interactions (mentions, replies, etc.)."""
    if TEST_MODE:
        return
        
    try:
        # Load last checked timestamp
        last_checked = {}
        if os.path.exists(LAST_CHECKED_FILE):
            with open(LAST_CHECKED_FILE, 'r') as f:
                last_checked = json.load(f)
        
        current_time = datetime.now().isoformat()
        
        # Check mentions of our bot account
        mentions = twitter_client.get_users_mentions(
            id=BOT_TWITTER_ID,
            max_results=100,
            start_time=last_checked.get('mentions')
        )
        
        if mentions.data:
            for mention in mentions.data:
                # Generate response using idea generator
                response = idea_generator.generate_reply(mention.text)
                if response:
                    # Reply to the mention
                    twitter_client.create_tweet(
                        text=response,
                        in_reply_to_tweet_id=mention.id
                    )
                    print(f"Replied to mention {mention.id}")
        
        # Check replies to our tweets
        tweets = twitter_client.get_users_tweets(
            id=BOT_TWITTER_ID,
            max_results=100
        )
        
        if tweets.data:
            for tweet in tweets.data:
                # Get replies to this tweet
                replies = twitter_client.search_recent_tweets(
                    query=f"conversation_id:{tweet.id}",
                    max_results=100,
                    start_time=last_checked.get('replies')
                )
                
                if replies.data:
                    for reply in replies.data:
                        # Don't reply to our own replies
                        if str(reply.author_id) != BOT_TWITTER_ID:
                            response = idea_generator.generate_reply(reply.text)
                            if response:
                                twitter_client.create_tweet(
                                    text=response,
                                    in_reply_to_tweet_id=reply.id
                                )
                                print(f"Replied to comment {reply.id}")
        
        # Update last checked timestamps
        last_checked.update({
            'mentions': current_time,
            'replies': current_time
        })
        
        with open(LAST_CHECKED_FILE, 'w') as f:
            json.dump(last_checked, f)
            
    except Exception as e:
        print(f"Error handling interactions: {e}")

async def generate_and_post_tweet():
    """Generate and post a tweet."""
    if TEST_MODE:
        return
        
    try:
        # Get unused idea
        idea = idea_generator.get_unused_idea()
        if idea:
            tweet_text = f"{idea['title']}\n\n{idea['key_points']}\n\n#MovementLabs #MoveLang"
            twitter_client.create_tweet(text=tweet_text)
            print("Posted new tweet")
            
    except Exception as e:
        print(f"Error posting tweet: {e}")

async def run_twitter_automation():
    """Run Twitter automation tasks."""
    if TEST_MODE:
        return
        
    while True:
        try:
            # Schedule tasks at different intervals
            await asyncio.gather(
                # Fetch trends every 12 hours
                asyncio.create_task(
                    asyncio.gather(
                        fetch_and_store_trends(),
                        asyncio.sleep(TREND_FETCH_INTERVAL)
                    )
                ),
                # Check and handle all interactions every 4 hours
                asyncio.create_task(
                    asyncio.gather(
                        handle_interactions(),
                        check_and_retweet_movement(),
                        asyncio.sleep(INTERACTION_CHECK_INTERVAL)
                    )
                ),
                # Post tweet every 24 hours
                asyncio.create_task(
                    asyncio.gather(
                        generate_and_post_tweet(),
                        asyncio.sleep(TWEET_POST_INTERVAL)
                    )
                )
            )
        except Exception as e:
            print(f"Error in Twitter automation: {e}")
            await asyncio.sleep(60)  # Wait a minute before retrying

async def main():
    """Main function to run the framework."""
    # Load environment variables
    load_dotenv()
    
    # Initialize vector database if needed
    await init_vector_db()
    
    # Create application instance
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add message and command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_telegram_message))
    
    # Add test command handlers if in test mode
    if TEST_MODE:
        application.add_handler(CommandHandler("generate_tweet", handle_generate_tweet))
    
    try:
        print("Starting bot...")
        if TEST_MODE:
            # In test mode, only run the Telegram bot
            await application.initialize()
            await application.start()
            await application.updater.start_polling()
            
            # Keep the bot running
            stop_signal = asyncio.Event()
            await stop_signal.wait()
        else:
            # In production, run both Telegram bot and Twitter automation
            await application.initialize()
            await application.start()
            
            # Run both services and wait for either to complete
            await asyncio.gather(
                application.updater.start_polling(),
                run_twitter_automation()
            )
    except KeyboardInterrupt:
        print("\nReceived stop signal")
    finally:
        print("Stopping bot...")
        if application.updater.running:
            await application.updater.stop()
        await application.stop()
        await application.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")