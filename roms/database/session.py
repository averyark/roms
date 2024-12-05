from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine('sqlite:///mock_database.db')
Session = sessionmaker(bind=engine)
session = Session()
