// Funcionalidad para la página de login
document.addEventListener('DOMContentLoaded', function() {
  const loginForm = document.getElementById('login-form');
  
  if (loginForm) {
    loginForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      
      const username = document.getElementById('username').value;
      const password = document.getElementById('password').value;
      
      try {
        // Usar la URL relativa ya que estamos en el frontend
        const response = await fetch('/login', {
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
          localStorage.setItem('token', data.access_token);
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
