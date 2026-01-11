/* register.js */

document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('register-form');
    const errorMessage = document.getElementById('error-message');

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Clear previous errors
        errorMessage.style.display = 'none';
        errorMessage.textContent = '';

        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm-password').value;

        // Validation
        if (password !== confirmPassword) {
            showError('Las contraseñas no coinciden');
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:8000/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok) {
                // Success! Redirect to login page
                window.location.href = 'login.html';
            } else {
                // Handle backend errors
                let detail = data.detail || 'Error al registrarse';
                if (detail.includes('already exists')) {
                    detail = 'El usuario o el correo ya están registrados';
                }
                showError(detail);
            }
        } catch (error) {
            console.error('Registration error:', error);
            showError('No se pudo conectar con el servidor. Verifica que el backend esté corriendo.');
        }
    });

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        errorMessage.style.animation = 'shake 0.5s ease-in-out';
    }
});
