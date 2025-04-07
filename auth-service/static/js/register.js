// Funcionalidad para el registro de usuarios
document.addEventListener('DOMContentLoaded', function() {
  const registerForm = document.getElementById('register-form');
  
  if (registerForm) {
    registerForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const username = document.getElementById('username').value;
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      const confirmPassword = document.getElementById('confirm-password').value;
      
      // Validación básica
      if (!username || !email || !password || !confirmPassword) {
        showMessage('Por favor, complete todos los campos', 'error');
        return;
      }
      
      if (password !== confirmPassword) {
        showMessage('Las contraseñas no coinciden', 'error');
        return;
      }
      
      // Enviar solicitud de registro
      fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username: username,
          email: email,
          password: password
        })
      })
      .then(response => response.json())
      .then(data => {
        if (data.message === 'Usuario registrado exitosamente') {
          showMessage('Registro exitoso. Redirigiendo al inicio de sesión...', 'success');
          
          // Redireccionar a la página de inicio de sesión después de un breve retraso
          setTimeout(() => {
            window.location.href = '/login';
          }, 2000);
        } else {
          showMessage(data.message || 'Error en el registro', 'error');
        }
      })
      .catch(error => {
        console.error('Error:', error);
        showMessage('Error al conectar con el servidor', 'error');
      });
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
