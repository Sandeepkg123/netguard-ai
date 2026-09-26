from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float

from sqlalchemy.sql import func

from db.database import Base


class ConfigFile(Base):
    __tablename__ = "config_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_hash = Column(String, nullable=False, unique=True, index=True)
    raw_config = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())