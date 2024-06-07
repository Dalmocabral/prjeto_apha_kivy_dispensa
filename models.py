from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    dataCreated = Column(DateTime, default=datetime.utcnow, nullable=False)
    afastado = Column(Boolean, default=False)
    dataDispensa = Column(DateTime, nullable=True)

    def __repr__(self):
        return f'<User {self.name}>'

# Configuração do banco de dados
engine = create_engine('sqlite:///users.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
