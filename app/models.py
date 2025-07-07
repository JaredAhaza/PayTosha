from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, DECIMAL, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    tier = Column(String, default="free")
    income_level = Column(String, default="low")
    persona = Column(String, default="general")
    persona_confidence = Column(DECIMAL(3,2), default=0.0)
    persona_sources = Column(JSON, default=list)
    persona_reasoning = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_admin = Column(Boolean, default=False)

class ContextProfile(Base):
    __tablename__ = "context_profiles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    username = Column(String, nullable=False)
    location = Column(String)
    device_type = Column(String)
    browser = Column(String)
    operating_system = Column(String)
    bandwidth = Column(String)
    language = Column(String)
    context_score = Column(DECIMAL(3,2), default=0.0)
    context_persona = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="context_profiles")

class Package(Base):
    __tablename__ = "packages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    tier = Column(String(50), nullable=False)  # free, student, fair, standard, premium
    price = Column(DECIMAL(10,2), nullable=False)
    original_price = Column(DECIMAL(10,2), nullable=False)
    discount_percentage = Column(Integer, default=0)
    features = Column(JSON, nullable=False)  # Array of features
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    max_users = Column(Integer, default=1)
    storage_limit_gb = Column(Integer, default=1)
    api_calls_per_month = Column(Integer, default=1000)
    support_level = Column(String(50), default="community")  # community, email, priority, dedicated
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_packages = relationship("UserPackage", back_populates="package")

class UserPackage(Base):
    __tablename__ = "user_packages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    package_id = Column(String, ForeignKey("packages.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="active")  # active, cancelled, expired, pending
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    auto_renew = Column(Boolean, default=True)
    payment_method = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="user_packages")
    package = relationship("Package", back_populates="user_packages")
    
    # Unique constraint
    __table_args__ = (UniqueConstraint('user_id', 'package_id', name='uq_user_package'),)

# Add relationships to User model
User.context_profiles = relationship("ContextProfile", back_populates="user", cascade="all, delete-orphan")
User.user_packages = relationship("UserPackage", back_populates="user", cascade="all, delete-orphan")
