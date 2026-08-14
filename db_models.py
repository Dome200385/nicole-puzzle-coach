from datetime import datetime
from sqlalchemy import Column,Integer,String,DateTime,Text,Float,Boolean
from app.database import Base
class OAuthToken(Base):
    __tablename__="oauth_tokens"
    id=Column(Integer,primary_key=True)
    owner_key=Column(String(80),unique=True,index=True,nullable=False,default="nicole")
    encrypted_payload=Column(Text,nullable=False)
    updated_at=Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)
class SyncSnapshot(Base):
    __tablename__="sync_snapshots"
    id=Column(Integer,primary_key=True)
    owner_key=Column(String(80),index=True,nullable=False,default="nicole")
    profile_json=Column(Text,nullable=False,default="{}")
    results_json=Column(Text,nullable=False,default="{}")
    statistics_json=Column(Text,nullable=False,default="{}")
    collections_json=Column(Text,nullable=False,default="{}")
    synced_at=Column(DateTime,default=datetime.utcnow,nullable=False)
class Tournament(Base):
    __tablename__="tournaments"
    id=Column(Integer,primary_key=True)
    name=Column(String(200),nullable=False); date=Column(String(20),nullable=False)
    location=Column(String(200)); mode=Column(String(20),default="solo")
    manufacturer=Column(String(120)); piece_count=Column(Integer)
    time_limit_minutes=Column(Integer); priority=Column(String(20),default="normal")
    international=Column(Boolean,default=False); notes=Column(Text)
    created_at=Column(DateTime,default=datetime.utcnow)
class TrainingSession(Base):
    __tablename__="training_sessions"
    id=Column(Integer,primary_key=True)
    date=Column(String(20),nullable=False); puzzle_name=Column(String(250),nullable=False)
    puzzle_id=Column(String(120)); manufacturer=Column(String(120)); piece_count=Column(Integer)
    mode=Column(String(20),default="solo"); duration_seconds=Column(Integer); target_seconds=Column(Integer)
    tournament_id=Column(Integer); perceived_difficulty=Column(Float); focus=Column(String(200)); notes=Column(Text)
    created_at=Column(DateTime,default=datetime.utcnow)
