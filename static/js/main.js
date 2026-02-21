/**
 * Grocery Store Management System - Main JavaScript
 */

// Global utility functions
const Utils = {
    // Format currency
    formatCurrency: function(amount) {
        return '₹' + parseFloat(amount).toFixed(2);
    },
    
    // Format date
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },
    
    // Format datetime
    formatDateTime: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    // Debounce function
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Show toast notification
    showToast: function(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : type === 'error' ? 'danger' : type === 'warning' ? 'warning text-dark' : 'info'} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.appendChild(toast);
        document.body.appendChild(container);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', () => container.remove());
    },
    
    // Confirm action
    confirmAction: function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    },
    
    // Validate phone number
    validatePhone: function(phone) {
        return /^\d{10}$/.test(phone);
    },
    
    // Validate email
    validateEmail: function(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }
};

// API helper functions
const API = {
    // GET request
    get: async function(url) {
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API GET Error:', error);
            Utils.showToast('An error occurred. Please try again.', 'error');
            throw error;
        }
    },
    
    // POST request
    post: async function(url, data) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.error || 'An error occurred');
            }
            return result;
        } catch (error) {
            console.error('API POST Error:', error);
            Utils.showToast(error.message || 'An error occurred. Please try again.', 'error');
            throw error;
        }
    },
    
    // PUT request
    put: async function(url, data) {
        try {
            const response = await fetch(url, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.error || 'An error occurred');
            }
            return result;
        } catch (error) {
            console.error('API PUT Error:', error);
            Utils.showToast(error.message || 'An error occurred. Please try again.', 'error');
            throw error;
        }
    },
    
    // DELETE request
    delete: async function(url) {
        try {
            const response = await fetch(url, {
                method: 'DELETE'
            });
            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.error || 'An error occurred');
            }
            return result;
        } catch (error) {
            console.error('API DELETE Error:', error);
            Utils.showToast(error.message || 'An error occurred. Please try again.', 'error');
            throw error;
        }
    }
};

// Table helper functions
const TableHelper = {
    // Create pagination
    createPagination: function(currentPage, totalPages, onPageChange) {
        if (totalPages <= 1) return '';
        
        let html = '<nav><ul class="pagination justify-content-center">';
        
        // Previous button
        html += `<li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${currentPage - 1}">Previous</a>
        </li>`;
        
        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            html += `<li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" data-page="${i}">${i}</a>
            </li>`;
        }
        
        // Next button
        html += `<li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${currentPage + 1}">Next</a>
        </li>`;
        
        html += '</ul></nav>';
        
        return html;
    },
    
    // Sort table
    sortTable: function(tableId, column, direction) {
        const table = document.getElementById(tableId);
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        rows.sort((a, b) => {
            const aVal = a.cells[column].textContent.trim();
            const bVal = b.cells[column].textContent.trim();
            
            if (direction === 'asc') {
                return aVal.localeCompare(bVal);
            } else {
                return bVal.localeCompare(aVal);
            }
        });
        
        rows.forEach(row => tbody.appendChild(row));
    }
};

// Form validation
const FormValidator = {
    // Validate required fields
    validateRequired: function(formId) {
        const form = document.getElementById(formId);
        const inputs = form.querySelectorAll('[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    },
    
    // Validate email
    validateEmail: function(email) {
        return Utils.validateEmail(email);
    },
    
    // Validate phone
    validatePhone: function(phone) {
        return Utils.validatePhone(phone);
    }
};

// Export functions
const ExportHelper = {
    // Export table to CSV
    tableToCSV: function(tableId, filename) {
        const table = document.getElementById(tableId);
        const rows = Array.from(table.querySelectorAll('tr'));
        
        let csv = rows.map(row => {
            const cells = Array.from(row.querySelectorAll('th, td'));
            return cells.map(cell => {
                let text = cell.textContent.trim();
                // Escape quotes and wrap in quotes if contains comma
                if (text.includes(',') || text.includes('"')) {
                    text = '"' + text.replace(/"/g, '""') + '"';
                }
                return text;
            }).join(',');
        }).join('\n');
        
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename || 'export.csv';
        a.click();
        window.URL.revokeObjectURL(url);
    },
    
    // Export to Excel (using CSV)
    toExcel: function(tableId, filename) {
        ExportHelper.tableToCSV(tableId, filename || 'export.xls');
    },
    
    // Print element
    printElement: function(elementId) {
        const element = document.getElementById(elementId);
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
            <head>
                <title>Print</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    body { padding: 20px; }
                    .no-print { display: none; }
                </style>
            </head>
            <body>
                ${element.innerHTML}
            </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    }
};

// Initialize common functionality when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Grocery Store Management System initialized');
    
    // Add loading indicator for async operations
    document.addEventListener('fetchstart', function() {
        document.body.classList.add('loading');
    });
    
    document.addEventListener('fetchend', function() {
        document.body.classList.remove('loading');
    });
    
    // Add click handlers for confirmation buttons
    document.querySelectorAll('[data-confirm]').forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
});

// Make utilities available globally
window.Utils = Utils;
window.API = API;
window.TableHelper = TableHelper;
window.FormValidator = FormValidator;
window.ExportHelper = ExportHelper;
