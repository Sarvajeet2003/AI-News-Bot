#!/usr/bin/env python3
"""
Simple runner script for the AI News Bot
"""

import sys
import os
from telegram_bot import AINewsBot

def main():
    try:
        print("🤖 Starting AI Advancement Tracker Bot...")
        print("📡 Monitoring AI developments worldwide...")
        print("🆓 Free for everyone!")
        print("-" * 50)
        
        bot = AINewsBot()
        bot.run()
        
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        print("\n💡 Make sure you have:")
        print("1. Created a .env file with your TELEGRAM_BOT_TOKEN")
        print("2. Installed dependencies: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()