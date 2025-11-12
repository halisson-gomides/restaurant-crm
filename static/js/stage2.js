 // Stage 2 JavaScript - CNPJ/CPF Registration System
// Functions for dynamic form handling and validations

(function($) {
    'use strict';

    // Formatting functions - Handle null/undefined values
    window.formatCNPJ = function(value) {
        if (value == null || value === '') return value;
        let strValue = String(value);
        let cnpj = strValue.replace(/\D/g, '');
        if (cnpj.length <= 14) {
            cnpj = cnpj.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
        }
        return cnpj;
    };

    window.formatCPF = function(value) {
        if (value == null || value === '') return value;
        let strValue = String(value);
        let cpf = strValue.replace(/\D/g, '');
        if (cpf.length <= 11) {
            cpf = cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
        }
        return cpf;
    };

    window.formatPhone = function(value) {
        if (value == null || value === '') return value;
        let strValue = String(value);
        let phone = strValue.replace(/\D/g, '');
        if (phone.length <= 11) {
            if (phone.length <= 6) {
                phone = phone.replace(/(\d{2})(\d{4})/, '($1) $2');
            } else {
                phone = phone.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
            }
        }
        return phone;
    };

    window.formatCEP = function(value) {
        if (value == null || value === '') return value;
        let strValue = String(value);
        let cep = strValue.replace(/\D/g, '');
        if (cep.length <= 8) {
            cep = cep.replace(/(\d{5})(\d{3})/, '$1-$2');
        }
        return cep;
    };

    // Document validation functions
    window.validateDocument = function(document, type) {
        if (!document) return false;
        const cleanDoc = document.toString().replace(/\D/g, '');
        
        if (type === 'CNPJ') {
            return validateCNPJ(cleanDoc);
        } else if (type === 'CPF') {
            return validateCPF(cleanDoc);
        }
        return false;
    };

    function validateCNPJ(cnpj) {
        if (cnpj.length !== 14) return false;
        
        // Check for all equal numbers (invalid CNPJ)
        if (/^(\d)\1{13}$/.test(cnpj)) return false;
        
        // CNPJ validation algorithm
        let sum = 0;
        let weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
        let weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
        
        // First digit
        for (let i = 0; i < 12; i++) {
            sum += parseInt(cnpj.charAt(i)) * weights1[i];
        }
        let digit1 = sum % 11 < 2 ? 0 : 11 - (sum % 11);
        if (parseInt(cnpj.charAt(12)) !== digit1) return false;
        
        // Second digit
        sum = 0;
        for (let i = 0; i < 13; i++) {
            sum += parseInt(cnpj.charAt(i)) * weights2[i];
        }
        let digit2 = sum % 11 < 2 ? 0 : 11 - (sum % 11);
        
        return parseInt(cnpj.charAt(13)) === digit2;
    }

    function validateCPF(cpf) {
        if (cpf.length !== 11) return false;
        
        // Check for all equal numbers (invalid CPF)
        if (/^(\d)\1{10}$/.test(cpf)) return false;
        
        // CPF validation algorithm
        let sum = 0;
        let weight = 10;
        
        // First digit
        for (let i = 0; i < 9; i++) {
            sum += parseInt(cpf.charAt(i)) * weight--;
        }
        let digit1 = sum % 11 < 2 ? 0 : 11 - (sum % 11);
        if (parseInt(cpf.charAt(9)) !== digit1) return false;
        
        // Second digit
        sum = 0;
        weight = 11;
        for (let i = 0; i < 10; i++) {
            sum += parseInt(cpf.charAt(i)) * weight--;
        }
        let digit2 = sum % 11 < 2 ? 0 : 11 - (sum % 11);
        
        return parseInt(cpf.charAt(10)) === digit2;
    }

    function isValidEmail(email) {
        var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
        return regex.test(email);
    }

    // jQuery initialization
    $(document).ready(function() {
        initializeStage2();
    });

    function initializeStage2() {
        // Initialize CNPJ formatting
        $(document).on('input', '#cnpj', function() {
            this.value = window.formatCNPJ(this.value);
        });

        // Initialize CPF formatting
        $(document).on('input', '#cpf', function() {
            this.value = window.formatCPF(this.value);
        });

        // Initialize phone formatting
        $(document).on('input', '#celular', function() {
            this.value = window.formatPhone(this.value);
        });

        // Initialize CEP formatting
        $(document).on('input', '#cep', function() {
            this.value = window.formatCEP(this.value);
        });

        // CPF business field toggle
        $(document).on('change', 'input[name="perfil_compra"]', function() {
            const businessField = $('#business-field');
            const businessNameInput = $('#qual_negocio_cpf');
            const negocio = ["negocio", "ambos"];
            
            if (negocio.includes(this.value)) {
                businessField.removeClass('hidden');
                businessNameInput.attr('required', true);
            } else {
                businessNameInput.val('');
                businessField.addClass('hidden');
                businessNameInput.removeAttr('required');
            }
        });

        // Auto-fill address fields on CEP blur - FIXED: Remove hiding/showing logic
        // $(document).on('blur', '#cep', function() {
        //     const cep = $(this).val().replace(/\D/g, '');

        //     if (cep.length === 8) {
        //         getAddressByCEP(cep);
        //     }
        // });

        // Document validation on blur - NEW: AJAX validation for CNPJ/CPF
        $(document).on('blur', '#cnpj', function() {
            const cnpj = $(this).val().replace(/\D/g, '');
            if (cnpj.length === 14) {
                validateDocumentAJAX(cnpj, 'CNPJ');
            }
        });

        $(document).on('blur', '#cpf', function() {
            const cpf = $(this).val().replace(/\D/g, '');
            if (cpf.length === 11) {
                validateDocumentAJAX(cpf, 'CPF');
            }
        });

        $(document).on('blur', '#email', function() {
            const email = $.trim($(this).val());
            validateDocumentAJAX(email, 'EMAIL');
        });

        // Show loading indicator for HTMX requests
        $(document).on('htmx:beforeRequest', 'form', function() {
            $(this).find('button[type="submit"]').prop('disabled', true).addClass('opacity-50');
        });

        $(document).on('htmx:afterRequest', 'form', function() {
            $(this).find('button[type="submit"]').prop('disabled', false).removeClass('opacity-50');
        });

        // Handle HTMX validation responses specifically
        $(document).on('htmx:afterRequest', '[hx-target="#registration-form"]', function(event) {
            const xhr = event.detail.xhr;
            const responseText = xhr.responseText;

            // Hide loading indicator
            $(this).find('button[type="submit"]').prop('disabled', false).removeClass('opacity-50');

            // Only process JSON responses (error responses)
            if (xhr.getResponseHeader('content-type') && xhr.getResponseHeader('content-type').includes('application/json')) {
                try {
                    const data = JSON.parse(responseText);

                    // Handle validation errors (both 200 and 400 status codes)
                    if (data.success === false) {
                        // Handle field-specific errors
                        if (data.field_errors) {
                            showFieldErrors(data.field_errors);

                            // Focus on first error field
                            const firstErrorField = Object.keys(data.field_errors)[0];
                            if (firstErrorField) {
                                focusOnField(firstErrorField);
                            }

                            // Show toast with first error
                            const firstError = Object.values(data.field_errors)[0];
                            showErrorToast(firstError);
                            return; // Stop processing - don't allow form advance
                        }

                        // Handle general error
                        if (data.error) {
                            showErrorToast(data.error);
                            return; // Stop processing - don't allow form advance
                        }
                    }

                    // If success is true, let HTMX handle the HTML response normally
                    if (data.success === true) {
                        // This is a successful validation, HTMX will handle the HTML response
                        return;
                    }

                } catch (e) {
                    console.error('Error parsing validation response:', e);
                    showErrorToast('Erro de validação. Verifique os dados informados.');
                }
            }
            // If not JSON, it's HTML - let HTMX handle it normally
        });
        
        // Remove duplicate handler - validation is now handled in the main afterRequest handler
    }

    // Address lookup using ViaCEP - FIXED: Properly use jQuery and remove field hiding
    function getAddressByCEP(cep) {
        // Show loading overlay for CEP lookup
        $('#loading-overlay').removeClass('hidden').addClass('flex');

        $.ajax({
            url: `/registration/address/cep/${cep}`,
            method: 'GET',
            dataType: 'json',
            timeout: 10000,
            success: function(data) {
                // Hide loading overlay
                $('#loading-overlay').addClass('hidden').removeClass('flex');

                if (data.success) {
                    // Auto-fill address fields individually using jQuery
                    // CRITICAL: Do NOT hide or remove address fields
                    $('#endereco').val(data.endereco || '').trigger('change');
                    $('#bairro').val(data.bairro || '').trigger('change');
                    $('#cidade').val(data.cidade || '').trigger('change');
                    $('#estado').val(data.estado || '').trigger('change');

                    // Show success toast
                    showSuccessToast('Endereço encontrado e preenchido automaticamente!');

                    // Focus on next field
                    $('#endereco').focus();
                } else {
                    // Show error toast
                    showErrorToast(data.error || 'CEP não encontrado. Por favor, preencha manualmente.');
                }
            },
            error: function(xhr, status, error) {
                // Hide loading overlay
                $('#loading-overlay').addClass('hidden').removeClass('flex');

                console.error('Erro na busca do CEP:', error);
                showErrorToast('Erro ao buscar CEP. Por favor, tente novamente.');
            }
        });
    }

    // Document validation using AJAX - NEW: Separate function for document validation
    function validateDocumentAJAX(document, type) {
        // Clear previous validation messages
        $(`#${type.toLowerCase()}-validation`).html('');

        const doc_name = type === 'EMAIL'? "E-mail" : "Documento";

        if (type === 'EMAIL' && !isValidEmail(document)){
            $(`#${type.toLowerCase()}-validation`).html(`<div class="text-red-600 text-sm mt-1">✗ ${doc_name} inválido</div>`);
            $(`#${type.toLowerCase()}`).focus();
            return;
        }

        $.ajax({
            url: `/registration/validate/document/${type}/${document}`,
            method: 'GET',
            dataType: 'json',
            timeout: 5000,
            success: function(data) {
                if (data.valid) {
                    // Show success message
                    $(`#${type.toLowerCase()}-validation`).html(`<div class="text-green-600 text-sm mt-1">✓ ${doc_name} válido e disponível</div>`);
                } else {
                    // Show error message
                    $(`#${type.toLowerCase()}-validation`).html(`<div class="text-red-600 text-sm mt-1">✗ ${data.message}</div>`);
                    // $(`#${type.toLowerCase()}`).focus();
                }
            },
            error: function(xhr, status, error) {
                console.error(`Erro na validação do ${type}:`, error);
                $(`#${type.toLowerCase()}-validation`).html('<div class="text-red-600 text-sm mt-1">✗ Erro na validação. Tente novamente.</div>');
            }
        });
    }
    
    // Toast message functions using base.html toast system
    function showErrorToast(message) {
        // console.log('showErrorToast called with message:', message);
        
        const toast = $('#error-toast');
        const messageEl = $('#error-message');
        
        if (toast.length === 0 || messageEl.length === 0) {
            console.error('Toast elements not found, falling back to alert');
            alert('Erro: ' + message);
            return;
        }
        
        messageEl.text(message);
        // Remove the hidden display style and opacity classes
        toast.css('display', 'block');
        toast.removeClass('opacity-0 invisible').addClass('opacity-100 visible');
        
        // console.log('Toast displayed successfully');
        
        setTimeout(function() {
            closeErrorToast();
        }, 5000);
    }

    function showSuccessToast(message) {
        const toast = $('#success-toast');
        const messageEl = $('#success-message');
        
        messageEl.text(message);
        // Remove the hidden display style and opacity classes
        toast.css('display', 'block');
        toast.removeClass('opacity-0 invisible').addClass('opacity-100 visible');
        
        setTimeout(function() {
            closeSuccessToast();
        }, 5000);
    }

    function closeErrorToast() {
        const toast = $('#error-toast');
        toast.addClass('opacity-0 invisible').removeClass('opacity-100 visible');
        setTimeout(function() {
            toast.css('display', 'none');
        }, 300);
    }

    function closeSuccessToast() {
        const toast = $('#success-toast');
        toast.addClass('opacity-0 invisible').removeClass('opacity-100 visible');
        setTimeout(function() {
            toast.css('display', 'none');
        }, 300);
    }

    // Registration session creation and form loading - MOVED from select_type.html
    window.startRegistration = function(registrationType) {
        // Show loading indicator
        const loadingId = registrationType.toLowerCase() + '-loading';
        const loadingElement = $('#' + loadingId);
        if (loadingElement.length) {
            loadingElement.removeClass('hidden');
        }
        
        // Create registration session via AJAX
        $.ajax({
            url: '/registration/session',
            method: 'POST',
            data: { registration_type: registrationType },
            dataType: 'json',
            timeout: 10000,
            success: function(response) {
                // Hide loading indicator
                if (loadingElement.length) {
                    loadingElement.addClass('hidden');
                }
                
                if (response.success) {
                    // Store session data
                    window.currentSessionId = response.session_id;
                    window.currentRegistrationType = response.registration_type;
                    
                    // Load the appropriate form template
                    loadRegistrationForm(response.session_id, response.registration_type);
                    
                    // showSuccessToast('Sessão criada com sucesso!');
                } else {
                    showErrorToast(response.error || 'Erro ao criar sessão de cadastro.');
                }
            },
            error: function(xhr, status, error) {
                // Hide loading indicator
                if (loadingElement.length) {
                    loadingElement.addClass('hidden');
                }
                
                console.error('Erro ao criar sessão:', error);
                console.error('Status:', status);
                console.error('Response:', xhr.responseText);
                showErrorToast('Erro ao criar sessão de cadastro. Tente novamente.');
            }
        });
    };

    // Load registration form based on type
    window.loadRegistrationForm = function(sessionId, registrationType) {
        // Determine which form template to load
        const formUrl = registrationType === 'CNPJ'
            ? '/registration/cnpj/form'
            : '/registration/cpf/form';
        
        // Load form via AJAX
        $.ajax({
            url: formUrl,
            method: 'GET',
            data: { session_id: sessionId },
            dataType: 'html',
            timeout: 10000,
            success: function(html) {
                // Replace the registration form container with the loaded form
                $('#registration-form').html(html);
                
                // Initialize form-specific functionality
                initializeRegistrationForm(sessionId, registrationType);
            },
            error: function(xhr, status, error) {
                console.error('Erro ao carregar formulário:', error);
                console.error('Status:', status);
                console.error('Response:', xhr.responseText);
                showErrorToast('Erro ao carregar formulário. Tente novamente.');
            }
        });
    };

    // Initialize registration form after loading
    window.initializeRegistrationForm = function(sessionId, registrationType) {
        // Set up form submission handlers
        setupFormSubmission(sessionId, registrationType);
        
        // Set up validation handlers
        setupValidationHandlers();
        
        // Set up navigation handlers
        setupNavigationHandlers(sessionId, registrationType);
    };

    // Set up form submission for step 1
    function setupFormSubmission(sessionId, registrationType) {
        const form = $('#registration-form form');
        if (form.length === 0) return;
        
        form.on('submit', function(e) {
            e.preventDefault();
            
            // Show loading
            const submitButton = form.find('button[type="submit"]');
            submitButton.prop('disabled', true).addClass('opacity-50');
            
            // Collect form data into a JSON object
            const formData = {};
            const formElements = form[0].elements;
            
            for (let i = 0; i < formElements.length; i++) {
                const element = formElements[i];
                // Skip reCAPTCHA response field and submit buttons
                if (element.name && element.type !== 'submit') {
                    if (element.type === 'checkbox') {
                        formData[element.name] = element.checked;
                    } else if (element.type === 'radio') {
                        // Only include radio buttons that are checked
                        if (element.checked) {
                            formData[element.name] = element.value;
                        }
                    } else {
                        formData[element.name] = element.value;
                    }
                }
            }
            
            // Submit step 1 data as JSON with session_id as query parameter
            const step1Url = registrationType === 'CNPJ'
                ? `/registration/cnpj/step1?session_id=${sessionId}`
                : `/registration/cpf/step1?session_id=${sessionId}`;

            $.ajax({
                url: step1Url,
                method: 'POST',
                data: JSON.stringify(formData),
                contentType: 'application/json',
                dataType: 'json',
                timeout: 15000,
                success: function(response) {
                    submitButton.prop('disabled', false).removeClass('opacity-50');
                    
                    if (response.success) {
                        // Load step 2 form
                        loadStep2Form(sessionId, registrationType, response.data);
                    } else {
                        // Show validation errors
                        if (response.field_errors) {
                            showFieldErrors(response.field_errors);
                        } else if (response.error) {
                            showErrorToast(response.error);
                        }
                    }
                },
                error: function(xhr, status, error) {
                    submitButton.prop('disabled', false).removeClass('opacity-50');
                    // console.error('Erro ao enviar formulário:', error);
                    // console.error('Status:', status);
                    // console.error('Response:', xhr.responseText);
                    
                    // Try to parse error response
                    let errorMessage = 'Erro ao enviar formulário. Tente novamente.';
                    if (xhr.responseText) {
                        try {
                            const errorData = JSON.parse(xhr.responseText);
                            console.log(errorData);
                            errorDetail = errorData.detail[0] || errorData.error || errorMessage;
                            errorMessage = 'O valor "' + errorDetail.input + '" não é válido.'
                        } catch (e) {
                            errorMessage = xhr.responseText;
                        }
                    }
                    
                    // Ensure the error message is displayed to the user
                    // console.error('Error message to display:', errorMessage);
                    
                    // Try multiple methods to show the error
                    try {
                        // Method 1: Use the toast system
                        showErrorToast(errorMessage);
                        const fieldId = errorDetail.loc[errorDetail.loc.length - 1];
                        $("#"+fieldId).focus();
                        
                        // Method 2: Fallback to alert if toast fails
                        setTimeout(function() {
                            if (!$('#error-toast').hasClass('opacity-100')) {
                                alert('Erro: ' + errorMessage);
                            }
                        }, 100);
                        
                        // Method 3: Show inline error message
                        // const responseDiv = $('#step1-response');
                        // if (responseDiv.length) {
                        //     responseDiv.html(`<div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">${errorMessage}</div>`);
                        // }
                        
                    } catch (toastError) {
                        console.error('Error showing toast:', toastError);
                        // Final fallback - use browser alert
                        alert('Erro: ' + errorMessage);
                    }
                }
            });
        });
    }

    // Load step 2 form (address form)
    function loadStep2Form(sessionId, registrationType, step1Data) {
        // Store step 1 data for potential back navigation
        window.step1Data = step1Data;
        
        const step2Url = registrationType === 'CNPJ'
            ? '/registration/cnpj/step2/form'
            : '/registration/cpf/step2/form';
        
        $.ajax({
            url: step2Url,
            method: 'GET',
            data: { session_id: sessionId },
            dataType: 'html',
            timeout: 10000,
            success: function(html) {
                $('#registration-form').html(html);
                
                // Initialize step 2 form
                initializeStep2Form(sessionId, registrationType);
            },
            error: function(xhr, status, error) {
                console.error('Erro ao carregar formulário de endereço:', error);
                showErrorToast('Erro ao carregar formulário de endereço. Tente novamente.');
            }
        });
    }

    // Initialize step 2 form
    function initializeStep2Form(sessionId, registrationType) {
        const form = $('#registration-form form');
        if (form.length === 0) return;
        
        // Initialize reCAPTCHA if container exists
        if (document.getElementById('recaptcha-container')) {
            initializeRecaptcha();
        }
        
        // Set up form submission for step 2
        form.on('submit', function(e) {
            e.preventDefault();
            
            const submitButton = form.find('button[type="submit"]');
            
            // Validate reCAPTCHA first
            if (!validateRecaptcha()) {
                return;
            }
            
            submitButton.prop('disabled', true).addClass('opacity-50');
            
            // Get reCAPTCHA token
            const recaptchaToken = $('#recaptcha-token').val();
            
            // Collect form data into a JSON object
            const formData = {};
            const formElements = form[0].elements;
            
            for (let i = 0; i < formElements.length; i++) {
                const element = formElements[i];
                if (element.name && element.type !== 'submit' && element.name !== 'g-recaptcha-response') {
                    if (element.type === 'checkbox') {
                        formData[element.name] = element.checked;
                    } else if (element.type === 'radio') {
                        // Only include radio buttons that are checked
                        if (element.checked) {
                            formData[element.name] = element.value;
                        }
                    } else {
                        formData[element.name] = element.value;
                    }
                }
            }
            
            // Add session_id and recaptcha_token to the data
            // formData.session_id = sessionId;
            formData.recaptcha_token = recaptchaToken;
            
            const step2Url = registrationType === 'CNPJ'
                ? `/registration/cnpj/step2?session_id=${sessionId}`
                : `/registration/cpf/step2?session_id=${sessionId}`;
            console.log(JSON.stringify(formData));
            $.ajax({
                url: step2Url,
                method: 'POST',
                data: JSON.stringify(formData),
                contentType: 'application/json',
                dataType: 'json',
                timeout: 15000,
                success: function(response) {
                    submitButton.prop('disabled', false).removeClass('opacity-50');
                    
                    if (response.success) {
                        // Registration completed successfully
                        showSuccessToast('Cadastro realizado com sucesso!');
                        // Redirect to dedicated success page
                        window.location.href = `/registration/success/${registrationType}/${response.registration_id}`;
                        
                        // Display success message in the form container
                        // const successHtml = `
                        //     <div class="mt-8 bg-green-50 border border-green-200 rounded-lg p-8 text-center">
                        //         <div class="flex justify-center mb-4">
                        //             <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                        //                 <i class="fas fa-check text-green-600 text-2xl"></i>
                        //             </div>
                        //         </div>
                        //         <h2 class="text-2xl font-bold text-green-800 mb-2">Cadastro Concluído!</h2>
                        //         <p class="text-green-700 mb-4">Seu cadastro foi concluído com sucesso!</p>
                        //     </div>

                        //     <!-- Next Steps -->
                        //     <div class="mt-8 bg-blue-50 rounded-lg p-4">
                        //         <div class="flex">
                        //             <div class="flex-shrink-0">
                        //                 <i class="fas fa-info-circle text-blue-400"></i>
                        //             </div>
                        //             <div class="ml-3 text-left">
                        //                 <h3 class="text-sm font-medium text-blue-800">
                        //                     Próximos Passos
                        //                 </h3>
                        //                 <div class="mt-2 text-sm text-blue-700">
                        //                     <p>
                        //                         Agora basta aguardar. Nossa equipe entrará em contato o mais breve possível para entendermos melhor suas
                        //                         necessidades a fim de prestarmos o serviço da forma que melhor te atenda.
                        //                     </p>
                        //                     <ul class="mt-2 list-disc list-inside space-y-1">
                        //                         <li>Você receberá mensagem por WhatsApp em até 02 dias.</li>
                        //                         <li>Também poderá receber e-mail do nosso time.</li>
                        //                         <li>Fique Atento!</li>
                        //                     </ul>
                        //                 </div>
                        //             </div>
                        //         </div>
                        //     </div>
                        // `;
                        
                        // // Replace form with success message
                        // $('#registration-form').html(successHtml);
                        
                        // Redirect to home page after a short delay
                        // setTimeout(function() {
                        //     window.location.href = response.redirect_url || '/';
                        // }, 5000);
                    } else {
                        if (response.error) {
                            showErrorToast(response.error);
                        }
                    }
                },
                error: function(xhr, status, error) {
                    submitButton.prop('disabled', false).removeClass('opacity-50');
                    console.error('Erro ao completar cadastro:', error);
                    
                    // Reset reCAPTCHA on error
                    if (window.recaptchaWidgetId) {
                        grecaptcha.reset(window.recaptchaWidgetId);
                        document.getElementById('recaptcha-token').value = '';
                    }
                    
                    showErrorToast('Erro ao completar cadastro. Tente novamente.');
                }
            });
        });
        
        // Set up back button handler
        setupBackButton(sessionId, registrationType);
    }
    
    // Initialize reCAPTCHA widget
    function initializeRecaptcha() {
        if (typeof grecaptcha !== 'undefined' && document.getElementById('recaptcha-container')) {
            window.recaptchaWidgetId = grecaptcha.render('recaptcha-container', {
                'sitekey': window.recaptchaSiteKey,
                'callback': function(token) {
                    // Success callback
                    document.getElementById('recaptcha-token').value = token;
                    document.getElementById('recaptcha-error').classList.add('hidden');
                    console.log('reCAPTCHA verified successfully');
                },
                'expired-callback': function() {
                    // Expired callback
                    document.getElementById('recaptcha-token').value = '';
                    console.log('reCAPTCHA expired');
                },
                'error-callback': function() {
                    // Error callback
                    document.getElementById('recaptcha-token').value = '';
                    console.log('reCAPTCHA error');
                }
            });
        }
    }

    // Set up back button to return to step 1 with pre-filled data
    function setupBackButton(sessionId, registrationType) {
        const backButton = $('#registration-form a[href="/registration"]');
        if (backButton.length === 0) return;
        
        backButton.on('click', function(e) {
            e.preventDefault();
            
            // Load step 1 form with pre-filled data
            const step1Url = registrationType === 'CNPJ'
                ? '/registration/cnpj/step1/form'
                : '/registration/cpf/step1/form';
            
            $.ajax({
                url: step1Url,
                method: 'GET',
                data: {
                    session_id: sessionId,
                    prefill_data: JSON.stringify(window.step1Data || {})
                },
                dataType: 'html',
                timeout: 10000,
                success: function(html) {
                    $('#registration-form').html(html);
                    
                    // Re-initialize step 1 form
                    initializeRegistrationForm(sessionId, registrationType);
                },
                error: function(xhr, status, error) {
                    console.error('Erro ao voltar para etapa 1:', error);
                    showErrorToast('Erro ao voltar para etapa anterior. Tente novamente.');
                }
            });
        });
    }

    // Set up validation handlers
    function setupValidationHandlers() {
        // CNPJ/CPF validation on blur
        $(document).on('blur', '#cnpj', function() {
            const cnpj = $(this).val().replace(/\D/g, '');
            if (cnpj.length === 14) {
                validateDocumentAJAX(cnpj, 'CNPJ');
            }
        });
        
        $(document).on('blur', '#cpf', function() {
            const cpf = $(this).val().replace(/\D/g, '');
            if (cpf.length === 11) {
                validateDocumentAJAX(cpf, 'CPF');
            }
        });

        $(document).on('blur', '#email', function() {
            const email = $.trim($(this).val());
            validateDocumentAJAX(email, 'EMAIL');
        });
        
        // CEP auto-fill
        $(document).on('blur', '#cep', function() {
            const cep = $(this).val().replace(/\D/g, '');
            if (cep.length === 8) {
                getAddressByCEP(cep);
            }
        });
    }

    // Set up navigation handlers
    function setupNavigationHandlers(sessionId, registrationType) {
        // Handle "Voltar" button
        const backButton = $('#registration-form a[href="/registration"]');
        if (backButton.length > 0) {
            backButton.on('click', function(e) {
                e.preventDefault();
                // Return to registration type selection
                window.location.href = '/registration';
            });
        }
    }

    // Error handling functions
    function showFieldErrors(fieldErrors) {
        // Clear previous errors
        $('.field-error').remove();
        $('.border-red-500').removeClass('border-red-500');
        
        // Show new errors
        $.each(fieldErrors, function(field, error) {
            const $field = $(`[name="${field}"]`);
            if ($field.length) {
                $field.addClass('border-red-500');
                $field.after(`<div class="field-error text-sm text-red-600 mt-1">${error}</div>`);
            }
        });
        
        // Also show as toast
        const firstError = Object.values(fieldErrors)[0];
        if (firstError) {
            showErrorToast(firstError);
        }
    }
    
    function showFieldError(fieldName, errorMessage) {
        const $field = $(`[name="${fieldName}"]`);
        if ($field.length) {
            $field.addClass('border-red-500');
            $field.after(`<div class="field-error text-sm text-red-600 mt-1">${errorMessage}</div>`);
        }
    }
    
    function focusOnField(fieldName) {
        const $field = $(`[name="${fieldName}"]`);
        if ($field.length) {
            $field.focus();
            // Scroll to field if needed
            $field[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
    
    function getFieldLabel(fieldName) {
        const labels = {
            'qual_seu_negocio': 'Tipo de Negócio',
            'cnpj': 'CNPJ',
            'razao_social': 'Razão Social',
            'seu_nome': 'Seu Nome',
            'sua_funcao': 'Sua Função',
            'email': 'E-mail',
            'celular': 'Celular',
            'cpf': 'CPF',
            'nome_completo': 'Nome Completo',
            'genero': 'Gênero',
            'perfil_compra': 'Perfil de Compra',
            'qual_negocio_cpf': 'Tipo de Negócio'
        };
        return labels[fieldName] || fieldName;
    }

    // Form submission helpers
    window.submitStep2 = function(sessionId, registrationType) {
        const form = $('<form></form>');
        form.attr('action', `/registration/${registrationType}/step2`);
        form.attr('method', 'POST');
        
        // Add session ID
        form.append(`<input type="hidden" name="session_id" value="${sessionId}">`);
        
        // Add reCAPTCHA token (placeholder for now)
        form.append('<input type="hidden" name="recaptcha_token" value="test_token">');
        
        // Submit form
        form.submit();
    };

    window.submitCNPJStep2 = function(sessionId) {
        window.submitStep2(sessionId, 'cnpj');
    };

    // Success message display
    window.showSuccessMessage = function(message) {
        showSuccessToast(message);
    };

    // Make toast functions globally available for base.html
    window.closeErrorToast = closeErrorToast;
    window.closeSuccessToast = closeSuccessToast;

    // reCAPTCHA Implementation
    window.recaptchaWidgetId = null;
    window.recaptchaSiteKey = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'; // Test key - replace with your actual key
    
    // Initialize reCAPTCHA when API loads
    window.onRecaptchaLoad = function() {
        if (document.getElementById('recaptcha-container')) {
            window.recaptchaWidgetId = grecaptcha.render('recaptcha-container', {
                'sitekey': window.recaptchaSiteKey,
                'callback': function(token) {
                    // Success callback
                    document.getElementById('recaptcha-token').value = token;
                    document.getElementById('recaptcha-error').classList.add('hidden');
                    console.log('reCAPTCHA verified successfully');
                },
                'expired-callback': function() {
                    // Expired callback
                    document.getElementById('recaptcha-token').value = '';
                    console.log('reCAPTCHA expired');
                },
                'error-callback': function() {
                    // Error callback
                    document.getElementById('recaptcha-token').value = '';
                    console.log('reCAPTCHA error');
                }
            });
        }
    };
    
    // Validate reCAPTCHA before form submission
    window.validateRecaptcha = function() {
        const token = document.getElementById('recaptcha-token').value;
        const errorDiv = document.getElementById('recaptcha-error');
        
        if (!token) {
            errorDiv.classList.remove('hidden');
            return false;
        }
        
        errorDiv.classList.add('hidden');
        return true;
    };

})(jQuery);

// Ensure jQuery is loaded
if (typeof jQuery === 'undefined') {
    console.error('jQuery is required for Stage 2 functionality');
}