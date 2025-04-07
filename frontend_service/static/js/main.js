// Funcionalidad para la página principal
document.addEventListener('DOMContentLoaded', function() {
  // Verificar autenticación
  const token = localStorage.getItem('auth_token');
  
  if (!token) {
    // Redirigir a la página de login si no hay token
    window.location.href = '/login';
    return;
  }
  
  // Mostrar información del usuario
  const authServiceUrl = 'http://localhost:5000/api/auth/user';
  
  fetch(authServiceUrl, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('No autenticado');
    }
    return response.json();
  })
  .then(userData => {
    // Mostrar nombre de usuario
    const userInfo = document.getElementById('user-info');
    if (userInfo) {
      userInfo.textContent = `Hola, ${userData.username} (${userData.role})`;
    }
    
    // Cargar las tarjetas de aplicaciones
    loadAppCards();
  })
  .catch(error => {
    console.error('Error de autenticación:', error);
    // Redirigir a login
    localStorage.removeItem('auth_token');
    window.location.href = '/login';
  });
  
  // Configurar botón de logout
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', function() {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    });
  }
  
  // Función para cargar las tarjetas de aplicaciones
  function loadAppCards() {
    // Datos de aplicaciones
    const apps = [
      {
        id: 1,
        name: 'Auth Service',
        icon: 'lock',
        description: 'Servicio de autenticación, gestión de usuarios, roles y permisos.'
      },
      {
        id: 2,
        name: 'User Management',
        icon: 'users',
        description: 'Administración de usuarios y perfiles.'
      },
      {
        id: 3,
        name: 'Reports',
        icon: 'chart-bar',
        description: 'Generación y visualización de reportes.'
      },
      {
        id: 4,
        name: 'Settings',
        icon: 'cog',
        description: 'Configuración del sistema y preferencias.'
      },
      {
        id: 5,
        name: 'Dashboard',
        icon: 'tachometer-alt',
        description: 'Panel de control y estadísticas.'
      },
      {
        id: 6,
        name: 'Notifications',
        icon: 'bell',
        description: 'Sistema de notificaciones y alertas.'
      }
    ];
    
    const cardsContainer = document.querySelector('.cards-container');
    if (!cardsContainer) return;
    
    // Limpiar contenedor
    cardsContainer.innerHTML = '';
    
    // Crear tarjetas
    apps.forEach(app => {
      const card = document.createElement('div');
      card.className = 'card';
      card.innerHTML = `
        <div class="card-header">
          <div class="card-icon">
            <i class="fas fa-${app.icon}"></i>
          </div>
          <h3 class="card-title">${app.name}</h3>
        </div>
        <div class="card-body">
          <p class="card-description">${app.description}</p>
        </div>
        <div class="card-footer">
          <a href="#" class="card-link" data-app-id="${app.id}">Abrir aplicación</a>
        </div>
      `;
      cardsContainer.appendChild(card);
    });
    
    // Agregar event listeners a los enlaces de las tarjetas
    document.querySelectorAll('.card-link').forEach(link => {
      link.addEventListener('click', function(e) {
        e.preventDefault();
        const appId = this.getAttribute('data-app-id');
        alert(`Abriendo aplicación ${appId}`);
        // Aquí se implementaría la navegación a la aplicación específica
      });
    });
  }
});
