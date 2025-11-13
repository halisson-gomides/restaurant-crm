// Stage 2.1 JavaScript - Admin Login System
// Functions for admin authentication and dashboard management

(function($) {
    'use strict';

    // Admin login functionality
    window.initializeAdminLogin = function() {
        setupLoginForm();
        setupInputFormatting();
    };

    // Set up login form submission
    function setupLoginForm() {
        $('#login-form').on('submit', function(e) {
            e.preventDefault();

            const formData = {
                username: $('#username').val().replace(/\D/g, ''), // Remove formatting for submission
                password: $('#password').val()
            };

            // Basic validation
            if (!formData.username || !formData.password) {
                showLoginError('Please fill in all fields');
                return;
            }

            // Show loading state
            setLoginLoading(true);

            // Submit login request
            $.ajax({
                url: '/auth/login',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(formData),
                timeout: 10000,
                success: function(response) {
                    setLoginLoading(false);

                    if (response.access_token) {
                        // Store token and redirect to dashboard
                        localStorage.setItem('admin_token', response.access_token);
                        // showLoginSuccess('Login successful! Redirecting...');
                        showSuccessToast('Login realizado com sucesso! Redirecionando...');

                        setTimeout(function() {
                            window.location.href = '/admin/dashboard';
                        }, 1000);
                    } else {
                        // showLoginError('Invalid response from server');
                        showErrorToast('Não foi possível realizar o Login.');
                    }
                },
                error: function(xhr, status, error) {
                    setLoginLoading(false);

                    let errorMessage = 'Login falhou. Por favor tente novamente.';

                    if (xhr.responseJSON && xhr.responseJSON.detail) {
                        errorMessage = xhr.responseJSON.detail;
                    } else if (xhr.status === 401) {
                        errorMessage = 'Credenciais inválidas';
                    } else if (xhr.status === 0) {
                        errorMessage = 'Servidor indisponível';
                    }

                    showErrorToast(errorMessage);
                }
            });
        });
    }

    // Set up input formatting for CPF/CNPJ
    function setupInputFormatting() {
        $('#username').on('input', function() {
            let value = $(this).val().replace(/\D/g, '');

            if (value.length <= 11) {
                // CPF format: 000.000.000-00
                value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
            } else if (value.length <= 14) {
                // CNPJ format: 00.000.000/0000-00
                value = value.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
            }

            $(this).val(value);
        });
    }

    // Set login form loading state
    function setLoginLoading(loading) {
        const button = $('#login-button');
        const buttonText = $('#button-text');
        const spinner = $('#loading-spinner');

        if (loading) {
            button.prop('disabled', true);
            buttonText.hide();
            spinner.show();
        } else {
            button.prop('disabled', false);
            buttonText.show();
            spinner.hide();
        }
    }


    // Admin dashboard functionality
    window.initializeAdminDashboard = function() {
        loadDashboardStats();
        setupDashboardActions();
    };

    // Load dashboard statistics
    function loadDashboardStats() {
        // Show loading state on individual stat cards
        $('.stat-number').text('...');

        $.ajax({
            url: '/auth/dashboard/stats',
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('admin_token')
            },
            success: function(data) {
                renderDashboardStats(data);
            },
            error: function(xhr) {
                console.error('Failed to load dashboard stats:', xhr);
                $('.stat-number').text('Erro');
                $('#recent-registrations tbody').html('<tr><td colspan="6" class="empty-state"><i class="fas fa-exclamation-triangle"></i><p>Erro ao carregar estatísticas</p></td></tr>');
            }
        });
    }

    // Render dashboard statistics
    function renderDashboardStats(stats) {
        // Update stat numbers
        $('#cnpj-count').text(stats.total_cnpj_registrations || 0);
        $('#cpf-count').text(stats.total_cpf_registrations || 0);
        $('#org-count').text(stats.total_organizations || 0);
        $('#user-count').text(stats.total_users || 0);

        // Render recent registrations
        renderRecentRegistrations(stats.recent_registrations || []);
    }

    // Render recent registrations
    function renderRecentRegistrations(registrations) {
        if (!registrations || registrations.length === 0) {
            $('#recent-registrations tbody').html(`
                <tr>
                    <td colspan="6" class="empty-state">
                        <i class="fas fa-inbox"></i>
                        <p>Nenhum cadastro recente encontrado</p>
                    </td>
                </tr>
            `);
            return;
        }

        let html = '';
        registrations.forEach(reg => {
            const typeClass = reg.type.toLowerCase();
            const documentFormatted = reg.type === 'CNPJ'
                ? formatCNPJ(reg.document)
                : formatCPF(reg.document);
            const phoneFormatted = window.formatPhone ? window.formatPhone(reg.phone || '') : (reg.phone || '-');

            html += `
                <tr>
                    <td>
                        <span class="registration-type ${typeClass}">${reg.type}</span>
                    </td>
                    <td>
                        <div class="registration-name">${reg.name}</div>
                    </td>
                    <td>
                        <div class="registration-document">${documentFormatted}</div>
                    </td>
                    <td>
                        <div class="registration-phone">${phoneFormatted}</div>
                    </td>
                    <td>
                        <div class="registration-email">${reg.email}</div>
                    </td>
                    <td>
                        <div class="registration-date">${new Date(reg.created_at).toLocaleDateString('pt-BR')}</div>
                    </td>
                </tr>
            `;
        });

        $('#recent-registrations tbody').html(html);
    }

    // Set up dashboard action buttons
    function setupDashboardActions() {
        // Refresh stats button
        $('#refresh-stats').on('click', function() {
            $(this).addClass('loading');
            $(this).find('i').addClass('fa-spin');

            loadDashboardStats();

            setTimeout(function() {
                $('#refresh-stats').removeClass('loading');
                $('#refresh-stats').find('i').removeClass('fa-spin');
            }, 1000);
        });
    }

    // Admin registrations management
    window.initializeAdminRegistrations = function() {
        loadRegistrations();
        setupFilters();
        setupExportActions();
    };

    // Load registrations with filters
    function loadRegistrations(page = 1, filters = {}) {
        const loadingHtml = '<div class="text-center py-8"><div class="loading-spinner mx-auto"></div><p class="mt-2 text-gray-600">Loading registrations...</p></div>';
        $('#registrations-tbody').html(loadingHtml);

        const queryParams = new URLSearchParams({
            page: page,
            ...filters
        });

        $.ajax({
            url: `/auth/registrations?${queryParams.toString()}`,
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('admin_token')
            },
            success: function(data) {
                renderRegistrations(data.registrations);
                renderPagination(data.pagination);
            },
            error: function(xhr) {
                console.error('Failed to load registrations:', xhr);
                $('#registrations-tbody').html('<tr><td colspan="6" class="text-center py-8 text-red-600">Failed to load registrations</td></tr>');
            }
        });
    }

    // Render registrations table
    function renderRegistrations(registrations) {
        if (!registrations || registrations.length === 0) {
            $('#registrations-tbody').html('<tr><td colspan="6" class="text-center py-8 text-gray-500">No registrations found</td></tr>');
            return;
        }

        let html = '';
        registrations.forEach(reg => {
            const typeClass = reg.type.toLowerCase();
            const createdDate = new Date(reg.created_at).toLocaleDateString('pt-BR');

            html += `
                <tr data-type="${reg.type}">
                    <td>
                        <span class="registration-type ${typeClass}">
                            ${reg.type}
                        </span>
                    </td>
                    <td>
                        <div style="font-weight: 600; color: #1f2937;">
                            ${reg.name}
                        </div>
                    </td>
                    <td>
                        <div style="color: #6b7280;">
                            ${reg.email}
                        </div>
                    </td>
                    <td>
                        <div style="color: #6b7280;">
                            ${reg.phone || '-'}
                        </div>
                    </td>
                    <td>
                        <div style="color: #6b7280; font-size: 0.875rem;">
                            ${createdDate}
                        </div>
                    </td>
                    <td>
                        <div class="registration-actions">
                            <button class="action-btn view-btn" onclick="viewRegistration('${reg.id}', '${reg.type}')">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="action-btn edit-btn" onclick="editRegistration('${reg.id}', '${reg.type}')">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="action-btn delete-btn" onclick="deleteRegistration('${reg.id}', '${reg.type}')">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        });

        $('#registrations-tbody').html(html);
    }

    // Render pagination
    function renderPagination(pagination) {
        if (!pagination || pagination.total_pages <= 1) {
            $('#pagination').html('');
            return;
        }

        let html = '';

        // Previous button
        if (pagination.has_prev) {
            html += `<a href="#" class="page-btn" onclick="loadRegistrations(${pagination.prev_num})">« Previous</a>`;
        }

        // Page numbers
        for (let i = 1; i <= pagination.total_pages; i++) {
            const activeClass = i === pagination.page ? 'active' : '';
            html += `<a href="#" class="page-btn ${activeClass}" onclick="loadRegistrations(${i})">${i}</a>`;
        }

        // Next button
        if (pagination.has_next) {
            html += `<a href="#" class="page-btn" onclick="loadRegistrations(${pagination.next_num})">Next »</a>`;
        }

        $('#pagination').html(html);
    }

    // Set up filters
    function setupFilters() {
        $('#apply-filters').on('click', function() {
            applyFilters();
        });

        $('#clear-filters').on('click', function() {
            clearFilters();
        });
    }

    // Global filter functions
    window.applyFilters = function() {
        const filters = {
            registration_type: $('#registration-type-filter').val(),
            date_from: $('#date-from-filter').val(),
            date_to: $('#date-to-filter').val(),
            search: $('#search-filter').val().trim()
        };

        loadRegistrations(1, filters);
    };

    window.clearFilters = function() {
        $('#registration-type-filter').val('');
        $('#date-from-filter').val('');
        $('#date-to-filter').val('');
        $('#search-filter').val('');

        loadRegistrations(1, {});
    };

    // Set up export actions
    function setupExportActions() {
        $('.export-actions button').on('click', function() {
            const format = $(this).data('format');
            exportData(format);
        });
    }

    // Export data
    function exportData(format) {
        const filters = {
            format: format,
            registration_type: $('#registration-type-filter').val(),
            date_from: $('#date-from-filter').val(),
            date_to: $('#date-to-filter').val(),
            search: $('#search-filter').val().trim()            
        };

        const queryParams = new URLSearchParams(filters);

        // Create download link
        const downloadUrl = `/auth/registrations/export?${queryParams.toString()}`;
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `registrations.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    // View registration details
    window.viewRegistration = function(id, type) {
        // Implementation for viewing registration details
        alert(`View registration ${id} (${type}) - Feature coming soon!`);
    };

    // Edit registration
    window.editRegistration = function(id, type) {
        // Implementation for editing registration
        alert(`Edit registration ${id} (${type}) - Feature coming soon!`);
    };

    // Delete registration
    window.deleteRegistration = function(id, type) {
        if (confirm(`Are you sure you want to delete this ${type} registration? This action cannot be undone.`)) {
            // Implementation for deleting registration
            alert(`Delete registration ${id} (${type}) - Feature coming soon!`);
        }
    };

    // Dashboard dropdown functionality
    window.initializeDashboardDropdown = function() {
        const $dashboardMenu = $('#dashboard-menu');
        const $dashboardDropdown = $('#dashboard-dropdown');

        if ($dashboardMenu.length && $dashboardDropdown.length) {
            $dashboardMenu.on('click', function(e) {
                e.stopPropagation();
                $dashboardDropdown.toggleClass('hidden');
            });

            // Close dropdown when clicking outside
            $(document).on('click', function(e) {
                if (!$dashboardMenu.is(e.target) && $dashboardMenu.has(e.target).length === 0 &&
                    !$dashboardDropdown.is(e.target) && $dashboardDropdown.has(e.target).length === 0) {
                    $dashboardDropdown.addClass('hidden');
                }
            });
        }
    };


    // Utility functions
    window.logout = function() {
        // Clear JWT token from localStorage/sessionStorage
        localStorage.removeItem('admin_token');
        sessionStorage.removeItem('admin_token');

        // Clear any auth headers
        if (typeof htmx !== 'undefined' && htmx.config && htmx.config.headers) {
            delete htmx.config.headers['Authorization'];
        }

        // Redirect to logout endpoint (clears cookie and redirects to login)
        window.location.href = '/auth/logout';
    };


    // Check if user is authenticated
    window.checkAuth = function() {
        const token = localStorage.getItem('admin_token');
        if (!token && window.location.pathname !== '/auth/login') {
            window.location.href = '/auth/login';
        }
    };

})(jQuery);

// Initialize dashboard dropdown on page load if elements exist
$(document).ready(function() {
    if ($('#dashboard-menu').length) {
        window.initializeDashboardDropdown();
    }
});

// Ensure jQuery is loaded
if (typeof jQuery === 'undefined') {
    console.error('jQuery is required for Stage 2.1 functionality');
}