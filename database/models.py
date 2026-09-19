from datetime import datetime
import json
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    investigation_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    query = Column(String(550), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="ACTIVE")

    searches = relationship("SearchRecord", back_populates="investigation", cascade="all, delete-orphan")
    entities = relationship("Entity", back_populates="investigation", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="investigation", cascade="all, delete-orphan")


class SearchRecord(Base):
    __tablename__ = "search_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    investigation_id = Column(String(50), ForeignKey("investigations.investigation_id"), nullable=False)
    search_type = Column(String(50), nullable=False)
    query = Column(String(500), nullable=False)
    raw_results = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    investigation = relationship("Investigation", back_populates="searches")


class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    investigation_id = Column(String(50), ForeignKey("investigations.investigation_id"), nullable=False)
    entity_type = Column(String(50), nullable=False)
    value = Column(String(255), nullable=False)
    confidence = Column(Float, default=1.0)
    source_url = Column(String(500), nullable=True)
    metadata_json = Column(Text, nullable=True)

    investigation = relationship("Investigation", back_populates="entities")


class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(Integer, primary_key=True, autoincrement=True)
    investigation_id = Column(String(50), nullable=False, index=True)
    source_entity = Column(String(255), nullable=False)
    target_entity = Column(String(255), nullable=False)
    relation_type = Column(String(100), nullable=False)
    confidence = Column(Float, default=1.0)
    source_url = Column(String(500), nullable=True)


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    investigation_id = Column(String(50), ForeignKey("investigations.investigation_id"), nullable=False)
    report_type = Column(String(50), default="OSINT_SUMMARY")
    content_markdown = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    investigation = relationship("Investigation", back_populates="reports")


# --- ABUSE EVIDENCE & CASE TRACKING MODELS ---

class AbuseCase(Base):
    __tablename__ = "abuse_cases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String(50), unique=True, nullable=False, index=True)
    target_url = Column(String(500), nullable=False)
    category = Column(String(100), nullable=False)
    status = Column(String(50), default="DRAFT") # DRAFT, REVIEWED, SUBMITTED
    created_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)

    evidence_items = relationship("AbuseEvidence", back_populates="case", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="case", cascade="all, delete-orphan")


class AbuseEvidence(Base):
    __tablename__ = "abuse_evidence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String(50), ForeignKey("abuse_cases.case_id"), nullable=False)
    evidence_url = Column(String(500), nullable=False)
    content_hash = Column(String(64), nullable=False, index=True) # SHA-256 for deduplication
    snippet = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("AbuseCase", back_populates="evidence_items")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String(50), ForeignKey("abuse_cases.case_id"), nullable=False)
    action = Column(String(100), nullable=False) # CASE_CREATED, EVIDENCE_ADDED, DUPLICATE_BLOCKED, REPORT_EXPORTED, SUBMITTED
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    case = relationship("AbuseCase", back_populates="audit_logs")


class BotUser(Base):
    __tablename__ = "bot_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(String(50), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone_number = Column(String(50), nullable=True)
    is_verified = Column(Integer, default=0) # 0 = unverified, 1 = verified
    query_count = Column(Integer, default=0)
    report_count = Column(Integer, default=0)
    max_report_limit = Column(Integer, default=1000)
    language_code = Column(String(10), default="en")
    user_role = Column(String(20), default="MEMBER") # MEMBER, PREMIUM, ADMIN
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    last_ip = Column(String(50), nullable=True)


class WelcomeConfig(Base):
    __tablename__ = "welcome_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(50), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(String(50), nullable=False, index=True)
    username = Column(String(100), nullable=True)
    sender_type = Column(String(20), default="USER") # USER or BOT
    message_text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)




