from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="viewer")
    created_at = Column(DateTime, default=datetime.utcnow)
class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    prompt = Column(Text, nullable=False)
    tool_list = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    scenarios = relationship("Scenario", back_populates="agent", cascade="all, delete-orphan")
    baselines = relationship("Baseline", back_populates="agent", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="agent", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="agent", cascade="all, delete-orphan")
    drift_histories = relationship("DriftHistory", back_populates="agent", cascade="all, delete-orphan")
    stores = relationship("Store", back_populates="agent", cascade="all, delete-orphan")


class Baseline(Base):
    __tablename__ = "baselines"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(String(50), default="created")
    fingerprint = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    agent = relationship("Agent", back_populates="baselines")
    sessions = relationship("Session", back_populates="baseline")
    metrics = relationship("BehaviorMetric", back_populates="baseline", cascade="all, delete-orphan")
    drift_histories = relationship("DriftHistory", back_populates="baseline", cascade="all, delete-orphan")


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    expected_tools = Column(JSON, nullable=False, default=list)
    instructions = Column(Text, nullable=False)
    cluster_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    agent = relationship("Agent", back_populates="scenarios")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    baseline_id = Column(Integer, ForeignKey("baselines.id"), nullable=True)
    status = Column(String(50), default="recorded")
    request_payload = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    agent = relationship("Agent", back_populates="sessions")
    baseline = relationship("Baseline", back_populates="sessions")
    metrics = relationship("BehaviorMetric", back_populates="session", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="session", cascade="all, delete-orphan")


class BehaviorMetric(Base):
    __tablename__ = "behavior_metrics"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    baseline_id = Column(Integer, ForeignKey("baselines.id"), nullable=False)
    latency_ms = Column(Float, nullable=False, default=0.0)
    response_length = Column(Integer, nullable=False, default=0)
    execution_time_ms = Column(Float, nullable=False, default=0.0)
    tool_count = Column(Integer, nullable=False, default=0)
    error_count = Column(Integer, nullable=False, default=0)
    data_access_count = Column(Integer, nullable=False, default=0)
    tool_frequencies = Column(JSON, nullable=False, default=dict)
    tool_sequence = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="metrics")
    baseline = relationship("Baseline", back_populates="metrics")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True)
    severity = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    score = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    agent = relationship("Agent", back_populates="alerts")
    session = relationship("Session", back_populates="alerts")


class DriftHistory(Base):
    __tablename__ = "drift_history"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    baseline_id = Column(Integer, ForeignKey("baselines.id"), nullable=False)
    drift_score = Column(Float, nullable=False, default=0.0)
    details = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    agent = relationship("Agent", back_populates="drift_histories")
    baseline = relationship("Baseline", back_populates="drift_histories")


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    key = Column(String(255), nullable=False, index=True)
    value = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    agent = relationship("Agent", back_populates="stores")
