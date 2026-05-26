from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Configuração da URL do banco de dados local (SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"

# Criação do motor de conexão
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Sessão para conversar com o banco
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base para a criação das tabelas
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # Relação com a tabela de logs
    logs = relationship("APILog", back_populates="user")

class APILog(Base):
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    endpoint = Column(String)
    data_hora = Column(DateTime, default=datetime.utcnow)
    resposta_json = Column(Text)
    
    # Relação de volta para o usuário
    user = relationship("User", back_populates="logs")