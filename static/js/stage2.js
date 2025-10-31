 // Stage 2 JavaScript - CNPJ/CPF Registration System
// Functions for dynamic form handling and validations

(function($) {
    'use strict';

    // Formatting functions - FIXED: Handle null/undefined values
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
            
            if (this.value === 'negocio') {
                businessField.removeClass('hidden');
                businessNameInput.attr('required', true);
            } else {
                businessField.addClass('hidden');
                businessNameInput.removeAttr('required');
            }
        });

        // Auto-fill address fields on CEP blur
        $(document).on('blur', '#cep', function() {
            const cep = $(this).val().replace(/\D/g, '');
            
            if (cep.length === 8) {
                getAddressByCEP(cep);
            }
        });

        // Show loading indicator for HTMX requests
        $(document).on('htmx:beforeRequest', 'form', function() {
            $(this).find('button[type="submit"]').prop('disabled', true).addClass('opacity-50');
        });

        $(document).on('htmx:afterRequest', 'form', function() {
            $(this).find('button[type="submit"]').prop('disabled', false).removeClass('opacity-50');
        });

        // Handle HTMX responses
        $(document).on('htmx:afterOnLoad', '[hx-target]', function(event) {
            try {
                const response = event.detail.xhr.responseText;
                let data;
                
                // Try to parse as JSON
                try {
                    data = JSON.parse(response);
                } catch (e) {
                    // Response is HTML, not JSON
                    return;
                }
                
                if (data.success === false && data.field_errors) {
                    // Show field errors
                    showFieldErrors(data.field_errors);
                }
                
                if (data.success === false && data.error) {
                    showGlobalError(data.error);
                }
            } catch (e) {
                console.error('Error handling HTMX response:', e);
            }
        });
    }

    // Address lookup using ViaCEP
    function getAddressByCEP(cep) {
        const $addressFields = $('#address-fields');
        
        // Show loading state
        if ($addressFields.length === 0) {
            $addressFields = $('<div id="address-fields" class="space-y-4"></div>');
        }
        
        $addressFields.html('<div class="text-sm text-gray-500">Carregando endereço...</div>');
        
        $.ajax({
            url: `/registration/address/cep/${cep}`,
            method: 'GET',
            dataType: 'json',
            timeout: 10000,
            success: function(data) {
                if (data.html) {
                    $addressFields.html(data.html);
                } else {
                    $addressFields.html('<div class="text-sm text-red-600">CEP não encontrado. Por favor, preencha manualmente.</div>');
                }
            },
            error: function() {
                $addressFields.html('<div class="text-sm text-red-600">Erro ao buscar CEP. Por favor, tente novamente.</div>');
            }
        });
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
    }

    function showGlobalError(message) {
        // Remove existing global errors
        $('#global-error').remove();
        
        // Show new global error
        $('<div id="global-error" class="bg-red-50 border border-red-200 rounded-md p-4 mb-4">' +
            '<div class="flex">' +
                '<div class="flex-shrink-0">' +
                    '<svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">' +
                        '<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />' +
                    '</svg>' +
                '</div>' +
                '<div class="ml-3">' +
                    `<p class="text-sm text-red-700">${message}</p>` +
                '</div>' +
            '</div>' +
          '</div>').insertBefore('form');
        
        // Auto-remove after 5 seconds
        setTimeout(function() {
            $('#global-error').fadeOut();
        }, 5000);
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

    // Success message display
    window.showSuccessMessage = function(message) {
        $('<div class="bg-green-50 border border-green-200 rounded-md p-4 mb-4">' +
            '<div class="flex">' +
                '<div class="flex-shrink-0">' +
                    '<svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">' +
                        '<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />' +
                    '</svg>' +
                '</div>' +
                '<div class="ml-3">' +
                    `<p class="text-sm text-green-700">${message}</p>` +
                '</div>' +
            '</div>' +
          '</div>').insertBefore('form');
    };

})(jQuery);

// Ensure jQuery is loaded
if (typeof jQuery === 'undefined') {
    console.error('jQuery is required for Stage 2 functionality');
}