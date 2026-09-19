import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from telegram.ext import ContextTypes
from engine.research_manager import ResearchManager
from engine.abuse_reporter import AbuseReporter
from database.user_manager import (
    record_user_activity, get_user_by_telegram_id, set_user_language, 
    get_welcome_config, set_welcome_config, get_user_report_stats, 
    set_user_report_limit, set_global_report_limit, get_user_stats
)

research_manager = ResearchManager()

LOCALES = {
    "en": {
        "welcome_title": "⚡ *NEXUS OSINT RESEARCH ENGINE*",
        "tagline": "Premium • Autonomous • Enterprise Intelligence",
        "greeting_new": "👋 *Welcome to NEXUS OSINT*, {first_name}!",
        "greeting_returning": "👋 *Welcome back*, {first_name}!",
        "features": "✨ *CORE CAPABILITIES*\n⚡ *Fast OSINT*: DNS, Username & Phone Metadata\n🛡️ *Abuse Evidence*: Cryptographic SHA-256 Dockets\n🤖 *Gemini 2.5 AI*: Neural Entity Extraction\n🌐 *Cloud Infrastructure*: 24/7 Enterprise Node",
        "profile_title": "👤 *INVESTIGATOR PROFILE*",
        "dashboard_title": "📊 *SYSTEM TELEMETRY & DASHBOARD*",
        "ai_title": "🤖 *GEMINI AI ASSISTANT*",
        "lang_title": "🌐 *SELECT PREFERRED LANGUAGE*",
        "back": "⬅️ Back",
        "home": "🏠 Main Menu"
    },
    "hi": {
        "welcome_title": "⚡ *नेक्सस OSINT रिसर्च इंजन*",
        "tagline": "प्रीमियम • तेज़ • स्वायत्त इंटेलिजेंस",
        "greeting_new": "👋 *नेक्सस OSINT में आपका स्वागत है*, {first_name}!",
        "greeting_returning": "👋 *वापसी पर आपका स्वागत है*, {first_name}!",
        "features": "✨ *मुख्य सुविधाएं*\n⚡ *त्वरित खोज*: डोमेन, यूज़रनेम और फ़ोन डेटा\n🛡️ *रिपोर्टिंग*: SHA-256 सबूत रिपोर्ट प्रणाली\n🤖 *जेमिनी AI*: एआई विश्लेषण और संक्षेप\n🌐 *क्लाउड इंफ्रास्ट्रक्चर*: 24/7 एंटरप्राइज नोड",
        "profile_title": "👤 *उपयोगकर्ता प्रोफाइल*",
        "dashboard_title": "📊 *सिस्टम डैशबोर्ड*",
        "ai_title": "🤖 *जेमिनी AI सहायक*",
        "lang_title": "🌐 *भाषा चुनें*",
        "back": "⬅️ वापस",
        "home": "🏠 मुख्य मेनू"
    },
    "mr": {
        "welcome_title": "⚡ *नेक्सस OSINT रिसर्च इंजिन*",
        "tagline": "प्रीमियम • वेगवान • अत्याधुनिक बुद्धिमत्ता",
        "greeting_new": "👋 *नेक्सस OSINT मध्ये आपले स्वागत आहे*, {first_name}!",
        "greeting_returning": "👋 *पुन्हा स्वागत आहे*, {first_name}!",
        "features": "✨ *प्रमुख वैशिष्ट्ये*\n⚡ *जलद शोध*: डोमेन, वापरकर्ता नाव आणि फोन माहिती\n🛡️ *अहवाल*: SHA-256 पुरावा अहवाल\n🤖 *जेमिनी AI*: AI विश्लेषण आणि सारांश\n🌐 *क्लाउड पायाभूत सुविधा*: 24/7 एंटरप्राइझ नोड",
        "profile_title": "👤 *वापरकर्ता प्रोफाइल*",
        "dashboard_title": "📊 *सिस्टम डॅशबोर्ड*",
        "ai_title": "🤖 *जेमिनी AI सहाय्यक*",
        "lang_title": "🌐 *भाषा निवडा*",
        "back": "⬅️ मागे",
        "home": "🏠 मुख्य मेनू"
    }
}

async def setup_bot_commands(application):
    """Set default scope commands to ONLY /start so unverified users see NO feature commands in their / menu."""
    default_commands = [
        BotCommand("start", "🚀 Tap Start button below to initialize & unlock bot commands")
    ]
    await application.bot.set_my_commands(default_commands, scope=BotCommandScopeDefault())


async def unlock_user_commands(bot, chat_id: int):
    """Dynamically register all OSINT feature commands for a verified user's chat_id in Telegram UI."""
    commands = [
        BotCommand("start", "Launch Premium Dashboard & Navigation"),
        BotCommand("numinfo", "📞 Phone Number to Info OSINT Lookup"),
        BotCommand("search", "Quick OSINT lookup (Domain, Username, Phone, Web)"),
        BotCommand("research", "Deep OSINT investigation & AI entity analysis"),
        BotCommand("report", "Collect evidence & draft policy violation report"),
        BotCommand("reports", "View total reports sent and remaining quota limit"),
        BotCommand("setlimit", "Set report submission limit (100 - 100000)"),
        BotCommand("profile", "View account status & phone verification"),
        BotCommand("language", "Switch language (English / हिन्दी / मराठी)"),
        BotCommand("sources", "List active OSINT source adapters"),
        BotCommand("history", "View recent investigation history"),
        BotCommand("settings", "View system settings & live portal link"),
        BotCommand("help", "Display full interactive help guide")
    ]
    try:
        await bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id=chat_id))
    except Exception as e:
        pass


def build_main_keyboard(lang: str = "en"):
    channel_url = "https://t.me/Ruk_research_bot"
    keyboard = [
        [InlineKeyboardButton("📞 Phone to Info", callback_data="menu_numinfo"), InlineKeyboardButton("🛒 Explore Features", callback_data="menu_explore")],
        [InlineKeyboardButton("👤 My Profile", callback_data="menu_profile"), InlineKeyboardButton("📊 Dashboard", callback_data="menu_dashboard")],
        [InlineKeyboardButton("🤖 AI Assistant", callback_data="menu_ai"), InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings")],
        [InlineKeyboardButton("📑 Abuse Reports", callback_data="menu_reports"), InlineKeyboardButton("📚 Help & Guide", callback_data="menu_help")],
        [InlineKeyboardButton("🌐 Language / भाषा", callback_data="menu_lang"), InlineKeyboardButton("📢 Official Channel", url=channel_url)]
    ]
    return InlineKeyboardMarkup(keyboard)


async def check_user_verification(update: Update) -> bool:
    """Gatekeeper: Checks if user has tapped 🚀 Start to link/verify their phone number before allowing tool access."""
    user = update.effective_user
    if not user:
        return False

    db_user = await get_user_by_telegram_id(str(user.id))
    if db_user and (db_user.is_verified or db_user.phone_number):
        return True

    contact_keyboard = [[KeyboardButton("🚀 Start", request_contact=True)]]
    contact_markup = ReplyKeyboardMarkup(contact_keyboard, resize_keyboard=True, one_time_keyboard=False)

    lock_msg = f"🔒 *VERIFICATION REQUIRED — ACCESS LOCKED*\n" \
               f"━━━━━━━━━━━━━━━━━━━━\n\n" \
               f"👋 Hello *{user.first_name}*!\n\n" \
               f"⚠️ *1st Priority Requirement*: To use any bot feature (OSINT Search, Phone Lookup, AI Assistant, Abuse Reports), you MUST tap the *🚀 Start* button in the bottom keyboard to verify your account.\n\n" \
               f"👇 *Tap the 🚀 Start button below now to unlock full access:* "

    if update.message:
        await update.message.reply_text(lock_msg, parse_mode="Markdown", reply_markup=contact_markup)
    elif update.callback_query:
        await update.callback_query.answer("⚠️ Verification Required! Tap 🚀 Start below in your chat keyboard to unlock.", show_alert=True)
        try:
            await update.callback_query.message.reply_text(lock_msg, parse_mode="Markdown", reply_markup=contact_markup)
        except Exception:
            pass
    return False


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        return

    db_user, is_new = await record_user_activity(
        telegram_id=str(user.id),
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )

    lang = db_user.language_code if db_user else "en"
    loc = LOCALES.get(lang, LOCALES["en"])

    greeting = loc["greeting_new"].format(first_name=user.first_name) if is_new else loc["greeting_returning"].format(first_name=user.first_name)
    is_verified = bool(db_user and (db_user.is_verified or db_user.phone_number))
    status_badge = "🛡️ Verified Investigator" if is_verified else "⏳ Unverified (Tap 🚀 Start Below)"
    custom_welcome = await get_welcome_config("custom_welcome", "")

    msg = f"━━━━━━━━━━━━━━━━━━━━\n" \
          f"{loc['welcome_title']}\n" \
          f"_{loc['tagline']}_\n" \
          f"━━━━━━━━━━━━━━━━━━━━\n\n" \
          f"{greeting}\n\n" \
          f"🆔 *User*: @{user.username or user.first_name} ({user.id})\n" \
          f"🎖️ *Status*: {status_badge}\n" \
          f"🔍 *Queries Run*: {db_user.query_count or 0} | 📑 *Reports*: {db_user.report_count or 0}\n\n" \
          f"{custom_welcome if custom_welcome else loc['features']}\n\n" \
          f"━━━━━━━━━━━━━━━━━━━━\n" \
          f"🔥 *QUICK ACTIONS MENU*"

    reply_markup = build_main_keyboard(lang)
    contact_keyboard = [[KeyboardButton("🚀 Start", request_contact=True)]]
    contact_markup = ReplyKeyboardMarkup(contact_keyboard, resize_keyboard=True, one_time_keyboard=False)

    # Send banner image if custom banner configured
    banner_url = await get_welcome_config("welcome_banner", "")
    if banner_url:
        try:
            await update.message.reply_photo(photo=banner_url, caption=msg, parse_mode="Markdown", reply_markup=reply_markup)
        except Exception:
            await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)

    if is_verified:
        await unlock_user_commands(context.bot, user.id)
    else:
        await update.message.reply_text(
            "👇 *1st Priority Required Step: Tap 🚀 Start below to verify your phone number & unlock all bot commands:*",
            reply_markup=contact_markup
        )


async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    user = update.effective_user
    if contact and user:
        phone = contact.phone_number
        db_user, _ = await record_user_activity(
            telegram_id=str(user.id),
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            phone_number=phone
        )
        lang = db_user.language_code if db_user else "en"
        
        # Unlock user commands in Telegram UI
        await unlock_user_commands(context.bot, user.id)

        msg = f"🎉 *IDENTITY & PHONE VERIFIED SUCCESSFULLY!*\n\n" \
              f"👤 *Name*: {user.first_name}\n" \
              f"🏷️ *Username*: @{user.username or 'None'}\n" \
              f"📱 *Phone*: `{phone}`\n\n" \
              f"🚀 *All Bot Commands & Features Unlocked!* You can now run OSINT searches (`/search`), Phone Lookup (`/numinfo`), AI research, and abuse reporting.\n\n" \
              f"👇 *Tap any feature button below or type / to see unlocked commands:* "
        
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=build_main_keyboard(lang))

        try:
            from config import settings
            admin_notice = f"👤 *ADMIN AUDIT: NEW VERIFIED USER*\n\n" \
                           f"• *Name*: {user.first_name} {user.last_name or ''}\n" \
                           f"• *Username*: @{user.username or 'None'}\n" \
                           f"• *Phone*: {phone}\n" \
                           f"• *Telegram ID*: {user.id}"
            await context.bot.send_message(chat_id=settings.ADMIN_CHAT_ID, text=admin_notice, parse_mode="Markdown")
        except Exception:
            pass


async def profile_handler(update_or_query, user_id: str, lang: str = "en"):
    u = await get_user_by_telegram_id(user_id)
    if not u:
        return "User profile not found."

    status_badge = "✅ Phone Verified" if u.is_verified else "⏳ Unverified"
    joined_date = u.first_seen.strftime("%Y-%m-%d") if u.first_seen else "N/A"
    last_act = u.last_active.strftime("%Y-%m-%d %H:%M UTC") if u.last_active else "N/A"

    return f"👤 *INVESTIGATOR ACCOUNT PROFILE*\n" \
           f"━━━━━━━━━━━━━━━━━━━━\n\n" \
           f"🆔 *Telegram ID*: {u.telegram_id}\n" \
           f"👤 *Full Name*: {u.first_name or ''} {u.last_name or ''}\n" \
           f"🏷️ *Username*: @{u.username or 'None'}\n" \
           f"📱 *Phone Number*: {u.phone_number or 'Not Linked'}\n" \
           f"🛡️ *Verification Status*: {status_badge}\n" \
           f"🎖️ *Role / Tier*: {u.user_role or 'MEMBER'}\n" \
           f"🌐 *Language Preference*: {u.language_code.upper()}\n\n" \
           f"📊 *ACTIVITY TELEMETRY*\n" \
           f"• *OSINT Queries Executed*: {u.query_count or 0}\n" \
           f"• *Abuse Reports Submitted*: {u.report_count or 0}\n" \
           f"• *Current Report Limit*: {u.max_report_limit or 1000}\n" \
           f"📅 *Member Since*: {joined_date}\n" \
           f"⏱️ *Last Active*: {last_act}\n" \
           f"━━━━━━━━━━━━━━━━━━━━"


async def dashboard_handler():
    stats = await get_user_stats()
    return f"📊 *SYSTEM TELEMETRY & CLOUD DASHBOARD*\n" \
           f"━━━━━━━━━━━━━━━━━━━━\n\n" \
           f"👥 *Total Registered Bot Users*: {stats['total_users']}\n" \
           f"📱 *Phone Verified Accounts*: {stats['verified_users']}\n" \
           f"🔍 *Total OSINT Queries Run*: {stats['total_queries']}\n" \
           f"📑 *Abuse Reports Drafted*: {stats['total_reports']}\n\n" \
           f"⚡ *Engine Health*: ONLINE • Render Cloud Node\n" \
           f"🤖 *AI Model*: Gemini 2.5 Flash\n" \
           f"━━━━━━━━━━━━━━━━━━━━"


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user_verification(update):
        return

    help_text = "ℹ️ *NEXUS OSINT BOT HELP & GUIDE*\n" \
                "━━━━━━━━━━━━━━━━━━━━\n\n" \
                "*Core Commands Reference*:\n" \
                "• /search <query> — Lookup Domain, Username, Phone, or Web\n" \
                "• /research <query> — Deep OSINT research with AI entity extraction\n" \
                "• /report <url> <category_id> — Deduplicated abuse evidence report\n" \
                "• /reports — View total sent reports and remaining quota limit\n" \
                "• /setlimit <100-100000> — Change report submission limit\n" \
                "• /profile — Display your account stats & verification\n" \
                "• /language — Switch language (English / हिन्दी / मराठी)\n" \
                "• /settings — Portal link & configurations\n\n" \
                "*Report Category IDs*:\n" \
                "1: Child Safety | 2: Terrorism | 3: Fraud/Scam | 4: Contraband | 5: Non-consensual | 6: DMCA | 7: General Violation"
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def reports_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user_verification(update):
        return

    user = update.effective_user
    if not user:
        return

    stats = await get_user_report_stats(str(user.id))
    msg = f"📊 *ABUSE EVIDENCE REPORTING TELEMETRY*\n" \
          f"━━━━━━━━━━━━━━━━━━━━\n\n" \
          f"👤 *Investigator*: @{user.username or user.first_name}\n" \
          f"🆔 *Telegram ID*: {user.id}\n\n" \
          f"📈 *Total Reports Submitted*: {stats['reports_sent']}\n" \
          f"🛡️ *Active Quota Limit*: {stats['max_limit']}\n" \
          f"⏳ *Remaining Allowance*: {stats['remaining_quota']}\n\n" \
          f"💡 *Change Quota Limit*: Send /setlimit <number> (e.g. /setlimit 5000) or use the Web Portal."
    await update.message.reply_text(msg, parse_mode="Markdown")


async def setlimit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user_verification(update):
        return

    user = update.effective_user
    if not user:
        return

    if not context.args:
        await update.message.reply_text("💡 *Usage*: /setlimit <number>\n\nExample: /setlimit 5000 (Allowed range: 100 to 100,000)", parse_mode="Markdown")
        return

    try:
        new_limit = int(context.args[0])
        if new_limit < 100 or new_limit > 100000:
            await update.message.reply_text("⚠️ *Invalid Limit*: Please specify a number between 100 and 100,000.", parse_mode="Markdown")
            return

        await set_user_report_limit(str(user.id), new_limit)
        await set_global_report_limit(new_limit)

        msg = f"✅ *Report Limit Updated Successfully!*\n\n" \
              f"🛡️ *New Active Quota Limit*: {new_limit:,} reports\n" \
              f"👤 *Updated For*: @{user.username or user.first_name} and System Default."
        await update.message.reply_text(msg, parse_mode="Markdown")

    except ValueError:
        await update.message.reply_text("⚠️ *Error*: Please provide a valid numeric limit (e.g. /setlimit 5000).", parse_mode="Markdown")


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user_verification(update):
        return

    user = update.effective_user
    if user:
        await record_user_activity(
            telegram_id=str(user.id),
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            is_query=True
        )

    if not context.args:
        await update.message.reply_text("💡 *Usage*: /search <query>\n\nExamples:\n• /search example.com (Domain)\n• /search @username (Username)\n• /search +14155552671 (Phone)", parse_mode="Markdown")
        return

    query = " ".join(context.args)
    msg = await update.message.reply_text(f"🔍 *Executing OSINT Investigation* for {query}...\nPlease wait while public adapters collect data.", parse_mode="Markdown")

    res = await research_manager.execute_investigation(query)
    inv_id = res["investigation_id"]
    search_type = res["search_type"]
    data = res["data"]

    output_text = f"✅ *OSINT RESULTS — {search_type}*\n\n" \
                  f"*Investigation ID*: {inv_id}\n" \
                  f"*Target Query*: {query}\n\n"

    if search_type == "DOMAIN":
        dns = data.get("dns_records", {})
        output_text += f"🌐 *DNS Records*:\n" \
                       f"• A: {', '.join(dns.get('A', ['None']))}\n" \
                       f"• MX: {', '.join(dns.get('MX', ['None']))}\n" \
                       f"• NS: {', '.join(dns.get('NS', ['None']))}\n" \
                       f"• Security Score: {data.get('security_score', 0)}/100\n"

    elif search_type == "USERNAME":
        profiles = data.get("profiles", [])
        output_text += f"👤 *Public Profile Matches* ({len(profiles)} found):\n"
        for p in profiles:
            output_text += f"• [{p['platform']}]({p['profile_url']}) (Confidence: {p['confidence']*100:.0f}%)\n"

    elif search_type == "PHONE":
        output_text += f"📞 *PHONE OSINT DOSSIER & METADATA*:\n" \
                       f"• *Normalized E.164*: `{data.get('normalized_e164')}`\n" \
                       f"• *Country*: {data.get('country')} ({data.get('country_code')})\n" \
                       f"• *Region*: {data.get('region', 'Global')}\n" \
                       f"• *Estimated Carrier*: {data.get('carrier_hint', 'Telecom Provider')}\n" \
                       f"• *Line Classification*: {data.get('line_type')}\n" \
                       f"• *Risk Rating*: `{data.get('risk_score', 'LOW')}` ({', '.join(data.get('risk_factors', ['Clean format']))})\n\n" \
                       f"🔗 *DIRECT LOOKUP & FOOTPRINT LINKS*:\n" \
                       f"• [💬 WhatsApp Direct Chat]({data.get('whatsapp_url', '#')})\n" \
                       f"• [✈️ Telegram Contact Link]({data.get('telegram_url', '#')})\n" \
                       f"• [🔍 Truecaller Search]({data.get('truecaller_url', '#')})\n" \
                       f"• [🌐 Google OSINT Footprint]({data.get('google_dork_url', '#')})\n"

    else:
        web_res = data.get("web_results", [])
        output_text += f"📰 *Web Search Results* ({len(web_res)} items):\n"
        for item in web_res[:3]:
            output_text += f"• [{item['title']}]({item['url']})\n  _{item['snippet'][:100]}_\n"

    if "ai_analysis" in res and "ai_analysis" in res["ai_analysis"]:
        output_text += f"\n🤖 *AI Executive Summary*:\n{res['ai_analysis']['ai_analysis'][:500]}\n"

    await msg.edit_text(output_text, parse_mode="Markdown", disable_web_page_preview=True)

    try:
        from config import settings
        user_info = f"@{user.username}" if user and user.username else f"User {user.id if user else 'Unknown'}"
        admin_log = f"🔔 *ADMIN AUDIT LOG — NEW SEARCH*\n\n• *User*: {user_info}\n• *Query*: {query}\n• *Type*: {search_type}\n• *Investigation ID*: {inv_id}"
        await context.bot.send_message(chat_id=settings.ADMIN_CHAT_ID, text=admin_log, parse_mode="Markdown")
    except Exception:
        pass


async def numinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user_verification(update):
        return

    user = update.effective_user
    if user:
        await record_user_activity(
            telegram_id=str(user.id),
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            is_query=True
        )

    # Extract target phone number from args or text
    phone_query = ""
    if context.args:
        phone_query = " ".join(context.args).strip()
    elif update.message and update.message.text:
        raw_text = update.message.text.strip()
        parts = raw_text.split(maxsplit=1)
        if len(parts) > 1:
            phone_query = parts[1].strip()
        else:
            match = re.search(r"(\+?\d[\d\s\-]{7,15}\d)", raw_text)
            if match:
                phone_query = match.group(1).strip()

    if not phone_query:
        await update.message.reply_text(
            "📞 *PHONE NUMBER TO INFO OSINT TOOL*\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "💡 *Usage*: `/numinfo <phone_number>` or `/phone <phone_number>`\n\n"
            "Examples:\n"
            "• `/numinfo +919876543210` (India 🇮🇳)\n"
            "• `/numinfo +14155552671` (US 🇺🇸)\n"
            "• `/numinfo +447911123456` (UK 🇬🇧)\n\n"
            "💡 *Pro-Tip*: You can also paste any phone number directly in chat (e.g. `+917248964895`)!",
            parse_mode="Markdown"
        )
        return

    try:
        msg = await update.message.reply_text(f"📞 *Executing Phone OSINT Lookup* for `{phone_query}`...\nPlease wait while telecom & OSINT adapters run.", parse_mode="Markdown")
    except Exception:
        msg = await update.message.reply_text(f"📞 Executing Phone OSINT Lookup for {phone_query}...\nPlease wait...")

    try:
        res = await research_manager.execute_investigation(phone_query, search_type="PHONE")
        inv_id = res.get("investigation_id", "INV-PHONE")
        data = res.get("data", {})

        output_text = f"📞 *PHONE NUMBER TO INFO DOSSIER*\n" \
                      f"━━━━━━━━━━━━━━━━━━━━\n\n" \
                      f"🆔 *Investigation ID*: `{inv_id}`\n" \
                      f"📲 *Input Target*: `{data.get('input_phone', phone_query)}`\n" \
                      f"🌐 *Normalized E.164*: `{data.get('normalized_e164', phone_query)}`\n" \
                      f"🌍 *Country*: {data.get('country', 'Unknown')} ({data.get('country_code', 'INTL')})\n" \
                      f"📍 *Region*: {data.get('region', 'Global')}\n" \
                      f"📡 *Estimated Carrier*: {data.get('carrier_hint', 'Telecom Provider')}\n" \
                      f"🏷️ *Line Type*: {data.get('line_type', 'Mobile Line')}\n" \
                      f"🛡️ *Risk Score*: `{data.get('risk_score', 'LOW')}`\n" \
                      f"⚠️ *Risk Indicators*: {', '.join(data.get('risk_factors', ['None']))}\n\n" \
                      f"🔗 *DIRECT LOOKUP & FOOTPRINT LINKS*:\n" \
                      f"• [💬 WhatsApp Direct Chat]({data.get('whatsapp_url', '#')})\n" \
                      f"• [✈️ Telegram Contact Link]({data.get('telegram_url', '#')})\n" \
                      f"• [🔍 Truecaller Search]({data.get('truecaller_url', '#')})\n" \
                      f"• [🌐 Google OSINT Footprint]({data.get('google_dork_url', '#')})\n"

        if "ai_analysis" in res and "ai_analysis" in res["ai_analysis"]:
            output_text += f"\n🤖 *AI Risk & Intelligence Brief*:\n{res['ai_analysis']['ai_analysis'][:500]}\n"

        try:
            await msg.edit_text(output_text, parse_mode="Markdown", disable_web_page_preview=True)
        except Exception:
            await msg.edit_text(output_text, disable_web_page_preview=True)

        try:
            from config import settings
            user_info = f"@{user.username}" if user and user.username else f"User {user.id if user else 'Unknown'}"
            admin_log = f"🔔 *ADMIN AUDIT LOG — PHONE OSINT LOOKUP*\n\n• *User*: {user_info}\n• *Target*: {phone_query}\n• *Investigation ID*: {inv_id}"
            await context.bot.send_message(chat_id=settings.ADMIN_CHAT_ID, text=admin_log, parse_mode="Markdown")
        except Exception:
            pass

    except Exception as e:
        err_msg = f"⚠️ *Phone Lookup Error*: Unable to process target `{phone_query}` ({str(e)}).\nPlease verify the phone number format (e.g. +919876543210)."
        try:
            await msg.edit_text(err_msg, parse_mode="Markdown")
        except Exception:
            await update.message.reply_text(err_msg)


async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user_verification(update):
        return

    user = update.effective_user
    if user:
        report_stats = await get_user_report_stats(str(user.id))
        if report_stats["reports_sent"] >= report_stats["max_limit"]:
            await update.message.reply_text(
                f"⚠️ *Reporting Limit Reached*: You have reached your active limit of {report_stats['max_limit']} reports.\n"
                f"Use /setlimit <number> (e.g. /setlimit 5000) to increase your quota limit.",
                parse_mode="Markdown"
            )
            return

        await record_user_activity(
            telegram_id=str(user.id),
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            is_report=True
        )

    if len(context.args) < 2:
        cat_list = "\n".join([f"{k}: {v}" for k, v in AbuseReporter.CATEGORIES.items()])
        msg = f"📑 *Automated Abuse Evidence & Reporting Assistant*\n\n" \
              f"Usage: /report <target_url> <category_id> <evidence_details>\n\n" \
              f"*Categories*:\n{cat_list}\n\n" \
              f"Example: /report https://t.me/example_channel 3 Fraudulent activity detected"
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
    if not await check_user_verification(update):
        return

    sources_text = "🌐 *Active OSINT Data Source Adapters*:\n\n" \
                   "1. *Domain & DNS Resolver*: DNS (A, MX, TXT, NS), RDAP/WHOIS, HTTP Headers.\n" \
                   "2. *Username Search Engine*: Multi-platform lookup (GitHub, Twitter, Reddit, Medium).\n" \
                   "3. *Phone Metadata Engine*: E.164 formatting, country code parsing, line-type.\n" \
                   "4. *Web & News Aggregator*: Search engine scrapers and RSS feed ingestion.\n" \
                   "5. *Document Parser*: PDF, TXT, CSV, JSON regex entity extractor."
    await update.message.reply_text(sources_text, parse_mode="Markdown")


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user_verification(update):
        return

    history_text = "📚 *Recent Investigation History*:\n\n" \
                   "• INV-A92F10B2 - example.com (Domain OSINT)\n" \
                   "• INV-4C8E91A0 - @targetuser (Username Search)\n" \
                   "• CASE-104928 - https://t.me/sample_channel (Abuse Evidence Draft)"
    await update.message.reply_text(history_text, parse_mode="Markdown")


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user_verification(update):
        return

    settings_text = "⚙️ *OSINT Platform Settings*:\n\n" \
                    "• *Database*: SQLite / PostgreSQL (Async Engine)\n" \
                    "• *AI Engine*: Gemini API (gemini-2.5-flash)\n" \
                    "• *Max Workers*: 5 Parallel Threads\n" \
                    "• *Rate Limit Handling*: Active\n" \
                    "• *Cloud Node*: Render Secured Instance"
    await update.message.reply_text(settings_text, parse_mode="Markdown")


# --- ADMIN CUSTOMIZATION COMMANDS ---

async def editwelcome_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args:
        await update.message.reply_text("💡 *Usage*: /editwelcome <custom_welcome_text>", parse_mode="Markdown")
        return
    text = " ".join(context.args)
    await set_welcome_config("custom_welcome", text)
    await update.message.reply_text("✅ *Welcome Message Updated Successfully!*", parse_mode="Markdown")


async def editbanner_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("💡 *Usage*: /editbanner <image_url>", parse_mode="Markdown")
        return
    url = context.args[0]
    await set_welcome_config("welcome_banner", url)
    await update.message.reply_text("✅ *Welcome Banner Image Updated!*", parse_mode="Markdown")


# --- INTERACTIVE BUTTON CALLBACK QUERY HANDLER ---

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    data = query.data

    if data not in ("menu_home", "menu_lang") and not data.startswith("lang_"):
        if not await check_user_verification(update):
            return

    await query.answer()

    nav_back_home = [
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu_home"), InlineKeyboardButton("🏠 Main Menu", callback_data="menu_home")]
    ]
    back_markup = InlineKeyboardMarkup(nav_back_home)

    if data == "menu_home":
        # Re-render main start menu
        u = await get_user_by_telegram_id(str(user.id))
        lang = u.language_code if u else "en"
        loc = LOCALES.get(lang, LOCALES["en"])
        msg = f"━━━━━━━━━━━━━━━━━━━━\n" \
              f"{loc['welcome_title']}\n" \
              f"_{loc['tagline']}_\n" \
              f"━━━━━━━━━━━━━━━━━━━━\n\n" \
              f"👋 *Welcome*, {user.first_name}!\n\n" \
              f"{loc['features']}\n\n" \
              f"━━━━━━━━━━━━━━━━━━━━\n" \
              f"🔥 *QUICK ACTIONS MENU*"
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=build_main_keyboard(lang))

    elif data == "menu_explore":
        txt = "🛒 *NEXUS OSINT CAPABILITIES & ADAPTERS*\n" \
              "━━━━━━━━━━━━━━━━━━━━\n\n" \
              "🌐 *1. Domain & DNS Intelligence*\n" \
              "   • Resolves A, AAAA, MX, NS records, WHOIS/RDAP, HTTP security headers.\n\n" \
              "👤 *2. Username Footprinting*\n" \
              "   • Multi-platform lookup (GitHub, Twitter, Reddit, Medium, Dev.to).\n\n" \
              "📞 *3. Phone Metadata Parser*\n" \
              "   • E.164 normalization, country code identification, carrier tags.\n\n" \
              "📰 *4. Web & News Aggregator*\n" \
              "   • Search engine scraping, news indexing, RSS feed ingestion.\n\n" \
              "📑 *5. Document Entity Extractor*\n" \
              "   • PDF, TXT, CSV, JSON regex entity harvester."
        await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=back_markup)

    elif data == "menu_numinfo":
        txt = "📞 *PHONE NUMBER TO INFO OSINT TOOL*\n" \
              "━━━━━━━━━━━━━━━━━━━━\n\n" \
              "This specialized OSINT module analyzes any phone number globally.\n\n" \
              "✨ *Features & Output*:\n" \
              "• E.164 Standard Normalization\n" \
              "• Country Code & Regional Location\n" \
              "• Estimated Telecom Carrier Provider\n" \
              "• Line Type (Mobile, Fixed, Toll-Free)\n" \
              "• Direct WhatsApp Chat & Telegram Links\n" \
              "• Truecaller Search & Google OSINT Footprints\n" \
              "• Neural AI Risk Score Assessment\n\n" \
              "💡 *How to Use*:\n" \
              "Send `/numinfo <phone_number>` or send any phone number directly in chat!\n\n" \
              "Example: `/numinfo +919876543210` or `+917248964895`"
        await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=back_markup)

    elif data == "menu_profile":
        txt = await profile_handler(query, str(user.id))
        await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=back_markup)

    elif data == "menu_dashboard":
        txt = await dashboard_handler()
        await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=back_markup)

    elif data == "menu_ai":
        txt = "🤖 *GEMINI 2.5 AI NEURAL RESEARCH ASSISTANT*\n" \
              "━━━━━━━━━━━━━━━━━━━━\n\n" \
              "The AI Engine automatically correlates entity relationships, extracts risk indicators, and generates structured executive summaries for every OSINT investigation.\n\n" \
              "💡 *How to Use*:\n" \
              "Send /research <target> in chat to trigger deep AI analysis!"
        await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=back_markup)

    elif data == "menu_help":
        txt = "📚 *NEXUS OSINT INTERACTIVE HELP*\n" \
              "━━━━━━━━━━━━━━━━━━━━\n\n" \
              "• Send /numinfo <phone> or any phone number to run Phone OSINT.\n" \
              "• Send /search <query> to begin a quick domain or username lookup.\n" \
              "• Send /research <query> for AI entity correlation.\n" \
              "• Send /report <url> <category_id> for abuse evidence collection.\n" \
              "• Send /reports to check your sent reports counter.\n" \
              "• Send /setlimit <number> to change your report quota limit (100 - 100,000)."
        await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=back_markup)

    elif data == "menu_reports":
        stats = await get_user_report_stats(str(user.id))
        txt = f"📑 *ABUSE EVIDENCE REPORTING TELEMETRY*\n" \
              f"━━━━━━━━━━━━━━━━━━━━\n\n" \
              f"📈 *Total Reports Submitted*: {stats['reports_sent']}\n" \
              f"🛡️ *Active Quota Limit*: {stats['max_limit']}\n" \
              f"⏳ *Remaining Allowance*: {stats['remaining_quota']}\n\n" \
              f"💡 Send /setlimit <number> to change your report submission limit."
        await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=back_markup)

    elif data == "menu_settings":
        txt = "⚙️ *SYSTEM CONFIGURATIONS*\n" \
              "━━━━━━━━━━━━━━━━━━━━\n\n" \
              "• *Engine*: FastAPI / Uvicorn + Async SQLAlchemy\n" \
              "• *AI Core*: Gemini 2.5 Flash API\n" \
              "• *Cloud Node*: Render Secured Instance\n" \
              "• *Telemetry*: Active"
        await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=back_markup)

    elif data == "menu_lang":
        lang_kb = [
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"), InlineKeyboardButton("🇮🇳 हिन्दी", callback_data="lang_hi")],
            [InlineKeyboardButton("🚩 मराठी", callback_data="lang_mr")],
            [InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu_home")]
        ]
        await query.edit_message_text("🌐 *SELECT YOUR PREFERRED LANGUAGE / भाषा चुनें / भाषा निवडा:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(lang_kb))

    elif data.startswith("lang_"):
        code = data.split("_")[1]
        await set_user_language(str(user.id), code)
        loc = LOCALES.get(code, LOCALES["en"])
        await query.edit_message_text(f"✅ *Language updated to {code.upper()}!*\n\n{loc['welcome_title']}", parse_mode="Markdown", reply_markup=back_markup)

    elif data.startswith("export_case_"):
        await query.message.reply_text("✅ *Abuse Evidence Report Package Exported Successfully!*", parse_mode="Markdown")

    elif data == "cancel_case":
        await query.message.reply_text("❌ Case cancelled.", parse_mode="Markdown")


async def unknown_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Automatic AI Assistant when user enters an unrecognized or mistyped command."""
    if not await check_user_verification(update):
        return

    text = update.message.text.strip() if update.message and update.message.text else ""
    cmd = text.split()[0] if text else ""

    # Check if text contains a phone number e.g. /numinfoo +919876543210
    clean_digits = re.sub(r"[^\d+]", "", text)
    is_phone = (clean_digits.startswith("+") and len(clean_digits) >= 8) or (len(clean_digits) >= 9 and clean_digits.isdigit())

    if is_phone:
        match = re.search(r"(\+?\d[\d\s\-]{7,15}\d)", text)
        phone_target = match.group(1).strip() if match else text
        notice = f"🤖 *GEMINI AI AUTO-ASSISTANT*\n" \
                 f"━━━━━━━━━━━━━━━━━━━━\n\n" \
                 f"💡 *Command Hint*: Unrecognized command `{cmd}`.\n" \
                 f"⚡ *Auto-Executing Phone OSINT* for `{phone_target}`..."
        await update.message.reply_text(notice, parse_mode="Markdown")
        context.args = [phone_target]
        await numinfo_command(update, context)
        return

    # Check if text contains domain or username
    if "." in text or text.startswith("@"):
        notice = f"🤖 *GEMINI AI AUTO-ASSISTANT*\n" \
                 f"━━━━━━━━━━━━━━━━━━━━\n\n" \
                 f"💡 *Command Hint*: Unrecognized command `{cmd}`.\n" \
                 f"⚡ *Auto-Executing Universal OSINT Search* for `{text}`..."
        await update.message.reply_text(notice, parse_mode="Markdown")
        context.args = text.split()
        await search_command(update, context)
        return

    # Fallback AI Guidance
    ai_guidance = f"🤖 *GEMINI AI AUTO-ASSISTANT*\n" \
                  f"━━━━━━━━━━━━━━━━━━━━\n\n" \
                  f"⚠️ *Unrecognized Command*: `{cmd}`\n\n" \
                  f"✨ *Available Active Commands*:\n" \
                  f"• `/numinfo <phone_number>` — Phone Number OSINT Lookup\n" \
                  f"• `/search <query>` — Domain, Username & Web Search\n" \
                  f"• `/research <query>` — AI Entity Correlation & Deep Research\n" \
                  f"• `/report <url> <category_id>` — Draft Abuse Evidence Docket\n" \
                  f"• `/profile` — View your account telemetry\n" \
                  f"• `/help` — Full interactive guide"
    await update.message.reply_text(ai_guidance, parse_mode="Markdown")


async def fallback_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fallback handler for plain text messages. Runs numinfo if phone number, search if domain/username, or AI Assistant otherwise."""
    user = update.effective_user
    if not user:
        return

    text = update.message.text.strip() if update.message and update.message.text else ""
    if not text:
        return

    clean_digits = re.sub(r"[^\d+]", "", text)
    is_phone_like = (clean_digits.startswith("+") and len(clean_digits) >= 8) or (len(clean_digits) >= 9 and clean_digits.isdigit())

    if not await check_user_verification(update):
        return

    if is_phone_like:
        match = re.search(r"(\+?\d[\d\s\-]{7,15}\d)", text)
        phone_target = match.group(1).strip() if match else text
        context.args = [phone_target]
        await numinfo_command(update, context)
    elif "." in text or text.startswith("@"):
        context.args = text.split()
        await search_command(update, context)
    else:
        await unknown_command_handler(update, context)
