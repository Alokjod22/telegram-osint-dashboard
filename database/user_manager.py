from datetime import datetime
from sqlalchemy import select, desc
from database.session import AsyncSessionLocal
from database.models import BotUser

MAX_REPORT_LIMIT_PER_USER = 1000  # Configurable quota limit between 100 and 100,000

async def record_user_activity(telegram_id: str, username: str = None, first_name: str = None, last_name: str = None, phone_number: str = None, is_query: bool = False, is_report: bool = False, ip: str = None):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(BotUser).where(BotUser.telegram_id == str(telegram_id)))
        user = result.scalars().first()
        if not user:
            user = BotUser(
                telegram_id=str(telegram_id),
                username=username,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                is_verified=1 if phone_number else 0,
                query_count=1 if is_query else 0,
                report_count=1 if is_report else 0,
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
        return user

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
        return {
            "telegram_id": telegram_id,
            "reports_sent": count,
            "max_limit": MAX_REPORT_LIMIT_PER_USER,
            "remaining_quota": max(0, MAX_REPORT_LIMIT_PER_USER - count)
        }
