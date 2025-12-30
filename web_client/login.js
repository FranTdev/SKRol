/* login.js */

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Clear previous errors
        errorMessage.style.display = 'none';
        errorMessage.textContent = '';

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            const response = await fetch('http://127.0.0.1:8000/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok) {
                // Success! Store user info (simplified for now)
                localStorage.setItem('user', JSON.stringify({
                    id: data.user_id,
                    username: data.username
                }));

                // Redirect to campaigns dashboard
                window.location.href = 'campaigns.html';
            } else {
                // Handle backend errors
                showError(data.detail || 'Error al iniciar sesión');
            }
        } catch (error) {
            console.error('Login error:', error);
            showError('No se pudo conectar con el servidor. Verifica que el backend esté corriendo.');
        }
    });

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        errorMessage.style.animation = 'shake 0.5s ease-in-out';
    }
});
