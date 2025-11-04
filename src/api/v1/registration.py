"""Registration API endpoints for CNPJ/CPF registration system."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, Optional
import json
from starlette.templating import Jinja2Templates
from ...database import get_database
from ...schemas.client_registration import (
    RegistrationSessionCreate, RegistrationSessionOut,
    CNPJStep1, CNPJStep2, CNPJRegistrationOut,
    CPFStep1, CPFStep2, CPFRegistrationOut,
    DocumentValidationResponse, AddressResponse
)
from ...services.client_registration_service import (
    ClientRegistrationService, ViaCEPService, ReCAPTCHAService
)

router = APIRouter(prefix="/registration", tags=["registration"])
templates = Jinja2Templates(directory="templates")


@router.post("/session")
async def create_registration_session(
    request: Request,
    db: AsyncSession = Depends(get_database)
):
    """Create a new registration session and return the appropriate form."""
    form_data = await request.form()
    registration_type = form_data.get("registration_type", "CNPJ")
    
    service = ClientRegistrationService()
    session = await service.create_registration_session(db, registration_type)
    
    # Return HTML fragment based on registration type
    if registration_type == "CNPJ":
        form_html = get_cnpj_step1_form(session.session_id)
    else:  # CPF
        form_html = get_cpf_step1_form(session.session_id)
    
    return HTMLResponse(content=form_html)


@router.get("/session/{session_id}", response_model=RegistrationSessionOut)
async def get_registration_session(
    session_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get registration session details."""
    service = ClientRegistrationService()
    session = await service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Registration session not found")
    
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
        raise HTTPException(status_code=404, detail="Invalid registration session")
    
    try:
        # Validate CNPJ format
        clean_cnpj = step1_data.cnpj.replace('.', '').replace('/', '').replace('-', '')
        if not service.validate_document_uniqueness(db, clean_cnpj, "CNPJ").valid:
            return {"success": False, "error": "CNPJ já registrado"}
        
        # Store step 1 data
        await service.update_session_data(db, session_id, 1, step1_data.dict())
        
        return {
            "success": True, 
            "message": "Step 1 validation successful", 
            "next_step": 2,
            "data": step1_data.model_dump()
        }
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
    
    if not session or session.registration_type != "CNPJ":
        raise HTTPException(status_code=404, detail="Invalid registration session")
    
    # Verify reCAPTCHA
    if not ReCAPTCHAService.verify_recaptcha(step2_data.recaptcha_token):
        raise HTTPException(status_code=400, detail="reCAPTCHA verification failed")
    
    try:
        # Get stored step 1 data
        if session.data:
            step1_data = CNPJStep1(**json.loads(session.data))
            complete_data = {**step1_data.model_dump(), **step2_data.model_dump()}
            registration = await service.complete_cnpj_registration(db, CNPJRegistrationComplete(**complete_data))
            
            # Mark session as completed
            await service.update_session_data(db, session_id, 2, {"completed": True, "registration_id": registration.id})
            
            return {
                "success": True,
                "message": "Registration completed successfully", 
                "registration_id": registration.id,
                "redirect_url": "/auth/login"
            }
        else:
            raise HTTPException(status_code=400, detail="Step 1 data not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


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
    
    if not session or session.registration_type != "CPF":
        raise HTTPException(status_code=404, detail="Invalid registration session")
    
    try:
        # Validate CPF format
        clean_cpf = step1_data.cpf.replace('.', '').replace('-', '')
        if not service.validate_document_uniqueness(db, clean_cpf, "CPF").valid:
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
    
    if not session or session.registration_type != "CPF":
        raise HTTPException(status_code=404, detail="Invalid registration session")
    
    # Verify reCAPTCHA
    if not ReCAPTCHAService.verify_recaptcha(step2_data.recaptcha_token):
        raise HTTPException(status_code=400, detail="reCAPTCHA verification failed")
    
    try:
        # Get stored step 1 data
        if session.data:
            step1_data = CPFStep1(**json.loads(session.data))
            complete_data = {**step1_data.model_dump(), **step2_data.model_dump()}
            registration = await service.complete_cpf_registration(db, CPFRegistrationComplete(**complete_data))
            
            # Mark session as completed
            await service.update_session_data(db, session_id, 2, {"completed": True, "registration_id": registration.id})
            
            return {
                "success": True,
                "message": "Registration completed successfully", 
                "registration_id": registration.id,
                "redirect_url": "/auth/login"
            }
        else:
            raise HTTPException(status_code=400, detail="Step 1 data not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


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
            "endereco": address.endereco or "",
            "bairro": address.bairro or "",
            "cidade": address.cidade or "",
            "estado": address.estado or ""
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


# HTMX Fragment Endpoints for Dynamic Form Updates
@router.post("/htmx/cnpj-step1")
async def htmx_cnpj_step1(
    request: Request,
    db: AsyncSession = Depends(get_database)
):
    """HTMX endpoint for CNPJ step 1 validation."""
    form_data = await request.form()
    session_id = form_data.get("session_id")
    
    if not session_id:
        return HTTPException(status_code=400, detail="Session ID required")
    
    try:
        step1_data = CNPJStep1(
            qual_seu_negocio=form_data.get("qual_seu_negocio"),
            cnpj=form_data.get("cnpj"),
            razao_social=form_data.get("razao_social"),
            seu_nome=form_data.get("seu_nome"),
            sua_funcao=form_data.get("sua_funcao"),
            email=form_data.get("email"),
            celular=form_data.get("celular"),
            terms_accepted=form_data.get("terms_accepted") == "on",
            marketing_opt_in=form_data.get("marketing_opt_in") == "on"
        )
        
        service = ClientRegistrationService()
        session = await service.get_session(db, session_id)
        
        if not session or session.registration_type != "CNPJ":
            return {"success": False, "error": "Invalid session"}
        
        # Validate CNPJ uniqueness
        validation_response = await service.validate_document_uniqueness(
            db, step1_data.cnpj.replace('.', '').replace('/', '').replace('-', ''), "CNPJ"
        )
        
        if not validation_response.valid:
            return {
                "success": False, 
                "error": validation_response.message,
                "field_errors": {"cnpj": validation_response.message}
            }
        
        # Store step 1 data
        await service.update_session_data(db, session_id, 1, step1_data.model_dump())
        
        # Get address form HTML
        address_form_html = get_address_form_html("cnpj")

        # Return HTML fragment for step 2
        html_parts = [
            '<div class="bg-white shadow-sm rounded-lg p-6">',
            '<div class="mb-6">',
                '<div class="flex items-center mb-4">',
                    '<div class="flex-shrink-0">',
                        '<div class="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">',
                            '<i class="fas fa-building text-blue-600"></i>',
                        '</div>',
                    '</div>',
                    '<div class="ml-4">',
                        '<h3 class="text-lg font-medium text-gray-900">Cadastro Empresa (CNPJ)</h3>',
                        '<p class="text-sm text-gray-500">Etapa 2 de 2: Informações de Endereço</p>',
                    '</div>',
                '</div>',
            '</div>',
            '<div id="step2-form" class="mt-6">',
            '<p class="text-sm text-gray-600 mb-4">Por favor, forneça as informações de endereço da sua empresa.</p>',
            f'<div id="address-form" class="space-y-4">{address_form_html}</div>',
            '<div class="mt-6 flex justify-between">',
            f'<button type="button" hx-post="/registration/htmx/cnpj-back-step1" hx-vals=\'{{"session_id": "{session_id}"}}\' hx-target="#registration-form" hx-swap="innerHTML" class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">Voltar</button>',
            f'<button type="button" onclick="submitCNPJStep2(\'{session_id}\')" class="inline-flex items-center px-6 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700">Finalizar Cadastro</button>',
            '</div>',
            '</div>',
            '</div>'
        ]

        return HTMLResponse(content=''.join(html_parts))
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/htmx/cpf-step1")
async def htmx_cpf_step1(
    request: Request,
    db: AsyncSession = Depends(get_database)
):
    """HTMX endpoint for CPF step 1 validation."""
    form_data = await request.form()
    session_id = form_data.get("session_id")
    
    if not session_id:
        return HTTPException(status_code=400, detail="Session ID required")
    
    try:
        step1_data = CPFStep1(
            perfil_compra=form_data.get("perfil_compra"),
            qual_negocio_cpf=form_data.get("qual_negocio_cpf"),
            cpf=form_data.get("cpf"),
            nome_completo=form_data.get("nome_completo"),
            email=form_data.get("email"),
            genero=form_data.get("genero"),
            celular=form_data.get("celular"),
            terms_accepted=form_data.get("terms_accepted") == "on",
            marketing_opt_in=form_data.get("marketing_opt_in") == "on"
        )
        
        service = ClientRegistrationService()
        session = await service.get_session(db, session_id)
        
        if not session or session.registration_type != "CPF":
            return {"success": False, "error": "Invalid session"}
        
        # Validate CPF uniqueness
        validation_response = await service.validate_document_uniqueness(
            db, step1_data.cpf.replace('.', '').replace('-', ''), "CPF"
        )
        
        if not validation_response.valid:
            return {
                "success": False, 
                "error": validation_response.message,
                "field_errors": {"cpf": validation_response.message}
            }
        
        # Store step 1 data
        await service.update_session_data(db, session_id, 1, step1_data.model_dump())
        
        # Get address form HTML
        address_form_html = get_address_form_html("cpf")

        # Return HTML fragment for step 2
        html_parts = [
            '<div class="bg-white shadow-sm rounded-lg p-6">',
            '<div class="mb-6">',
                '<div class="flex items-center mb-4">',
                    '<div class="flex-shrink-0">',
                        '<div class="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">',
                            '<i class="fas fa-user text-green-600"></i>',
                        '</div>',
                    '</div>',
                    '<div class="ml-4">',
                        '<h3 class="text-lg font-medium text-gray-900">Cadastro Pessoal (CPF)</h3>',
                        '<p class="text-sm text-gray-500">Etapa 2 de 2: Informações Complementares e Endereço</p>',
                    '</div>',
                '</div>',
            '</div>',
            '<div id="step2-form" class="mt-6">',
            f'<div id="address-form" class="space-y-4">{address_form_html}</div>',
            '<div class="mt-6 flex justify-between">',
            f'<button type="button" hx-post="/registration/htmx/cpf-back-step1" hx-vals=\'{{"session_id": "{session_id}"}}\' hx-target="#registration-form" hx-swap="innerHTML" class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">Voltar</button>',
            f'<button type="button" onclick="submitStep2(\'{session_id}\')" class="form-button-primary">Finalizar Cadastro</button>',
            '</div>',
            '</div>',
            '</div>'
        ]

        return HTMLResponse(content=''.join(html_parts))
    except Exception as e:
        return {"success": False, "error": str(e)}


# HTMX Back Step 1 Endpoints
@router.post("/htmx/cnpj-back-step1")
async def htmx_cnpj_back_step1(
    request: Request,
    db: AsyncSession = Depends(get_database)
):
    """HTMX endpoint to go back to CNPJ step 1 with preserved data."""
    form_data = await request.form()
    session_id = form_data.get("session_id")
    
    if not session_id:
        return HTTPException(status_code=400, detail="Session ID required")
    
    try:
        service = ClientRegistrationService()
        session = await service.get_session(db, session_id)
        
        if not session or session.registration_type != "CNPJ":
            return {"success": False, "error": "Invalid session"}
        
        # Get stored step 1 data
        if session.data:
            try:
                step1_data = json.loads(session.data)
                # Clean up data to handle encoding issues
                clean_data = {}
                for key, value in step1_data.items():
                    if isinstance(value, str):
                        clean_data[key] = value.encode('utf-8').decode('utf-8', errors='ignore')
                    else:
                        clean_data[key] = value
                
                form_html = get_cnpj_step1_form_with_data(session_id, clean_data)
                return {
                    "success": True,
                    "html": form_html
                }
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                # If JSON parsing fails, return fresh form
                form_html = get_cnpj_step1_form(session_id)
                return {
                    "success": True,
                    "html": form_html
                }
        else:
            # If no data, return fresh form
            form_html = get_cnpj_step1_form(session_id)
            return {
                "success": True,
                "html": form_html
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/htmx/cpf-back-step1")
async def htmx_cpf_back_step1(
    request: Request,
    db: AsyncSession = Depends(get_database)
):
    """HTMX endpoint to go back to CPF step 1 with preserved data."""
    form_data = await request.form()
    session_id = form_data.get("session_id")
    
    if not session_id:
        return HTTPException(status_code=400, detail="Session ID required")
    
    try:
        service = ClientRegistrationService()
        session = await service.get_session(db, session_id)
        
        if not session or session.registration_type != "CPF":
            return {"success": False, "error": "Invalid session"}
        
        # Get stored step 1 data
        if session.data:
            try:
                step1_data = json.loads(session.data)
                # Clean up data to handle encoding issues
                clean_data = {}
                for key, value in step1_data.items():
                    if isinstance(value, str):
                        clean_data[key] = value.encode('utf-8').decode('utf-8', errors='ignore')
                    else:
                        clean_data[key] = value
                
                form_html = get_cpf_step1_form_with_data(session_id, clean_data)
                return HTMLResponse(content=form_html)
                # return {
                #     "success": True,
                #     "html": form_html
                # }
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                # If JSON parsing fails, return fresh form
                form_html = get_cpf_step1_form(session_id)
                return HTMLResponse(content=form_html)
                # return {
                #     "success": True,
                #     "html": form_html
                # }
        else:
            # If no data, return fresh form
            form_html = get_cpf_step1_form(session_id)
            return HTMLResponse(content=form_html)
            # return {
            #     "success": True,
            #     "html": form_html
            # }
    except Exception as e:
        return {"success": False, "error": str(e)}


# Helper function to generate address form HTML
def get_address_form_html(registration_type: str) -> str:
    """Generate address form HTML fragment."""
    html_parts = [
        '<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">',
        '<div class="sm:col-span-2"><label for="cep" class="form-label">CEP *</label><input type="text" id="cep" name="cep" required placeholder="00000-000" class="form-input"></div>',
        '<div id="address-fields" class="sm:col-span-2 space-y-4">',
        '<div><label for="endereco" class="form-label">Endereço *</label><input type="text" id="endereco" name="endereco" required class="form-input"></div>',
        '<div><label for="bairro" class="form-label">Bairro *</label><input type="text" id="bairro" name="bairro" required class="form-input"></div>',
        '<div><label for="cidade" class="form-label">Cidade *</label><input type="text" id="cidade" name="cidade" required class="form-input"></div>',
        '<div><label for="estado" class="form-label">Estado *</label><select id="estado" name="estado" required class="form-select"><option value="">Selecione o estado</option><option value="AC">Acre</option><option value="AL">Alagoas</option><option value="AP">Amapá</option><option value="AM">Amazonas</option><option value="BA">Bahia</option><option value="CE">Ceará</option><option value="DF">Distrito Federal</option><option value="ES">Espírito Santo</option><option value="GO">Goiás</option><option value="MA">Maranhão</option><option value="MT">Mato Grosso</option><option value="MS">Mato Grosso do Sul</option><option value="MG">Minas Gerais</option><option value="PA">Pará</option><option value="PB">Paraíba</option><option value="PR">Paraná</option><option value="PE">Pernambuco</option><option value="PI">Piauí</option><option value="RJ">Rio de Janeiro</option><option value="RN">Rio Grande do Norte</option><option value="RS">Rio Grande do Sul</option><option value="RO">Rondônia</option><option value="RR">Roraima</option><option value="SC">Santa Catarina</option><option value="SP">São Paulo</option><option value="SE">Sergipe</option><option value="TO">Tocantins</option></select></div>',
        '</div>',
        '<div class="sm:col-span-2"><label for="recaptcha_token" class="form-label">reCAPTCHA *</label><div id="recaptcha-{}" class="mt-1"><input type="hidden" id="recaptcha_token" name="recaptcha_token" value="test_token"><div class="text-sm text-gray-500">Verificação reCAPTCHA necessária</div></div></div>'.format(registration_type),
        '</div>'
    ]
    
    if registration_type == "cpf":
        html_parts.insert(-1, '<div class="sm:col-span-2"><label for="data_nascimento" class="form-label">Data de Nascimento *</label><input type="date" id="data_nascimento" name="data_nascimento" required class="form-input"></div>')
    
    return ''.join(html_parts)


def get_cnpj_step1_form(session_id: str) -> str:
    """Generate CNPJ step 1 form HTML."""
    return f"""
<div class="bg-white shadow-sm rounded-lg p-6">
    <div class="mb-6">
        <div class="flex items-center mb-4">
            <div class="flex-shrink-0">
                <div class="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                    <i class="fas fa-building text-blue-600"></i>
                </div>
            </div>
            <div class="ml-4">
                <h3 class="text-lg font-medium text-gray-900">Cadastro Empresa (CNPJ)</h3>
                <p class="text-sm text-gray-500">Etapa 1 de 2: Dados da empresa e contato</p>
            </div>
        </div>
    </div>
    
    <form hx-post="/registration/htmx/cnpj-step1"
          hx-vals='{{"session_id": "{session_id}"}}'
          hx-target="#registration-form"
          hx-swap="innerHTML"
          hx-indicator=".cnpj-loading">
        
        <div class="form-space-y">
            <div>
                <label for="qual_seu_negocio" class="form-label">Qual o seu negócio? *</label>
                <select id="qual_seu_negocio" name="qual_seu_negocio" required
                        class="form-select">
                    <option value="">Selecione...</option>
                    <option value="Academia">Academia</option>
                    <option value="Adega">Adega</option>
                    <option value="Bar">Bar</option>
                    <option value="Bomboniere">Bomboniere</option>
                    <option value="Cantina">Cantina</option>
                    <option value="Clube esportivo">Clube esportivo</option>
                    <option value="Condomínio">Condomínio</option>
                    <option value="Confeitaria">Confeitaria</option>
                    <option value="Doceria">Doceria</option>
                    <option value="Dogueiro">Dogueiro</option>
                    <option value="Escola">Escola</option>
                    <option value="Food service">Food service</option>
                    <option value="Hotel">Hotel</option>
                    <option value="Instituição religiosa">Instituição religiosa</option>
                    <option value="Lanchonete">Lanchonete</option>
                    <option value="Mercearia">Mercearia</option>
                    <option value="Mini mercado">Mini mercado</option>
                    <option value="Padaria">Padaria</option>
                    <option value="Pastelaria">Pastelaria</option>
                    <option value="Pizzaria">Pizzaria</option>
                    <option value="Restaurante">Restaurante</option>
                    <option value="Outros">Outros</option>
                </select>
            </div>
            
            <div>
                <label for="cnpj" class="form-label">CNPJ *</label>
                <input type="text" id="cnpj" name="cnpj" required
                       class="form-input"
                       placeholder="00.000.000/0000-00"
                       oninput="formatCNPJ(this)"
                       maxlength="18">
            </div>
            
            <div>
                <label for="razao_social" class="form-label">Razão Social *</label>
                <input type="text" id="razao_social" name="razao_social" required
                       class="form-input">
            </div>
            
            <div>
                <label for="seu_nome" class="form-label">Seu nome *</label>
                <input type="text" id="seu_nome" name="seu_nome" required
                       class="form-input">
            </div>
            
            <div>
                <label for="sua_funcao" class="form-label">Sua função na empresa *</label>
                <select id="sua_funcao" name="sua_funcao" required
                        class="form-select">
                    <option value="">Selecione...</option>
                    <option value="Proprietário">Proprietário</option>
                    <option value="Gerente">Gerente</option>
                    <option value="Estoquista">Estoquista</option>
                    <option value="Administrador">Administrador</option>
                    <option value="Vendedor">Vendedor</option>
                    <option value="Outros">Outros</option>
                </select>
            </div>
            
            <div>
                <label for="email" class="form-label">E-mail *</label>
                <input type="email" id="email" name="email" required
                       class="form-input">
            </div>
            
            <div>
                <label for="celular" class="form-label">Celular *</label>
                <input type="text" id="celular" name="celular" required
                       class="form-input"
                       placeholder="(11) 99999-9999"
                       oninput="formatPhone(this)"
                       maxlength="15">
            </div>
            
            <div class="space-y-4">
                <div class="form-checkbox-container">
                    <input id="terms_accepted" name="terms_accepted" type="checkbox" required
                           class="form-checkbox">
                    <label for="terms_accepted" class="form-checkbox-label">
                        Concordar com os termos da Política de Privacidade *
                    </label>
                </div>
                
                <div class="form-checkbox-container">
                    <input id="marketing_opt_in" name="marketing_opt_in" type="checkbox"
                           class="form-checkbox">
                    <label for="marketing_opt_in" class="form-checkbox-label">
                        Receber e-mails com promoções e novidades do sistema e parceiros
                    </label>
                </div>
            </div>
        </div>
        
        <div class="mt-8 flex justify-between">
            <a href="/"
               class="form-button-secondary">
                Voltar
            </a>
            <button type="submit"
                    class="form-button-primary cnpj-loading">
                Avançar
            </button>
        </div>
    </form>
</div>
"""


def get_cpf_step1_form(session_id: str) -> str:
    """Generate CPF step 1 form HTML."""
    return f"""
<div class="bg-white shadow-sm rounded-lg p-6">
    <div class="mb-6">
        <div class="flex items-center mb-4">
            <div class="flex-shrink-0">
                <div class="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                    <i class="fas fa-user text-green-600"></i>
                </div>
            </div>
            <div class="ml-4">
                <h3 class="text-lg font-medium text-gray-900">Cadastro Pessoal (CPF)</h3>
                <p class="text-sm text-gray-500">Etapa 1 de 2: Dados pessoais e perfil</p>
            </div>
        </div>
    </div>
    
    <form hx-post="/registration/htmx/cpf-step1"
          hx-vals='{{"session_id": "{session_id}"}}'
          hx-target="#registration-form"
          hx-swap="innerHTML"
          hx-indicator=".cpf-loading">
        
        <div class="form-space-y">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-3">Você compra para: *</label>
                <div class="space-y-2">
                    <div class="flex items-center">
                        <input id="perfil_compra_casa" name="perfil_compra" type="radio" value="casa" required
                               class="form-checkbox">
                        <label for="perfil_compra_casa" class="ml-2 block text-sm text-gray-900">
                            Sua casa
                        </label>
                    </div>
                    <div class="flex items-center">
                        <input id="perfil_compra_negocio" name="perfil_compra" type="radio" value="negocio" required
                               class="form-checkbox">
                        <label for="perfil_compra_negocio" class="ml-2 block text-sm text-gray-900">
                            Seu negócio
                        </label>
                    </div>
                    <div class="flex items-center">
                        <input id="perfil_compra_ambos" name="perfil_compra" type="radio" value="ambos" required
                               class="form-checkbox">
                        <label for="perfil_compra_ambos" class="ml-2 block text-sm text-gray-900">
                            Para ambos
                        </label>
                    </div>
                </div>
            </div>
            
            <div id="business-field" class="hidden">
                <label for="qual_negocio_cpf" class="form-label">Qual o seu negócio?</label>
                <input type="text" id="qual_negocio_cpf" name="qual_negocio_cpf"
                       class="form-input">
            </div>
            
            <div>
                <label for="cpf" class="form-label">CPF *</label>
                <input type="text" id="cpf" name="cpf" required
                       class="form-input"
                       placeholder="000.000.000-00"
                       oninput="formatCPF(this)"
                       maxlength="14">
            </div>
            
            <div>
                <label for="nome_completo" class="form-label">Nome completo *</label>
                <input type="text" id="nome_completo" name="nome_completo" required
                       class="form-input">
            </div>
            
            <div>
                <label for="email" class="form-label">E-mail *</label>
                <input type="email" id="email" name="email" required
                       class="form-input">
            </div>
            
            <div>
                <label for="genero" class="form-label">Gênero *</label>
                <select id="genero" name="genero" required
                        class="form-select">
                    <option value="">Selecione...</option>
                    <option value="Feminino">Feminino</option>
                    <option value="masculino">Masculino</option>
                    <option value="outros">Outros</option>
                    <option value="nao_quero_me_identificar">Não quero me identificar</option>
                </select>
            </div>
            
            <div>
                <label for="celular" class="form-label">Celular *</label>
                <input type="text" id="celular" name="celular" required
                       class="form-input"
                       placeholder="(11) 99999-9999"
                       oninput="formatPhone(this)"
                       maxlength="15">
            </div>
            
            <div class="space-y-4">
                <div class="form-checkbox-container">
                    <input id="terms_accepted" name="terms_accepted" type="checkbox" required
                           class="form-checkbox">
                    <label for="terms_accepted" class="form-checkbox-label">
                        Concordar com os termos da Política de Privacidade *
                    </label>
                </div>
                
                <div class="form-checkbox-container">
                    <input id="marketing_opt_in" name="marketing_opt_in" type="checkbox"
                           class="form-checkbox">
                    <label for="marketing_opt_in" class="form-checkbox-label">
                        Receber e-mails com promoções e novidades do sistema e parceiros
                    </label>
                </div>
            </div>
        </div>
        
        <div class="mt-8 flex justify-between">
            <a href="/"
               class="form-button-secondary">
                Voltar
            </a>
            <button type="submit"
                    class="form-button-primary cpf-loading">
                Avançar
            </button>
        </div>
    </form>
</div>

<script>
// Show/hide business field based on selection
document.addEventListener('DOMContentLoaded', function() {{
    const businessRadio = document.getElementById('perfil_compra_negocio');
    const businessField = document.getElementById('business-field');
    const businessNameInput = document.getElementById('qual_negocio_cpf');
    
    function toggleBusinessField() {{
        if (businessRadio && businessRadio.checked) {{
            businessField.classList.remove('hidden');
            businessNameInput.setAttribute('required', 'required');
        }} else {{
            businessField.classList.add('hidden');
            businessNameInput.removeAttribute('required');
        }}
    }}
    
    // Event listeners for radio buttons
    document.querySelectorAll('input[name="perfil_compra"]').forEach(radio => {{
        radio.addEventListener('change', toggleBusinessField);
    }});
    
    // Check initial state
    toggleBusinessField();
}});
</script>
"""


def get_cnpj_step1_form_with_data(session_id: str, data: Dict[str, Any]) -> str:
    """Generate CNPJ step 1 form HTML with pre-filled data."""
    
    # Extract data with defaults
    qual_seu_negocio = data.get('qual_seu_negocio', '')
    cnpj = data.get('cnpj', '')
    razao_social = data.get('razao_social', '')
    seu_nome = data.get('seu_nome', '')
    sua_funcao = data.get('sua_funcao', '')
    email = data.get('email', '')
    celular = data.get('celular', '')
    terms_accepted = data.get('terms_accepted', False)
    marketing_opt_in = data.get('marketing_opt_in', False)
    
    # Helper functions
    def option_selected(option_value, selected_value):
        return 'selected' if option_value == selected_value else ''
    
    def checkbox_checked(is_checked):
        return 'checked' if is_checked else ''
    
    def safe_value(key, default=''):
        value = data.get(key, default)
        if isinstance(value, str):
            # Handle Unicode encoding issues properly
            try:
                return value.encode('latin1').decode('utf-8')
            except (UnicodeDecodeError, UnicodeEncodeError):
                return value
        return value
    
    # Extract data with proper encoding handling
    qual_seu_negocio = safe_value('qual_seu_negocio', '')
    cnpj = safe_value('cnpj', '')
    razao_social = safe_value('razao_social', '')
    seu_nome = safe_value('seu_nome', '')
    sua_funcao = safe_value('sua_funcao', '')
    email = safe_value('email', '')
    celular = safe_value('celular', '')
    terms_accepted = data.get('terms_accepted', False)
    marketing_opt_in = data.get('marketing_opt_in', False)
    
    return f"""
<div class="bg-white shadow-sm rounded-lg p-6">
    <div class="mb-6">
        <div class="flex items-center mb-4">
            <div class="flex-shrink-0">
                <div class="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                    <i class="fas fa-building text-blue-600"></i>
                </div>
            </div>
            <div class="ml-4">
                <h3 class="text-lg font-medium text-gray-900">Cadastro Empresa (CNPJ)</h3>
                <p class="text-sm text-gray-500">Etapa 1 de 2: Dados da empresa e contato</p>
            </div>
        </div>
    </div>
    
    <form hx-post="/registration/htmx/cnpj-step1" 
          hx-vals='{{"session_id": "{session_id}"}}'
          hx-target="#registration-form"
          hx-swap="innerHTML"
          hx-indicator=".cnpj-loading">
        
        <div class="form-space-y">
            <div>
                <label for="qual_seu_negocio" class="form-label">Qual o seu negócio? *</label>
                <select id="qual_seu_negocio" name="qual_seu_negocio" required
                        class="form-select">
                    <option value="">Selecione...</option>
                    <option value="Academia" {option_selected("Academia", qual_seu_negocio)}>Academia</option>
                    <option value="Adega" {option_selected("Adega", qual_seu_negocio)}>Adega</option>
                    <option value="Bar" {option_selected("Bar", qual_seu_negocio)}>Bar</option>
                    <option value="Bomboniere" {option_selected("Bomboniere", qual_seu_negocio)}>Bomboniere</option>
                    <option value="Cantina" {option_selected("Cantina", qual_seu_negocio)}>Cantina</option>
                    <option value="Clube esportivo" {option_selected("Clube esportivo", qual_seu_negocio)}>Clube esportivo</option>
                    <option value="Condomínio" {option_selected("Condomínio", qual_seu_negocio)}>Condomínio</option>
                    <option value="Confeitaria" {option_selected("Confeitaria", qual_seu_negocio)}>Confeitaria</option>
                    <option value="Doceria" {option_selected("Doceria", qual_seu_negocio)}>Doceria</option>
                    <option value="Dogueiro" {option_selected("Dogueiro", qual_seu_negocio)}>Dogueiro</option>
                    <option value="Escola" {option_selected("Escola", qual_seu_negocio)}>Escola</option>
                    <option value="Food service" {option_selected("Food service", qual_seu_negocio)}>Food service</option>
                    <option value="Hotel" {option_selected("Hotel", qual_seu_negocio)}>Hotel</option>
                    <option value="Instituição religiosa" {option_selected("Instituição religiosa", qual_seu_negocio)}>Instituição religiosa</option>
                    <option value="Lanchonete" {option_selected("Lanchonete", qual_seu_negocio)}>Lanchonete</option>
                    <option value="Mercearia" {option_selected("Mercearia", qual_seu_negocio)}>Mercearia</option>
                    <option value="Mini mercado" {option_selected("Mini mercado", qual_seu_negocio)}>Mini mercado</option>
                    <option value="Padaria" {option_selected("Padaria", qual_seu_negocio)}>Padaria</option>
                    <option value="Pastelaria" {option_selected("Pastelaria", qual_seu_negocio)}>Pastelaria</option>
                    <option value="Pizzaria" {option_selected("Pizzaria", qual_seu_negocio)}>Pizzaria</option>
                    <option value="Restaurante" {option_selected("Restaurante", qual_seu_negocio)}>Restaurante</option>
                    <option value="Outros" {option_selected("Outros", qual_seu_negocio)}>Outros</option>
                </select>
            </div>
            
            <div>
                <label for="cnpj" class="form-label">CNPJ *</label>
                <input type="text" id="cnpj" name="cnpj" required
                       value="{cnpj}"
                       class="form-input"
                       placeholder="00.000.000/0000-00"
                       oninput="formatCNPJ(this)"
                       maxlength="18">
            </div>
            
            <div>
                <label for="razao_social" class="form-label">Razão Social *</label>
                <input type="text" id="razao_social" name="razao_social" required
                       value="{razao_social}"
                       class="form-input">
            </div>
            
            <div>
                <label for="seu_nome" class="form-label">Seu nome *</label>
                <input type="text" id="seu_nome" name="seu_nome" required
                       value="{seu_nome}"
                       class="form-input">
            </div>
            
            <div>
                <label for="sua_funcao" class="form-label">Sua função na empresa *</label>
                <select id="sua_funcao" name="sua_funcao" required
                        class="form-select">
                    <option value="">Selecione...</option>
                    <option value="Proprietário" {option_selected("Proprietário", sua_funcao)}>Proprietário</option>
                    <option value="Gerente" {option_selected("Gerente", sua_funcao)}>Gerente</option>
                    <option value="Estoquista" {option_selected("Estoquista", sua_funcao)}>Estoquista</option>
                    <option value="Administrador" {option_selected("Administrador", sua_funcao)}>Administrador</option>
                    <option value="Vendedor" {option_selected("Vendedor", sua_funcao)}>Vendedor</option>
                    <option value="Outros" {option_selected("Outros", sua_funcao)}>Outros</option>
                </select>
            </div>
            
            <div>
                <label for="email" class="form-label">E-mail *</label>
                <input type="email" id="email" name="email" required
                       value="{email}"
                       class="form-input">
            </div>
            
            <div>
                <label for="celular" class="form-label">Celular *</label>
                <input type="text" id="celular" name="celular" required
                       value="{celular}"
                       class="form-input"
                       placeholder="(11) 99999-9999"
                       oninput="formatPhone(this)"
                       maxlength="15">
            </div>
            
            <div class="space-y-4">
                <div class="form-checkbox-container">
                    <input id="terms_accepted" name="terms_accepted" type="checkbox" required
                           {checkbox_checked(terms_accepted)}
                           class="form-checkbox">
                    <label for="terms_accepted" class="form-checkbox-label">
                        Concordar com os termos da Política de Privacidade *
                    </label>
                </div>
                
                <div class="form-checkbox-container">
                    <input id="marketing_opt_in" name="marketing_opt_in" type="checkbox"
                           {checkbox_checked(marketing_opt_in)}
                           class="form-checkbox">
                    <label for="marketing_opt_in" class="form-checkbox-label">
                        Receber e-mails com promoções e novidades do sistema e parceiros
                    </label>
                </div>
            </div>
        </div>
        
        <div class="mt-8 flex justify-between">
            <a href="/"
               class="form-button-secondary">
                Voltar
            </a>
            <button type="submit"
                    class="form-button-primary cnpj-loading">
                Avançar
            </button>
        </div>
    </form>
</div>
"""


def get_cpf_step1_form_with_data(session_id: str, data: Dict[str, Any]) -> str:
    """Generate CPF step 1 form HTML with pre-filled data."""
    
    # Helper functions
    def radio_checked(radio_value, selected_value):
        return 'checked' if radio_value == selected_value else ''
    
    def option_selected(option_value, selected_value):
        return 'selected' if option_value == selected_value else ''
    
    def checkbox_checked(is_checked):
        return 'checked' if is_checked else ''
    
    # Extract data with defaults and encoding handling
    def safe_value(key, default=''):
        value = data.get(key, default)
        if isinstance(value, str):
            # Handle Unicode encoding issues properly
            try:
                return value.encode('latin1').decode('utf-8')
            except (UnicodeDecodeError, UnicodeEncodeError):
                return value
        return value
    
    return f"""
<div class="bg-white shadow-sm rounded-lg p-6">
    <div class="mb-6">
        <div class="flex items-center mb-4">
            <div class="flex-shrink-0">
                <div class="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                    <i class="fas fa-user text-green-600"></i>
                </div>
            </div>
            <div class="ml-4">
                <h3 class="text-lg font-medium text-gray-900">Cadastro Pessoal (CPF)</h3>
                <p class="text-sm text-gray-500">Etapa 1 de 2: Dados pessoais e perfil</p>
            </div>
        </div>
    </div>
    
    <form hx-post="/registration/htmx/cpf-step1"
          hx-vals='{{"session_id": "{session_id}"}}'
          hx-target="#registration-form"
          hx-swap="innerHTML"
          hx-indicator=".cpf-loading">
        
        <div class="form-space-y">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-3">Você compra para: *</label>
                <div class="space-y-2">
                    <div class="flex items-center">
                        <input id="perfil_compra_casa" name="perfil_compra" type="radio" value="casa" required
                               {radio_checked('casa', data.get('perfil_compra', ''))}
                               class="form-checkbox">
                        <label for="perfil_compra_casa" class="ml-2 block text-sm text-gray-900">
                            Sua casa
                        </label>
                    </div>
                    <div class="flex items-center">
                        <input id="perfil_compra_negocio" name="perfil_compra" type="radio" value="negocio" required
                               {radio_checked('negocio', data.get('perfil_compra', ''))}
                               class="form-checkbox">
                        <label for="perfil_compra_negocio" class="ml-2 block text-sm text-gray-900">
                            Seu negócio
                        </label>
                    </div>
                    <div class="flex items-center">
                        <input id="perfil_compra_ambos" name="perfil_compra" type="radio" value="ambos" required
                               {radio_checked('ambos', data.get('perfil_compra', ''))}
                               class="form-checkbox">
                        <label for="perfil_compra_ambos" class="ml-2 block text-sm text-gray-900">
                            Para ambos
                        </label>
                    </div>
                </div>
            </div>
            
            <div id="business-field" class="{"hidden" if data.get('perfil_compra') not in ['negocio', 'ambos'] else ""}">
                <label for="qual_negocio_cpf" class="form-label">Qual o seu negócio?</label>
                <input type="text" id="qual_negocio_cpf" name="qual_negocio_cpf"
                       {"required" if data.get('perfil_compra') in ['negocio', 'ambos'] else ""}
                       value="{data.get('qual_negocio_cpf', '')}"
                       class="form-input">
            </div>
            
            <div>
                <label for="cpf" class="form-label">CPF *</label>
                <input type="text" id="cpf" name="cpf" required
                       value="{safe_value('cpf', '')}"
                       class="form-input"
                       placeholder="000.000.000-00"
                       oninput="formatCPF(this)"
                       maxlength="14">
            </div>
            
            <div>
                <label for="nome_completo" class="form-label">Nome completo *</label>
                <input type="text" id="nome_completo" name="nome_completo" required
                       value="{safe_value('nome_completo', '')}"
                       class="form-input">
            </div>
            
            <div>
                <label for="email" class="form-label">E-mail *</label>
                <input type="email" id="email" name="email" required
                       value="{safe_value('email', '')}"
                       class="form-input">
            </div>
            
            <div>
                <label for="genero" class="form-label">Gênero *</label>
                <select id="genero" name="genero" required
                        class="form-select">
                    <option value="">Selecione...</option>
                    <option value="Feminino" {option_selected('Feminino', safe_value('genero', ''))}>Feminino</option>
                    <option value="masculino" {option_selected('masculino', safe_value('genero', ''))}>Masculino</option>
                    <option value="outros" {option_selected('outros', safe_value('genero', ''))}>Outros</option>
                    <option value="não quero me identificar" {option_selected('não quero me identificar', safe_value('genero', ''))}>Não quero me identificar</option>
                </select>
            </div>
            
            <div>
                <label for="celular" class="form-label">Celular *</label>
                <input type="text" id="celular" name="celular" required
                       value="{safe_value('celular', '')}"
                       class="form-input"
                       placeholder="(11) 99999-9999"
                       oninput="formatPhone(this)"
                       maxlength="15">
            </div>
            
            <div class="space-y-4">
                <div class="form-checkbox-container">
                    <input id="terms_accepted" name="terms_accepted" type="checkbox" required
                           {checkbox_checked(data.get('terms_accepted', False))}
                           class="form-checkbox">
                    <label for="terms_accepted" class="form-checkbox-label">
                        Concordar com os termos da Política de Privacidade *
                    </label>
                </div>
                
                <div class="form-checkbox-container">
                    <input id="marketing_opt_in" name="marketing_opt_in" type="checkbox"
                           {checkbox_checked(data.get('marketing_opt_in', False))}
                           class="form-checkbox">
                    <label for="marketing_opt_in" class="form-checkbox-label">
                        Receber e-mails com promoções e novidades do sistema e parceiros
                    </label>
                </div>
            </div>
        </div>
        
        <div class="mt-8 flex justify-between">
            <a href="/"
               class="form-button-secondary">
                Voltar
            </a>
            <button type="submit"
                    class="form-button-primary cpf-loading">
                Avançar
            </button>
        </div>
    </form>
</div>

<script>
// Show/hide business field based on selection
document.addEventListener('DOMContentLoaded', function() {{
    const businessRadio = document.getElementById('perfil_compra_negocio');
    const businessField = document.getElementById('business-field');
    const businessNameInput = document.getElementById('qual_negocio_cpf');
    
    function toggleBusinessField() {{
        if (businessRadio && businessRadio.checked) {{
            businessField.classList.remove('hidden');
            businessNameInput.setAttribute('required', 'required');
        }} else {{
            businessField.classList.add('hidden');
            businessNameInput.removeAttribute('required');
        }}
    }}
    
    // Event listeners for radio buttons
    document.querySelectorAll('input[name="perfil_compra"]').forEach(radio => {{
        radio.addEventListener('change', toggleBusinessField);
    }});
    
    // Check initial state
    toggleBusinessField();
}});
</script>
"""