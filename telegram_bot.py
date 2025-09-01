import os
import logging
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext
from ai_news_scraper import AINewsScraper
from company_news_scraper import CompanyNewsScraper
import schedule
import time
import threading
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AINewsBot:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.scraper = AINewsScraper()
        self.company_scraper = CompanyNewsScraper()
        self.subscribers = set()
        
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
    
    def start_command(self, update: Update, context: CallbackContext):
        """Handle /start command"""
        chat_id = update.effective_chat.id
        self.subscribers.add(chat_id)
        
        welcome_message = """
🤖 Welcome to AI Advancement Tracker!

I'll keep you updated with the latest AI developments from around the web.

Commands:
/start - Subscribe to updates
/stop - Unsubscribe from updates  
/latest - Get latest AI news now
/help - Show this help message

You'll receive automatic updates every 6 hours with the latest AI advancements!
        """
        
        update.message.reply_text(welcome_message)
        logger.info(f"New subscriber: {chat_id}")
    
    def stop_command(self, update: Update, context: CallbackContext):
        """Handle /stop command"""
        chat_id = update.effective_chat.id
        self.subscribers.discard(chat_id)
        
        update.message.reply_text(
            "You've been unsubscribed from AI updates. Use /start to subscribe again."
        )
        logger.info(f"Unsubscribed: {chat_id}")
    
    def latest_command(self, update: Update, context: CallbackContext):
        """Handle /latest command"""
        update.message.reply_text("🔍 Scanning for latest AI advancements...")
        
        try:
            # Get both RSS news and company announcements with proper error handling
            articles = []
            company_news = []
            
            try:
                articles = self.scraper.get_latest_news(hours=48) or []
            except Exception as e:
                logger.error(f"Error getting RSS news: {e}")
                articles = []
            
            try:
                company_news = self.company_scraper.get_company_announcements() or []
            except Exception as e:
                logger.error(f"Error getting company news: {e}")
                company_news = []
            
            # Ensure we have lists
            if not isinstance(articles, list):
                articles = []
            if not isinstance(company_news, list):
                company_news = []
            
            # Combine and prioritize company announcements
            all_news = company_news + articles
            
            if not all_news:
                update.message.reply_text("No new AI product releases or announcements found in the last 48 hours.")
                return
            
            update.message.reply_text(f"Found {len(all_news)} recent AI product releases & announcements:")
            
            for article in all_news[:10]:  # Limit to 10 total
                try:
                    message = self.scraper.format_article_message(article)
                    update.message.reply_text(
                        message, 
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True
                    )
                    time.sleep(1)  # Avoid rate limiting
                except Exception as e:
                    logger.error(f"Error sending article: {e}")
                    # Continue with next article instead of failing completely
                    continue
                    
        except Exception as e:
            logger.error(f"Error in latest_command: {e}")
            update.message.reply_text("Sorry, there was an error fetching the latest news.")
    
    def help_command(self, update: Update, context: CallbackContext):
        """Handle /help command"""
        help_text = """
🤖 AI Advancement Tracker Bot

This bot scans multiple sources for AI developments and sends you updates.

Commands:
/start - Subscribe to automatic updates
/stop - Unsubscribe from updates
/latest - Get latest AI news immediately
/help - Show this help

Sources monitored:
• ArXiv AI papers
• Tech news sites
• Research institutions
• AI company announcements

Updates are sent every 6 hours automatically to subscribers.
        """
        update.message.reply_text(help_text)
    
    def send_updates_to_subscribers(self):
        """Send updates to all subscribers"""
        if not self.subscribers:
            logger.info("No subscribers to send updates to")
            return
        
        try:
            # Get articles with proper error handling
            articles = []
            company_news = []
            
            try:
                articles = self.scraper.get_latest_news(hours=6) or []
            except Exception as e:
                logger.error(f"Error getting RSS news: {e}")
                articles = []
            
            try:
                company_news = self.company_scraper.get_company_announcements() or []
            except Exception as e:
                logger.error(f"Error getting company news: {e}")
                company_news = []
            
            # Ensure we have lists
            if not isinstance(articles, list):
                articles = []
            if not isinstance(company_news, list):
                company_news = []
            
            all_news = company_news + articles
            
            if not all_news:
                logger.info("No new articles found")
                return
            
            logger.info(f"Sending {len(all_news)} articles to {len(self.subscribers)} subscribers")
            
            # Use the updater's bot instance
            updater = Updater(token=self.bot_token, use_context=True)
            
            for chat_id in self.subscribers.copy():  # Use copy to avoid modification during iteration
                try:
                    updater.bot.send_message(
                        chat_id=chat_id,
                        text=f"🚨 {len(all_news)} new AI developments found!"
                    )
                    
                    for article in all_news[:10]:  # Limit to 10
                        try:
                            message = self.scraper.format_article_message(article)
                            updater.bot.send_message(
                                chat_id=chat_id,
                                text=message,
                                parse_mode=ParseMode.HTML,
                                disable_web_page_preview=True
                            )
                            time.sleep(1)  # Rate limiting
                        except Exception as e:
                            logger.error(f"Error sending article to {chat_id}: {e}")
                            continue
                        
                except Exception as e:
                    logger.error(f"Error sending to {chat_id}: {e}")
                    if "chat not found" in str(e).lower():
                        self.subscribers.discard(chat_id)
                        
        except Exception as e:
            logger.error(f"Error in send_updates_to_subscribers: {e}")
    
    def schedule_updates(self):
        """Schedule automatic updates"""
        schedule.every(6).hours.do(self.send_updates_to_subscribers)
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def run(self):
        """Run the bot"""
        # Create updater
        updater = Updater(token=self.bot_token, use_context=True)
        dispatcher = updater.dispatcher
        
        # Add handlers
        dispatcher.add_handler(CommandHandler("start", self.start_command))
        dispatcher.add_handler(CommandHandler("stop", self.stop_command))
        dispatcher.add_handler(CommandHandler("latest", self.latest_command))
        dispatcher.add_handler(CommandHandler("help", self.help_command))
        
        # Start scheduler in background thread
        scheduler_thread = threading.Thread(target=self.schedule_updates, daemon=True)
        scheduler_thread.start()
        
        logger.info("Bot started successfully!")
        
        # Start the bot
        updater.start_polling()
        updater.idle()

if __name__ == "__main__":
    bot = AINewsBot()
    bot.run()