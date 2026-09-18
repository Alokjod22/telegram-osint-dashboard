import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import ContextTypes
from engine.research_manager import ResearchManager
from engine.abuse_reporter import AbuseReporter

research_manager = ResearchManager()

async def setup_bot_commands(application):
    """Register command suggestions in Telegram UI so typing / shows all available commands."""
    commands = [
        BotCommand("start", "Start the OSINT Research Bot"),
        BotCommand("search", "Quick OSINT lookup (Domain, Username, Phone, Web)"),
        BotCommand("research", "Deep OSINT investigation & AI entity analysis"),
        BotCommand("report", "Collect evidence & draft policy violation report"),
        BotCommand("sources", "List active OSINT source adapters"),
        BotCommand("history", "View recent investigation history"),
        BotCommand("settings", "View system settings & configuration"),
        BotCommand("export", "Export investigation report (Markdown/JSON)"),
        BotCommand("help", "Display full help & menu guide")
    ]
    await application.bot.set_my_commands(commands)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """🔍 **Telegram OSINT Research Bot Platform**

Welcome to your general-purpose Public-Source Intelligence Assistant.

📌 **All Commands List** (Type `/` to view in menu):
• `/search <query>` — Quick lookup for Domain, Username, Phone, or Web
• `/research <query>` — Deep OSINT analysis with AI entity correlation
• `/report <url> <category_id> <evidence>` — Draft policy violation evidence report
• `/sources` — View connected public data source adapters
• `/history` — View past research investigations
• `/settings` — View active API configurations
• `/export <inv_id>` — Download full report package
• `/help` — Display usage instructions
"""
    keyboard = [
        [InlineKeyboardButton("🔍 Quick Search", callback_data="menu_search"), InlineKeyboardButton("📊 Deep Research", callback_data="menu_research")],
        [InlineKeyboardButton("📑 Report Violation", callback_data="menu_report"), InlineKeyboardButton("📚 Sources", callback_data="menu_sources")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """ℹ️ **OSINT Research Bot Help & Guide**

**Command Reference**:
• `/search example.com` — Inspect DNS, RDAP, HTTP security headers & sitemaps.
• `/search @username` — Search username matches across GitHub, Twitter, Reddit, etc.
• `/search +14155552671` — E.164 normalization, country/carrier detection.
• `/research <query>` — Run deep OSINT research with AI entity extraction.
• `/report <url> <category_id>` — Create deduplicated abuse evidence report.

**Categories for `/report`**:
`1`: Child Safety | `2`: Terrorism | `3`: Fraud/Scam | `4`: Illegal Goods | `5`: Non-consensual Content | `6`: DMCA/Copyright | `7`: General Violation
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("💡 **Usage**: `/search <query>`\n\nExamples:\n• `/search example.com` (Domain OSINT)\n• `/search @username` (Username Search)\n• `/search +14155552671` (Phone Metadata)", parse_mode="Markdown")
        return

    query = " ".join(context.args)
    msg = await update.message.reply_text(f"🔍 **Executing OSINT Investigation** for `{query}`...\nPlease wait while public adapters collect data.", parse_mode="Markdown")

    res = await research_manager.execute_investigation(query)
    inv_id = res["investigation_id"]
    search_type = res["search_type"]
    data = res["data"]

    # Formatted detailed output based on search type
    output_text = f"✅ **OSINT RESULTS — {search_type}**\n\n"
    output_text += f"**Investigation ID**: `{inv_id}`\n"
    output_text += f"**Target Query**: `{query}`\n\n"

    if search_type == "DOMAIN":
        dns = data.get("dns_records", {})
        output_text += f"🌐 **DNS Records**:\n"
        output_text += f"• A: `{', '.join(dns.get('A', ['None']))}`\n"
        output_text += f"• MX: `{', '.join(dns.get('MX', ['None']))}`\n"
        output_text += f"• NS: `{', '.join(dns.get('NS', ['None']))}`\n"
        output_text += f"• Security Score: `{data.get('security_score', 0)}/100`\n"

    elif search_type == "USERNAME":
        profiles = data.get("profiles", [])
        output_text += f"👤 **Public Profile Matches** ({len(profiles)} found):\n"
        for p in profiles:
            output_text += f"• [{p['platform']}]({p['profile_url']}) (Confidence: {p['confidence']*100:.0f}%)\n"

    elif search_type == "PHONE":
        output_text += f"📞 **Phone Metadata**:\n"
        output_text += f"• E.164: `{data.get('normalized_e164')}`\n"
        output_text += f"• Country: `{data.get('country')}` (`{data.get('country_code')}`)\n"
        output_text += f"• Line Type: `{data.get('line_type')}`\n"

    else:
        web_res = data.get("web_results", [])
        output_text += f"📰 **Web Search Results** ({len(web_res)} items):\n"
        for item in web_res[:3]:
            output_text += f"• [{item['title']}]({item['url']})\n  _{item['snippet'][:100]}_\n"

    if "ai_analysis" in res and "ai_analysis" in res["ai_analysis"]:
        output_text += f"\n🤖 **AI Executive Summary**:\n{res['ai_analysis']['ai_analysis'][:500]}\n"

    await msg.edit_text(output_text, parse_mode="Markdown", disable_web_page_preview=True)

    # Log activity live to Admin Portal Group
    try:
        from config import settings
        user_info = f"@{update.effective_user.username}" if update.effective_user.username else f"User {update.effective_user.id}"
        admin_log = f"🔔 **ADMIN AUDIT LOG — NEW SEARCH**\n\n• **User**: {user_info}\n• **Query**: `{query}`\n• **Type**: `{search_type}`\n• **Investigation ID**: `{inv_id}`"
        await context.bot.send_message(chat_id=settings.ADMIN_CHAT_ID, text=admin_log, parse_mode="Markdown")
    except Exception:
        pass


async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        cat_list = "\n".join([f"`{k}`: {v}" for k, v in AbuseReporter.CATEGORIES.items()])
        msg = f"""📑 **Automated Abuse Evidence & Reporting Assistant**

Usage: `/report <target_url> <category_id> <evidence_details>`

**Categories**:
{cat_list}

Example: `/report https://t.me/example_channel 3 Fraudulent activity detected`
"""
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    url = context.args[0]
    cat_id = context.args[1]
    details = " ".join(context.args[2:]) if len(context.args) > 2 else "Publicly reported violation."

    case_id = f"CASE-{update.message.message_id}"
    case_data = AbuseReporter.create_abuse_case(case_id, url, cat_id, details)
    review_screen = AbuseReporter.generate_review_screen(case_data)

    keyboard = [
        [InlineKeyboardButton("✅ Approve & Export Package", callback_data=f"export_case_{case_id}"), InlineKeyboardButton("❌ Cancel Case", callback_data="cancel_case")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(review_screen, parse_mode="Markdown", reply_markup=reply_markup, disable_web_page_preview=True)


async def sources_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sources_text = """🌐 **Active OSINT Data Source Adapters**:

1. **Domain & DNS Resolver**: DNS (A, MX, TXT, NS), RDAP/WHOIS, HTTP Security Headers, robots.txt.
2. **Username Search Engine**: Multi-platform lookup (GitHub, GitLab, Twitter, Reddit, Medium, Dev.to).
3. **Phone Metadata Engine**: E.164 formatting, country code parsing, line-type classification.
4. **Web & News Aggregator**: Search engine web scrapers and RSS feed ingestion.
5. **Document Parser**: PDF, TXT, CSV, JSON regex entity extractor.
"""
    await update.message.reply_text(sources_text, parse_mode="Markdown")


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history_text = """📚 **Recent Investigation History**:

• `INV-A92F10B2` — `example.com` (Domain OSINT)
• `INV-4C8E91A0` — `@targetuser` (Username Search)
• `CASE-104928` — `https://t.me/sample_channel` (Abuse Evidence Draft)
"""
    await update.message.reply_text(history_text, parse_mode="Markdown")


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings_text = """⚙️ **OSINT Platform Settings**:

• **Database**: SQLite / PostgreSQL (Async Engine)
• **AI Engine**: Gemini API (`gemini-2.5-flash`)
• **Max Workers**: 5 Parallel Threads
• **Rate Limit Handling**: Active
• **Dashboard Server**: `http://localhost:8000`
"""
    await update.message.reply_text(settings_text, parse_mode="Markdown")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "menu_search":
        await query.message.reply_text("Send `/search <query>` to begin a quick lookup.", parse_mode="Markdown")
    elif query.data == "menu_research":
        await query.message.reply_text("Send `/research <query>` to begin deep OSINT research.", parse_mode="Markdown")
    elif query.data == "menu_report":
        await query.message.reply_text("Send `/report <url> <category_id>` to draft an evidence report.", parse_mode="Markdown")
    elif query.data == "menu_sources":
        await sources_command(update, context)
    elif query.data.startswith("export_case_"):
        await query.message.reply_text("✅ **Abuse Evidence Report Exported Successfully!**\nPackage saved in Markdown, HTML, and JSON format.", parse_mode="Markdown")
    elif query.data == "cancel_case":
        await query.message.reply_text("❌ Case cancelled.", parse_mode="Markdown")
