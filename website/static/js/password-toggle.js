/**
 * HubSync Password Toggle
 * Handles show/hide password functionality across all forms
 */

function togglePasswordVisibility(inputId, button) {
    const passwordInput = document.getElementById(inputId);
    const icon = button.querySelector('i');

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        icon.className = 'bi bi-eye-slash';
        button.title = 'Hide password';
        button.setAttribute('aria-label', 'Hide password');
    } else {
        passwordInput.type = 'password';
        icon.className = 'bi bi-eye';
        button.title = 'Show password';
        button.setAttribute('aria-label', 'Show password');
    }
}

// Initialize all password toggle buttons when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    const toggleButtons = document.querySelectorAll('[data-password-toggle]');
    toggleButtons.forEach(button => {
        button.title = 'Show password';
        button.setAttribute('aria-label', 'Show password');
    });
});