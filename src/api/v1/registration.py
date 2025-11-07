"""Registration API endpoints for CNPJ/CPF registration system."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any
import json
from pydantic import ValidationError
from ...database import get_database
from ...schemas.client_registration import (
    RegistrationSessionOut,
    CNPJStep1, CNPJStep2, CNPJRegistrationComplete,
    CPFStep1, CPFStep2, CPFRegistrationComplete,
    DocumentValidationResponse
)
from ...services.client_registration_service import (
    ClientRegistrationService, ViaCEPService, ReCAPTCHAService
)
from ...utils.helpers import remove_accents
from ...utils.templates import company_context
from ...config import settings

router = APIRouter(prefix="/registration", tags=["registration"])

# Create shared templates instance with custom filters
templates = Jinja2Templates(directory="templates")
templates.env.filters['remove_accents'] = remove_accents


@router.post("/session")
async def create_registration_session(
    request: Request,
    db: AsyncSession = Depends(get_database)
):
    """Create a new registration session and return session info."""
    data = await request.form()
    registration_type = data.get("registration_type", "CNPJ")

    service = ClientRegistrationService()
    session = await service.create_registration_session(db, registration_type)

    # Return JSON response with session info - frontend handles form rendering
    return {
        "success": True,
        "session_id": str(session.session_id),
        "registration_type": str(session.registration_type),
        "message": f"Session created for {registration_type} registration"
    }


@router.get("/session/{session_id}", response_model=RegistrationSessionOut)
async def get_registration_session(
    session_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get registration session details."""
    service = ClientRegistrationService()
    session = await service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration session not found")
    
    return RegistrationSessionOut.model_validate(session)


# CNPJ Registration Endpoints
@router.post("/cnpj/step1")
async def validate_cnpj_step1(
    session_id: str,
    step1_data: CNPJStep1,
    db: AsyncSession = Depends(get_database)
):
    """Validate CNPJ step 1 data and store in session."""
    service = ClientRegistrationService()
    session = await service.get_session(db, session_id)
    
    if not session or session.registration_type != "CNPJ":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid registration session")
    
    try:
        # Validate CNPJ format
        clean_cnpj = step1_data.cnpj.replace('.', '').replace('/', '').replace('-', '')
        validation_result = await service.validate_document_uniqueness(db, clean_cnpj, "CNPJ")
        if not validation_result.valid:
            return {"success": False, "error": "CNPJ já registrado"}
        
        # Store step 1 data
        await service.update_session_data(db, session_id, 1, step1_data.dict())
        
        return {
            "success": True,
            "message": "Step 1 validation successful",
            "next_step": 2,
            "data": step1_data.model_dump()
        }
    except ValueError as e:
        # Handle Pydantic validation errors more gracefully
        error_str = str(e)
        if "validation error" in error_str:
            return {"success": False, "error": error_str}
        return {"success": False, "error": f"Erro de validação: {error_str}"}
    except Exception as e:
        return {"success": False, "error": f"Validation error: {str(e)}"}


@router.post("/cnpj/step2")
async def complete_cnpj_registration(
    session_id: str,
    step2_data: CNPJStep2,
    db: AsyncSession = Depends(get_database)
):
    """Complete CNPJ registration."""
    service = ClientRegistrationService()
    session = await service.get_session(db, session_id)
    
    if not session or str(session.registration_type) != "CNPJ":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid registration session")
    
    # Verify reCAPTCHA
    if not await ReCAPTCHAService.verify_recaptcha(step2_data.recaptcha_token):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="reCAPTCHA verification failed")
    
    try:
        # Get stored step 1 data
        session_data = str(session.data) if session.data else None
        if session_data and session_data != "None":
            step1_data = CNPJStep1(**json.loads(session_data))
            complete_data = {**step1_data.model_dump(), **step2_data.model_dump()}
            
            registration = await service.complete_cnpj_registration(db, CNPJRegistrationComplete(**complete_data))
            
            # Mark session as completed
            await service.update_session_data(db, session_id, 2, {"completed": True, "registration_id": registration.id})
            
            return {
                "success": True,
                "message": "Registration completed successfully", 
                "registration_id": registration.id,
                "redirect_url": "/"
            }
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Step 1 data not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.__repr__())


# CPF Registration Endpoints  
@router.post("/cpf/step1")
async def validate_cpf_step1(
    session_id: str,
    step1_data: CPFStep1,
    db: AsyncSession = Depends(get_database)
):
    """Validate CPF step 1 data and store in session."""
    service = ClientRegistrationService()
    session = await service.get_session(db, session_id)
    
    if not session or str(session.registration_type) != "CPF":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid registration session")
    
    try:
        # Validate CPF format
        clean_cpf = step1_data.cpf.replace('.', '').replace('-', '')
        validation_result = await service.validate_document_uniqueness(db, clean_cpf, "CPF")
        if not validation_result.valid:
            return {"success": False, "error": "CPF já registrado"}
        
        # Store step 1 data
        await service.update_session_data(db, session_id, 1, step1_data.model_dump())
        
        return {
            "success": True, 
            "message": "Step 1 validation successful", 
            "next_step": 2,
            "data": step1_data.model_dump()
        }
    except Exception as e:
        return {"success": False, "error": f"Validation error: {str(e)}"}


@router.post("/cpf/step2")
async def complete_cpf_registration(
    session_id: str,
    step2_data: CPFStep2,
    db: AsyncSession = Depends(get_database)
):
    """Complete CPF registration."""
    service = ClientRegistrationService()
    session = await service.get_session(db, session_id)
    
    if not session or str(session.registration_type) != "CPF":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid registration session")
    
    # Verify reCAPTCHA
    if not await ReCAPTCHAService.verify_recaptcha(step2_data.recaptcha_token):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="reCAPTCHA verification failed")
    
    try:
        # Get stored step 1 data
        session_data = str(session.data) if session.data is not None else None
        print(f"session_data: {session_data}")
        if session_data and session_data != "None":
            step1_data = CPFStep1(**json.loads(session_data))
            complete_data = {**step1_data.model_dump(), **step2_data.model_dump()}
            registration = await service.complete_cpf_registration(db, CPFRegistrationComplete(**complete_data))
            
            # Mark session as completed
            await service.update_session_data(db, session_id, 2, {"completed": True, "registration_id": registration.id})
            
            return {
                "success": True,
                "message": "Registration completed successfully", 
                "registration_id": registration.id,
                "redirect_url": "/"
            }
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Step 1 data not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.__repr__())


# Utility Endpoints
@router.get("/validate/document/{document_type}/{document}", response_model=DocumentValidationResponse)
async def validate_document_uniqueness(
    document_type: str,
    document: str,
    db: AsyncSession = Depends(get_database)
):
    """Validate document uniqueness in real-time."""
    service = ClientRegistrationService()
    return await service.validate_document_uniqueness(db, document, document_type)


@router.get("/address/cep/{cep}")
async def get_address_by_cep(cep: str):
    """Get address information by CEP and return JSON data."""
    try:
        # Clean CEP format
        clean_cep = cep.replace("-", "").replace(".", "").strip()
        
        if len(clean_cep) != 8:
            return {
                "success": False,
                "error": "CEP deve conter 8 dígitos"
            }
        
        address = await ViaCEPService.get_address_by_cep(clean_cep)
        if not address:
            # Return empty data when CEP not found
            return {
                "success": False,
                "error": "CEP não encontrado. Por favor, digite o endereço manualmente."
            }

        # Return address data as JSON
        return {
            "success": True,
            "endereco": address.get("endereco", ""),
            "bairro": address.get("bairro", ""),
            "cidade": address.get("cidade", ""),
            "estado": address.get("estado", "")
        }
    except Exception as e:
        # Log error for debugging
        print(f"Error fetching address for CEP {cep}: {str(e)}")
        return {
            "success": False,
            "error": "Erro interno ao buscar endereço. Tente novamente."
        }


@router.get("/stats")
async def get_registration_stats(
    db: AsyncSession = Depends(get_database)
):
    """Get registration statistics."""
    service = ClientRegistrationService()
    return await service.get_registration_stats(db)


# Form Template Endpoints
@router.get("/cnpj/form")
async def get_cnpj_form(
    request: Request,
    session_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get CNPJ registration form template."""
    service = ClientRegistrationService()
    session = await service.get_session(db, session_id)
    
    if not session or str(session.registration_type) != "CNPJ":
        raise HTTPException(status_code=404, detail="Invalid CNPJ registration session")
    
    # Get stored step 1 data if available for pre-filling
    prefill_data = {}
    if session.data and str(session.data) != "None":
        try:
            import json
            prefill_data = json.loads(str(session.data))
        except (json.JSONDecodeError, ValueError):
            prefill_data = {}
    
    # Return rendered CNPJ form template with pre-filled data
    return templates.TemplateResponse(
        "registration/cnpj.html",
        {
            "request": request,
            "session_id": session_id,
            "prefill_data": prefill_data,
            **company_context(request)
        }
    )


@router.get("/cnpj/step2/form")
async def get_cnpj_step2_form(
    request: Request,
    session_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get CNPJ step 2 (address) form template."""
    service = ClientRegistrationService()
    session = await service.get_session(db, session_id)
    
    if not session or str(session.registration_type) != "CNPJ":
        raise HTTPException(status_code=404, detail="Invalid CNPJ registration session")
    
    # Return rendered address form template
    return templates.TemplateResponse(
        "registration/cnpj-step2.html",
        {
            "request": {},
            "session_id": session_id,
            "recaptcha_site_key": settings.recaptcha_site_key,
            **company_context(request)
        }
    )


@router.get("/cpf/form")
async def get_cpf_form(
    request: Request,
    session_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get CPF registration form template."""
    service = ClientRegistrationService()
    session = await service.get_session(db, session_id)
    
    if not session or str(session.registration_type) != "CPF":
        raise HTTPException(status_code=404, detail="Invalid CPF registration session")
    
    # Get stored step 1 data if available for pre-filling
    prefill_data = {}
    if session.data and str(session.data) != "None":
        try:
            import json
            prefill_data = json.loads(str(session.data))
        except (json.JSONDecodeError, ValueError):
            prefill_data = {}
    
    # Return rendered CPF form template with pre-filled data
    return templates.TemplateResponse(
        "registration/cpf.html",
        {
            "request": request,
            "session_id": session_id,
            "prefill_data": prefill_data,
            **company_context(request)
        }
    )


# Step 1 Form with Session Data Endpoints
@router.get("/cnpj/step1/form")
async def get_cnpj_step1_form_with_data(
    request: Request,
    session_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get CNPJ step 1 form with pre-filled session data."""
    service = ClientRegistrationService()
    session = await service.get_session(db, session_id)
    
    if not session or str(session.registration_type) != "CNPJ":
        raise HTTPException(status_code=404, detail="Invalid CNPJ registration session")
    
    # Get stored step 1 data if available
    prefill_data = {}
    if session.data and str(session.data) != "None":
        try:
            import json
            prefill_data = json.loads(str(session.data))
        except (json.JSONDecodeError, ValueError):
            prefill_data = {}
    
    # Return rendered CNPJ form template with pre-filled data
    return templates.TemplateResponse(
        "registration/cnpj.html",
        {
            "request": request,
            "session_id": session_id,
            "prefill_data": prefill_data,
            **company_context(request)
        }
    )


@router.get("/cpf/step1/form")
async def get_cpf_step1_form_with_data(
    request: Request,
    session_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get CPF step 1 form with pre-filled session data."""
    service = ClientRegistrationService()
    session = await service.get_session(db, session_id)
    
    if not session or str(session.registration_type) != "CPF":
        raise HTTPException(status_code=404, detail="Invalid CPF registration session")
    
    # Get stored step 1 data if available
    prefill_data = {}
    if session.data and str(session.data) != "None":
        try:
            import json
            prefill_data = json.loads(str(session.data))
        except (json.JSONDecodeError, ValueError):
            prefill_data = {}
    
    # Return rendered CPF form template with pre-filled data
    return templates.TemplateResponse(
        "registration/cpf.html",
        {
            "request": request,
            "session_id": session_id,
            "prefill_data": prefill_data,
            **company_context(request)
        }
    )


@router.get("/cpf/step2/form")
async def get_cpf_step2_form(
    request: Request,
    session_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get CPF step 2 (address) form template."""
    service = ClientRegistrationService()
    session = await service.get_session(db, session_id)
    
    if not session or str(session.registration_type) != "CPF":
        raise HTTPException(status_code=404, detail="Invalid CPF registration session")
    
    # Return rendered address form template
    return templates.TemplateResponse(
        "registration/cpf-step2.html",
        {
            "request": {},
            "session_id": session_id,
            "recaptcha_site_key": settings.recaptcha_site_key,
            **company_context(request)
        }
    )


