from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker
from app.config import DATABASE_URL
ca={"check_same_thread":False} if DATABASE_URL.startswith("sqlite") else {}
engine=create_engine(DATABASE_URL,pool_pre_ping=True,connect_args=ca)
SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False)
Base=declarative_base()
def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()
