# AI Advancement Tracker Bot 🤖

A free Telegram bot that tracks the latest AI product releases, model launches, and company announcements from major AI companies worldwide.

## Features

- 🚀 Tracks AI product releases from OpenAI, Anthropic, Google, Microsoft, Meta
- 📰 Monitors tech news for AI announcements and launches  
- 🔄 Automatic updates every 6 hours
- 🎯 Smart filtering for actual AI products (not research papers)
- 💬 Interactive Telegram commands
- 🆓 Completely free for all users

## Setup Instructions

### 1. Create a Telegram Bot

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow the instructions
3. Save your bot token

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

1. Copy `.env.example` to `.env`
2. Add your bot token:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### 4. Run the Bot

```bash
python telegram_bot.py
```

## Bot Commands

- `/start` - Subscribe to AI updates
- `/stop` - Unsubscribe from updates
- `/latest` - Get latest AI news immediately
- `/help` - Show help message

## News Sources

The bot monitors these sources for AI product releases:

- **Company Blogs**: OpenAI, Anthropic, Google AI, Microsoft AI, Meta AI
- **TechCrunch**: AI product announcements
- **VentureBeat**: AI company news
- **The Verge**: AI product reviews and launches
- **AI News**: Industry announcements and releases

## Deployment Options

### Free Hosting Options:

1. **Railway** (Recommended)
   - Connect your GitHub repo
   - Add environment variables
   - Deploy automatically

2. **Heroku** (Free tier)
   - Create a new app
   - Connect GitHub repo
   - Add config vars

3. **PythonAnywhere** (Free tier)
   - Upload files
   - Set up scheduled tasks

### VPS Options:
- DigitalOcean ($5/month)
- Linode ($5/month)
- AWS EC2 (Free tier available)

## Contributing

This is a free tool for the betterment of the world! Contributions welcome:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - Free for everyone to use and modify.

## Support

If you find this bot helpful, please share it with others who might benefit from staying updated on AI developments!