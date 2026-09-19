from datetime import datetime
from sqlalchemy import select, desc, update
from database.session import AsyncSessionLocal
from database.models import BotUser, WelcomeConfig

GLOBAL_DEFAULT_LIMIT = 1000

async def record_user_activity(telegram_id: str, username: str = None, first_name: str = None, last_name: str = None, phone_number: str = None, is_query: bool = False, is_report: bool = False, ip: str = None):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(BotUser).where(BotUser.telegram_id == str(telegram_id)))
        user = result.scalars().first()
        is_new = False
        if not user:
            is_new = True
            user = BotUser(
                telegram_id=str(telegram_id),
                username=username,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                is_verified=1 if phone_number else 0,
                query_count=1 if is_query else 0,
                report_count=1 if is_report else 0,
                max_report_limit=GLOBAL_DEFAULT_LIMIT,
                language_code="en",
                user_role="MEMBER",
                first_seen=datetime.utcnow(),
                last_active=datetime.utcnow(),
                last_ip=ip
            )
            session.add(user)
        else:
            if username is not None:
                user.username = username
            if first_name is not None:
                user.first_name = first_name
            if last_name is not None:
                user.last_name = last_name
            if phone_number is not None:
                user.phone_number = phone_number
                user.is_verified = 1
            if is_query:
                user.query_count = (user.query_count or 0) + 1
            if is_report:
                user.report_count = (user.report_count or 0) + 1
            if ip is not None:
                user.last_ip = ip
            user.last_active = datetime.utcnow()
        await session.commit()
        await session.refresh(user)
        return user, is_new

async def get_user_by_telegram_id(telegram_id: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(BotUser).where(BotUser.telegram_id == str(telegram_id)))
        return result.scalars().first()

async def set_user_language(telegram_id: str, lang_code: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(BotUser).where(BotUser.telegram_id == str(telegram_id)))
        user = result.scalars().first()
        if user:
            user.language_code = lang_code
            await session.commit()
            return True
        return False

async def get_welcome_config(key: str, default: str = ""):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(WelcomeConfig).where(WelcomeConfig.key == key))
        cfg = result.scalars().first()
        return cfg.value if cfg and cfg.value else default

async def set_welcome_config(key: str, value: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(WelcomeConfig).where(WelcomeConfig.key == key))
        cfg = result.scalars().first()
        if not cfg:
            cfg = WelcomeConfig(key=key, value=value)
            session.add(cfg)
        else:
            cfg.value = value
        await session.commit()
        return True

async def get_all_users(limit: int = 100):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(BotUser).order_by(desc(BotUser.last_active)).limit(limit))
        return result.scalars().all()

async def get_user_stats():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(BotUser))
        users = result.scalars().all()
        total_users = len(users)
        verified_users = sum(1 for u in users if u.phone_number or u.is_verified)
        total_queries = sum(u.query_count or 0 for u in users)
        total_reports = sum(u.report_count or 0 for u in users)
        return {
            "total_users": total_users,
            "verified_users": verified_users,
            "total_queries": total_queries,
            "total_reports": total_reports
        }

async def get_user_report_stats(telegram_id: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(BotUser).where(BotUser.telegram_id == str(telegram_id)))
        user = result.scalars().first()
        count = user.report_count if user else 0
        limit = user.max_report_limit if (user and user.max_report_limit) else GLOBAL_DEFAULT_LIMIT
        return {
            "telegram_id": telegram_id,
            "reports_sent": count,
            "max_limit": limit,
            "remaining_quota": max(0, limit - count)
        }

async def set_user_report_limit(telegram_id: str, new_limit: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(BotUser).where(BotUser.telegram_id == str(telegram_id)))
        user = result.scalars().first()
        if user:
            user.max_report_limit = new_limit
            await session.commit()
            return True
        return False

async def set_global_report_limit(new_limit: int):
    global GLOBAL_DEFAULT_LIMIT
    GLOBAL_DEFAULT_LIMIT = new_limit
    async with AsyncSessionLocal() as session:
        await session.execute(update(BotUser).values(max_report_limit=new_limit))
        await session.commit()
    return True

async def log_chat_message(telegram_id: str, username: str = None, message_text: str = "", sender_type: str = "USER"):
    if not message_text:
        return
    async with AsyncSessionLocal() as session:
        from database.models import ChatMessage
        msg = ChatMessage(
            telegram_id=str(telegram_id),
            username=username,
            sender_type=sender_type,
            message_text=message_text,
            timestamp=datetime.utcnow()
        )
        session.add(msg)
        await session.commit()

async def get_user_chat_history(telegram_id: str, limit: int = 100):
    async with AsyncSessionLocal() as session:
        from database.models import ChatMessage
        result = await session.execute(
            select(ChatMessage)
            .where(ChatMessage.telegram_id == str(telegram_id))
            .order_by(ChatMessage.timestamp.asc())
            .limit(limit)
        )
        return result.scalars().all()

async def get_maintenance_mode() -> bool:
    val = await get_welcome_config("maintenance_mode", "0")
    return val == "1"

async def set_maintenance_mode(enabled: bool) -> bool:
    val = "1" if enabled else "0"
    return await set_welcome_config("maintenance_mode", val)

