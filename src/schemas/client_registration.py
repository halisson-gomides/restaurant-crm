"""Client registration schemas for CNPJ/CPF registration system."""
from pydantic import BaseModel, EmailStr, field_validator, Field, model_validator
from typing import Optional, List, Dict, Any
from datetime import date
import re


class RegistrationSessionCreate(BaseModel):
    """Registration session creation schema."""
    registration_type: str = Field(..., pattern="^(CNPJ|CPF)$")


# Address schemas
class AddressBase(BaseModel):
    """Base address schema."""
    cep: str = Field(..., description="Brazilian postal code")
    endereco: str = Field(..., description="Street address")
    bairro: str = Field(..., description="Neighborhood")
    cidade: str = Field(..., description="City")
    estado: str = Field(..., description="State (2-letter abbreviation)")

    @field_validator('estado')
    def validate_estado(cls, v):
        """Validate Brazilian state abbreviations."""
        valid_states = [
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
            'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
            'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
        ]
        if v.upper() not in valid_states:
            raise ValueError(f'State must be one of: {", ".join(valid_states)}')
        return v.upper()


class AddressCreate(AddressBase):
    """Address creation schema."""
    pass


class AddressOut(AddressBase):
    """Address output schema."""
    id: str
    
    class Config:
        from_attributes = True


# CNPJ Registration schemas
class CNPJStep1(BaseModel):
    """CNPJ registration step 1 schema."""
    qual_seu_negocio: str = Field(..., description="Type of business")
    cnpj: str = Field(..., description="Company CNPJ")
    razao_social: str = Field(..., description="Company legal name")
    seu_nome: str = Field(..., description="Your name")
    sua_funcao: str = Field(..., description="Your role in the company")
    email: EmailStr
    celular: str = Field(..., description="Mobile phone")
    terms_accepted: bool = Field(..., description="Terms acceptance")
    marketing_opt_in: Optional[bool] = Field(default=False, description="Marketing consent")

    @field_validator('qual_seu_negocio')
    def validate_business_type(cls, v):
        """Validate business type options."""
        valid_types = [
            "Academia", "Adega", "Bar", "Bomboniere", "Cantina", "Clube esportivo",
            "Condomínio", "Confeitaria", "Doceria", "Dogueiro", "Escola", 
            "Food service", "Hotel", "Instituição religiosa", "Lanchonete", 
            "Mercearia", "Mini mercado", "Padaria", "Pastelaria", "Pizzaria", 
            "Restaurante", "Outros"
        ]
        if v not in valid_types:
            raise ValueError(f'Business type must be one of: {", ".join(valid_types)}')
        return v

    @field_validator('sua_funcao')
    def validate_role(cls, v):
        """Validate role options."""
        valid_roles = ["Proprietário", "Gerente", "Estoquista"]
        if v not in valid_roles:
            raise ValueError(f'Role must be one of: {", ".join(valid_roles)}')
        return v

    @field_validator('cnpj')
    def validate_cnpj(cls, v):
        """Validate and format CNPJ."""
        cnpj = re.sub(r'[^0-9]', '', v)
        if len(cnpj) != 14:
            raise ValueError('CNPJ must have exactly 14 digits')
        
        if not ValidationUtils.validate_cnpj(cnpj):
            raise ValueError('Invalid CNPJ format')
        
        return ValidationUtils.format_cnpj(cnpj)

    @field_validator('celular')
    def validate_celular(cls, v):
        """Validate and format Brazilian phone number."""
        phone = re.sub(r'[^0-9]', '', v)
        if len(phone) not in [10, 11]:
            raise ValueError('Phone number must have 10 or 11 digits')
        
        return ValidationUtils.format_phone(phone)


class CNPJStep2(AddressBase):
    """CNPJ registration step 2 schema."""
    recaptcha_token: str = Field(..., description="reCAPTCHA token")


class CNPJRegistrationComplete(CNPJStep1, CNPJStep2):
    """Complete CNPJ registration schema."""
    pass


# REMOVED: CNPJRegistrationOut - not used anywhere in the codebase


# CPF Registration schemas
class CPFStep1(BaseModel):
    """CPF registration step 1 schema."""
    perfil_compra: str = Field(..., description="Purchase profile")
    qual_negocio_cpf: Optional[str] = Field(default=None, description="Business name if applicable")
    cpf: str = Field(..., description="Individual CPF")
    nome_completo: str = Field(..., description="Full name")
    email: EmailStr
    genero: str = Field(..., description="Gender")
    celular: str = Field(..., description="Mobile phone")
    terms_accepted: bool = Field(..., description="Terms acceptance")
    marketing_opt_in: Optional[bool] = Field(default=False, description="Marketing consent")

    @field_validator('perfil_compra')
    def validate_perfil_compra(cls, v):
        """Validate purchase profile options."""
        valid_profiles = ["casa", "negocio", "ambos"]
        if v not in valid_profiles:
            raise ValueError(f'Purchase profile must be one of: {", ".join(valid_profiles)}')
        return v

    @field_validator('genero')
    def validate_genero(cls, v):
        """Validate gender options."""
        valid_genders = ["Feminino", "masculino", "outros", "não quero me identificar"]
        if v not in valid_genders:
            raise ValueError(f'Gender must be one of: {", ".join(valid_genders)}')
        return v

    @field_validator('cpf')
    def validate_cpf(cls, v):
        """Validate and format CPF."""
        cpf = re.sub(r'[^0-9]', '', v)
        if len(cpf) != 11:
            raise ValueError('CPF must have exactly 11 digits')
        
        if not ValidationUtils.validate_cpf(cpf):
            raise ValueError('Invalid CPF format')
        
        return ValidationUtils.format_cpf(cpf)

    @model_validator(mode='after')
    def validate_business_field(self):
        """Validate conditional business name field using model validator."""
        if self.perfil_compra in ['negocio', 'ambos'] and (not self.qual_negocio_cpf or not self.qual_negocio_cpf.strip()):
            raise ValueError('Business name is required when profile is "Seu negócio" or "Para ambos"')
        return self

    @field_validator('celular')
    def validate_celular(cls, v):
        """Validate and format Brazilian phone number."""
        phone = re.sub(r'[^0-9]', '', v)
        if len(phone) not in [10, 11]:
            raise ValueError('Phone number must have 10 or 11 digits')
        
        return ValidationUtils.format_phone(phone)


class CPFStep2(BaseModel):
    """CPF registration step 2 schema."""
    data_nascimento: date = Field(..., description="Birth date")
    cep: str
    endereco: str
    bairro: str
    cidade: str
    estado: str
    recaptcha_token: str = Field(..., description="reCAPTCHA token")

    @field_validator('estado')
    def validate_estado(cls, v):
        """Validate Brazilian state abbreviations."""
        valid_states = [
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
            'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
            'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
        ]
        if v.upper() not in valid_states:
            raise ValueError(f'State must be one of: {", ".join(valid_states)}')
        return v.upper()


class CPFRegistrationComplete(CPFStep1, CPFStep2):
    """Complete CPF registration schema."""
    pass


class RegistrationSessionOut(BaseModel):
    """Registration session output schema."""
    session_id: str
    registration_type: str
    step: int
    is_completed: bool
    data: Optional[Dict[str, Any]] = None
    created_at: str
    
    class Config:
        from_attributes = True


# Document validation schemas
class DocumentValidationResponse(BaseModel):
    """Document validation response schema."""
    valid: bool
    message: str



# Validation utilities
class ValidationUtils:
    """Validation utilities for Brazilian documents and formatting."""

    @staticmethod
    def validate_cnpj(cnpj: str) -> bool:
        """Validate CNPJ using official algorithm."""
        cnpj = re.sub(r'[^0-9]', '', cnpj)
        
        if len(cnpj) != 14:
            return False
        
        # Check for known invalid CNPJs (all same digit)
        if cnpj == cnpj[0] * 14:
            return False
        
        # Calculate first digit
        weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        sum1 = sum(int(cnpj[i]) * weights1[i] for i in range(12))
        digit1 = 11 - (sum1 % 11)
        if digit1 >= 10:
            digit1 = 0
        
        # Calculate second digit
        weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        sum2 = sum(int(cnpj[i]) * weights2[i] for i in range(13))
        digit2 = 11 - (sum2 % 11)
        if digit2 >= 10:
            digit2 = 0
        
        # Verify calculated digits
        return int(cnpj[12]) == digit1 and int(cnpj[13]) == digit2

    @staticmethod
    def validate_cpf(cpf: str) -> bool:
        """Validate CPF using official algorithm."""
        cpf = re.sub(r'[^0-9]', '', cpf)
        
        if len(cpf) != 11:
            return False
        
        # Check for known invalid CPFs (all same digit)
        if cpf == cpf[0] * 11:
            return False
        
        # Calculate first digit
        sum1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digit1 = 11 - (sum1 % 11)
        if digit1 >= 10:
            digit1 = 0
        
        # Calculate second digit
        sum2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digit2 = 11 - (sum2 % 11)
        if digit2 >= 10:
            digit2 = 0
        
        # Verify calculated digits
        return int(cpf[9]) == digit1 and int(cpf[10]) == digit2

    @staticmethod
    def format_cnpj(cnpj: str) -> str:
        """Format CNPJ with proper masking."""
        cnpj = re.sub(r'[^0-9]', '', cnpj)
        if len(cnpj) == 14:
            return re.sub(r'(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})', r'\1.\2.\3/\4-\5', cnpj)
        return cnpj

    @staticmethod
    def format_cpf(cpf: str) -> str:
        """Format CPF with proper masking."""
        cpf = re.sub(r'[^0-9]', '', cpf)
        if len(cpf) == 11:
            return re.sub(r'(\d{3})(\d{3})(\d{3})(\d{2})', r'\1.\2.\3-\4', cpf)
        return cpf

    @staticmethod
    def format_phone(phone: str) -> str:
        """Format Brazilian phone number."""
        phone = re.sub(r'[^0-9]', '', phone)
        if len(phone) == 11:
            # Mobile: (11) 99999-9999
            return re.sub(r'(\d{2})(\d{5})(\d{4})', r'(\1) \2-\3', phone)
        elif len(phone) == 10:
            # Landline: (11) 9999-9999
            return re.sub(r'(\d{2})(\d{4})(\d{4})', r'(\1) \2-\3', phone)
        return phone

    @staticmethod
    def format_cep(cep: str) -> str:
        """Format Brazilian postal code."""
        cep = re.sub(r'[^0-9]', '', cep)
        if len(cep) == 8:
            return re.sub(r'(\d{5})(\d{3})', r'\1-\2', cep)
        return cep