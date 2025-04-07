// Funcionalidad para la autenticación
document.addEventListener('DOMContentLoaded', function() {
  const loginForm = document.getElementById('login-form');
  
  if (loginForm) {
    loginForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      
      const username = document.getElementById('username').value;
      const password = document.getElementById('password').value;
      
      // Validación básica
      if (!username || !password) {
        showMessage('Por favor, complete todos los campos', 'error');
        return;
      }
      
      try {
        const auth_url = process.env.AUTH_SERVICE_URL || 'http://auth:8000';  // Cambiar a http://auth:8000 para Docker
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

        if (response.ok) {
          // Guardar el token
          localStorage.setItem('token', data.access_token);
          // Redirigir al usuario
          window.location.href = '/';
        } else {
          showMessage(data.message || 'Error al iniciar sesión', 'error');
        }
      } catch (error) {
        console.error('Error:', error);
        showMessage('Error al conectar con el servidor', 'error');
      }
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
