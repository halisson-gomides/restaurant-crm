"""Client registration models for CNPJ/CPF registration system."""
from sqlalchemy import Column, String, Text, Date, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class Address(BaseModel):
    """Address model for storing Brazilian addresses."""
    __tablename__ = "addresses"
    
    cep = Column(String(9), nullable=False, index=True)
    endereco = Column(Text, nullable=False)
    bairro = Column(String(100), nullable=True)
    cidade = Column(String(100), nullable=False)
    estado = Column(String(2), nullable=False)


class RegistrationSession(BaseModel):
    """Registration session management for multi-step forms."""
    __tablename__ = "registration_sessions"
    
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    registration_type = Column(String(10), nullable=False)  # 'CNPJ' or 'CPF'
    step = Column(Integer, default=1)
    is_completed = Column(Boolean, default=False)
    data = Column(Text)  # JSON string for form data


class CNPJRegistration(BaseModel):
    """CNPJ business registration data."""
    __tablename__ = "cnpj_registrations"
    
    # Business information
    qual_seu_negocio = Column(String(100), nullable=False)
    cnpj = Column(String(18), unique=True, nullable=False, index=True)
    razao_social = Column(String(255), nullable=False)
    seu_nome = Column(String(255), nullable=False)
    sua_funcao = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    celular = Column(String(20), nullable=False)
    
    # Terms and marketing consent
    terms_accepted = Column(Boolean, default=False)
    marketing_opt_in = Column(Boolean, default=False)
    
    # Address information
    cep = Column(String(9), nullable=False)
    endereco = Column(Text, nullable=False)
    bairro = Column(String(100), nullable=False)
    cidade = Column(String(100), nullable=False)
    estado = Column(String(2), nullable=False)
    
    # No direct relationship to Address as data is stored directly


class CPFRegistration(BaseModel):
    """CPF individual registration data."""
    __tablename__ = "cpf_registrations"
    
    # Purchase profile
    perfil_compra = Column(String(20), nullable=False)  # 'casa', 'negocio', 'ambos'
    qual_negocio_cpf = Column(String(255))  # Conditional field
    
    # Personal information
    cpf = Column(String(14), unique=True, nullable=False, index=True)
    nome_completo = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    genero = Column(String(20), nullable=False)
    celular = Column(String(20), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    
    # Terms and marketing consent
    terms_accepted = Column(Boolean, default=False)
    marketing_opt_in = Column(Boolean, default=False)
    
    # Address information
    cep = Column(String(9), nullable=False)
    endereco = Column(Text, nullable=False)
    bairro = Column(String(100), nullable=False)
    cidade = Column(String(100), nullable=False)
    estado = Column(String(2), nullable=False)
    
    # No direct relationship to Address as data is stored directly


class Organization(BaseModel):
    """Organization model for companies."""
    __tablename__ = "organizations"
    
    cnpj = Column(String(18), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    trade_name = Column(String(255))
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(255), unique=True, index=True)
    
    # Registration relation
    cnpj_registration_id = Column(String, ForeignKey("cnpj_registrations.id"))


class User(BaseModel):
    """User model with registration support."""
    __tablename__ = "users"
    
    username = Column(String(20), unique=True, nullable=False, index=True)  # CPF or CNPJ
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    organization_id = Column(String, ForeignKey("organizations.id"))
    role = Column(String(20), nullable=False)  # admin, manager, employee, shopper, customer
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    
    # Registration type and data
    registration_type = Column(String(10))  # 'CNPJ' or 'CPF'
    registration_data = Column(Text)  # JSON string
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    user_roles = relationship("UserRole", back_populates="user")


class UserRole(BaseModel):
    """User roles for multi-role support."""
    __tablename__ = "user_roles"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    role = Column(String(20), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="user_roles")
    organization = relationship("Organization", back_populates="user_roles")


# Relationships for Organization
Organization.users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
Organization.user_roles = relationship("UserRole", back_populates="organization")