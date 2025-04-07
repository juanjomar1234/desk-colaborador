// Funcionalidad para la página de login
document.addEventListener('DOMContentLoaded', function() {
  const loginForm = document.getElementById('login-form');
  
  if (loginForm) {
    loginForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const username = document.getElementById('username').value;
      const password = document.getElementById('password').value;
      
      // Validación básica
      if (!username || !password) {
        showMessage('Por favor, complete todos los campos', 'error');
        return;
      }
      
      // Enviar solicitud de inicio de sesión al auth-service
      async function login(username, password) {
        const auth_url = process.env.AUTH_SERVICE_URL || 'http://localhost:8000';
        try {
          const response = await fetch(`${auth_url}/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              username: username,
              password: password
            })
          });
          const data = await response.json();
          if (data.access_token) {
            // Guardar token en localStorage
            localStorage.setItem('auth_token', data.access_token);
            showMessage('Inicio de sesión exitoso', 'success');
            
            // Redireccionar a la página principal después de un breve retraso
            setTimeout(() => {
              window.location.href = '/';
            }, 1500);
          } else {
            showMessage(data.message || 'Error de inicio de sesión', 'error');
          }
        } catch (error) {
          console.error('Error:', error);
          showMessage('Error al conectar con el servidor de autenticación', 'error');
        }
      }
      
      login(username, password);
    });
  }
  
  // Función para mostrar mensajes
  function showMessage(message, type) {
    const alertBox = document.createElement('div');
    alertBox.className = `alert alert-${type}`;
    alertBox.textContent = message;
    
    const container = document.querySelector('.form-container');
    const form = document.querySelector('form');
    
    container.insertBefore(alertBox, form);
    
    // Eliminar el mensaje después de 5 segundos
    setTimeout(() => {
      alertBox.remove();
    }, 5000);
  }
});
