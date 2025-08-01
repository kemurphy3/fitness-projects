from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, Text, JSON, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .db import Base

class Team(Base):
    __tablename__ = "teams"
    
    team_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    organization = Column(String(100))
    level = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="team", cascade="all, delete-orphan")
    players = relationship("Player", back_populates="team", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.team_id", ondelete="CASCADE"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    team = relationship("Team", back_populates="users")

class Player(Base):
    __tablename__ = "players"

    player_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.team_id", ondelete="CASCADE"), index=True)
    name = Column(String(100), nullable=False)
    position = Column(String(20))
    jersey_number = Column(Integer)
    birth_date = Column(Date)
    baseline_rhr = Column(Integer)
    baseline_hrv = Column(Float)
    max_hr = Column(Integer)
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    team = relationship("Team", back_populates="players")
    training_sessions = relationship("TrainingSession", back_populates="player", cascade="all, delete-orphan")
    wellness_checks = relationship("WellnessCheck", back_populates="player", cascade="all, delete-orphan")
    readiness_scores = relationship("ReadinessScore", back_populates="player", cascade="all, delete-orphan")
    polar_imports = relationship("PolarImport", back_populates="player", cascade="all, delete-orphan")

class TrainingSession(Base):
    __tablename__ = "training_sessions"
    
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.player_id", ondelete="CASCADE"), index=True)
    date = Column(Date, nullable=False, index=True)
    session_type = Column(String(50))
    duration_min = Column(Integer)
    distance_m = Column(Float)
    high_speed_running_m = Column(Float)
    sprint_distance_m = Column(Float)
    accelerations = Column(Integer)
    decelerations = Column(Integer)
    avg_hr = Column(Integer)
    max_hr = Column(Integer)
    hr_zones = Column(JSON)
    training_load = Column(Float)
    rpe = Column(Integer, CheckConstraint('rpe BETWEEN 1 AND 10'))
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    player = relationship("Player", back_populates="training_sessions")

class WellnessCheck(Base):
    __tablename__ = "wellness_checks"
    
    check_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.player_id", ondelete="CASCADE"), index=True)
    date = Column(Date, nullable=False, index=True)
    sleep_hours = Column(Float, CheckConstraint('sleep_hours BETWEEN 0 AND 24'))
    sleep_quality = Column(Integer, CheckConstraint('sleep_quality BETWEEN 1 AND 5'))
    soreness = Column(Integer, CheckConstraint('soreness BETWEEN 1 AND 5'))
    fatigue = Column(Integer, CheckConstraint('fatigue BETWEEN 1 AND 5'))
    stress = Column(Integer, CheckConstraint('stress BETWEEN 1 AND 5'))
    mood = Column(Integer, CheckConstraint('mood BETWEEN 1 AND 5'))
    hydration = Column(Integer, CheckConstraint('hydration BETWEEN 1 AND 5'))
    nutrition_quality = Column(Integer, CheckConstraint('nutrition_quality BETWEEN 1 AND 5'))
    cycle_phase = Column(String(20))
    cycle_symptoms = Column(Text)
    injury_status = Column(String(50))
    injury_notes = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    player = relationship("Player", back_populates="wellness_checks")

class ReadinessScore(Base):
    __tablename__ = "readiness_scores"
    
    score_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.player_id", ondelete="CASCADE"), index=True)
    date = Column(Date, nullable=False, index=True)
    overall_score = Column(Float, CheckConstraint('overall_score BETWEEN 0 AND 100'))
    training_load_score = Column(Float, CheckConstraint('training_load_score BETWEEN 0 AND 100'))
    wellness_score = Column(Float, CheckConstraint('wellness_score BETWEEN 0 AND 100'))
    recovery_score = Column(Float, CheckConstraint('recovery_score BETWEEN 0 AND 100'))
    acute_load = Column(Float)
    chronic_load = Column(Float)
    acwr = Column(Float)
    readiness_flag = Column(String(10), CheckConstraint("readiness_flag IN ('green', 'yellow', 'red')"), index=True)
    recommendations = Column(ARRAY(Text))
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    player = relationship("Player", back_populates="readiness_scores")

class PolarImport(Base):
    __tablename__ = "polar_imports"
    
    import_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.player_id", ondelete="CASCADE"))
    file_name = Column(String(255))
    file_hash = Column(String(64))
    import_date = Column(DateTime, server_default=func.now())
    records_imported = Column(Integer)
    status = Column(String(20))
    error_message = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    player = relationship("Player", back_populates="polar_imports")
