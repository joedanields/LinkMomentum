from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime
import os
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./ai_curator.db')


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith('sqlite') else {})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class AuditLog(Base):
__tablename__ = 'audit_logs'
id = Column(Integer, primary_key=True, index=True)
user_id = Column(String, nullable=True)
timestamp = Column(DateTime, default=datetime.datetime.utcnow)
num_photos_uploaded = Column(Integer)
num_photos_selected = Column(Integer)
linkedin_post_id = Column(String, nullable=True)
status = Column(String)
metadata = Column(JSON, nullable=True)


def init_db():
Base.metadata.create_all(bind=engine)


def create_audit_log(db_session, **kwargs):
log = AuditLog(**kwargs)
db_session.add(log)
db_session.commit()
db_session.refresh(log)
return log