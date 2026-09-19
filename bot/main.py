import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import settings
from database.session import init_db
from bot.handlers import (
    start_command, help_command, search_command, numinfo_command, report_command, reports_command, setlimit_command,
    editwelcome_command, editbanner_command, sources_command, history_command, settings_command, 
    button_handler, contact_handler, fallback_text_handler, unknown_command_handler, setup_bot_commands
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def main():
    asyncio.run(init_db())

    if not settings.TELEGRAM_BOT_TOKEN or settings.TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("Error: TELEGRAM_BOT_TOKEN is not set in config or environment variables.")
        return

    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).post_init(setup_bot_commands).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("numinfo", numinfo_command))
    app.add_handler(CommandHandler("num", numinfo_command))
    app.add_handler(CommandHandler("phone", numinfo_command))
    app.add_handler(CommandHandler("phoneinfo", numinfo_command))
    app.add_handler(CommandHandler("numsearch", numinfo_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CommandHandler("research", search_command))
    app.add_handler(CommandHandler("report", report_command))
    app.add_handler(CommandHandler("reports", reports_command))
    app.add_handler(CommandHandler("setlimit", setlimit_command))
    app.add_handler(CommandHandler("editwelcome", editwelcome_command))
    app.add_handler(CommandHandler("editbanner", editbanner_command))
    app.add_handler(CommandHandler("sources", sources_command))
    app.add_handler(CommandHandler("history", history_command))
    app.add_handler(CommandHandler("settings", settings_command))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_text_handler))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("OSINT Research Bot is running with Premium /start & Telemetry...")
    app.run_polling()

if __name__ == "__main__":
    main()
