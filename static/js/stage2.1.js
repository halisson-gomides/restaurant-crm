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
                        showLoginSuccess('Login successful! Redirecting...');

                        setTimeout(function() {
                            window.location.href = '/auth/dashboard';
                        }, 1000);
                    } else {
                        showLoginError('Invalid response from server');
                    }
                },
                error: function(xhr, status, error) {
                    setLoginLoading(false);

                    let errorMessage = 'Login failed. Please try again.';

                    if (xhr.responseJSON && xhr.responseJSON.detail) {
                        errorMessage = xhr.responseJSON.detail;
                    } else if (xhr.status === 401) {
                        errorMessage = 'Invalid username or password';
                    } else if (xhr.status === 0) {
                        errorMessage = 'Unable to connect to server';
                    }

                    showLoginError(errorMessage);
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

    // Show login error message
    function showLoginError(message) {
        const errorDiv = $('#error-message');
        errorDiv.text(message).show();

        // Auto-hide after 5 seconds
        setTimeout(function() {
            errorDiv.fadeOut();
        }, 5000);
    }

    // Show login success message
    function showLoginSuccess(message) {
        const errorDiv = $('#error-message');
        errorDiv.removeClass('error-message')
                .addClass('success-message')
                .css({
                    'background': '#d1fae5',
                    'border-color': '#a7f3d0',
                    'color': '#065f46'
                })
                .text(message)
                .show();
    }

    // Admin dashboard functionality
    window.initializeAdminDashboard = function() {
        loadDashboardStats();
        setupDashboardActions();
    };

    // Load dashboard statistics
    function loadDashboardStats() {
        // Show loading state
        $('#stats-grid').html('<div class="col-span-full text-center py-8"><div class="loading-spinner mx-auto"></div><p class="mt-2 text-gray-600">Loading statistics...</p></div>');

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
                $('#stats-grid').html('<div class="col-span-full text-center py-8 text-red-600">Failed to load statistics</div>');
            }
        });
    }

    // Render dashboard statistics
    function renderDashboardStats(stats) {
        const statsHtml = `
            <div class="stat-card cnpj">
                <div class="stat-header">
                    <div class="stat-icon">
                        <i class="fas fa-building"></i>
                    </div>
                </div>
                <div class="stat-number">${stats.total_cnpj_registrations || 0}</div>
                <div class="stat-label">Cadastros CNPJ</div>
            </div>

            <div class="stat-card cpf">
                <div class="stat-header">
                    <div class="stat-icon">
                        <i class="fas fa-user"></i>
                    </div>
                </div>
                <div class="stat-number">${stats.total_cpf_registrations || 0}</div>
                <div class="stat-label">Cadastros CPF</div>
            </div>

            <div class="stat-card organizations">
                <div class="stat-header">
                    <div class="stat-icon">
                        <i class="fas fa-sitemap"></i>
                    </div>
                </div>
                <div class="stat-number">${stats.total_organizations || 0}</div>
                <div class="stat-label">Organizações</div>
            </div>

            <div class="stat-card users">
                <div class="stat-header">
                    <div class="stat-icon">
                        <i class="fas fa-users"></i>
                    </div>
                </div>
                <div class="stat-number">${stats.total_users || 0}</div>
                <div class="stat-label">Usuários</div>
            </div>
        `;

        $('#stats-grid').html(statsHtml);
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
            url: `/auth/registrations?${queryParams}`,
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
            const filters = {
                registration_type: $('#registration-type-filter').val(),
                date_from: $('#date-from-filter').val(),
                date_to: $('#date-to-filter').val(),
                search: $('#search-filter').val().trim()
            };

            loadRegistrations(1, filters);
        });

        $('#clear-filters').on('click', function() {
            $('#registration-type-filter').val('');
            $('#date-from-filter').val('');
            $('#date-to-filter').val('');
            $('#search-filter').val('');

            loadRegistrations(1, {});
        });
    }

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
            registration_type: $('#registration-type-filter').val(),
            date_from: $('#date-from-filter').val(),
            date_to: $('#date-to-filter').val(),
            search: $('#search-filter').val().trim(),
            format: format
        };

        const queryParams = new URLSearchParams(filters);

        // Create download link
        const downloadUrl = `/auth/registrations/export?${queryParams}`;
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

    // Utility functions
    window.logout = function() {
        localStorage.removeItem('admin_token');
        window.location.href = '/auth/login';
    };

    // Check if user is authenticated
    window.checkAuth = function() {
        const token = localStorage.getItem('admin_token');
        if (!token && window.location.pathname !== '/auth/login') {
            window.location.href = '/auth/login';
        }
    };

})(jQuery);

// Ensure jQuery is loaded
if (typeof jQuery === 'undefined') {
    console.error('jQuery is required for Stage 2.1 functionality');
}