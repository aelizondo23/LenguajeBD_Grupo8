document.addEventListener("DOMContentLoaded", () => {
  console.log("🔧 BLOODCARE - Panel de Administración Iniciado");
  
  // Verificar que sea administrador
  const usuario = JSON.parse(localStorage.getItem('usuario') || '{}');
  if (usuario.rol !== 'Administrador') {
    alert('Acceso denegado. Solo administradores pueden acceder.');
    window.location.href = 'index.html';
    return;
  }
});

// ===== GESTIÓN DE USUARIOS =====
function showUserManagement() {
  const modal = createModal('Gestión de Usuarios', `
    <div class="row">
      <div class="col-12 mb-3">
        <button class="btn btn-primary" onclick="showAddUserForm()">
          <i class="bi bi-person-plus"></i> Agregar Usuario
        </button>
      </div>
    </div>
    <div class="table-responsive">
      <table class="table table-striped">
        <thead>
          <tr>
            <th>ID</th>
            <th>Usuario</th>
            <th>Rol</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody id="users-table-body">
          <tr><td colspan="5" class="text-center">Cargando usuarios...</td></tr>
        </tbody>
      </table>
    </div>
  `);
  
  modal.show();
  loadUsers();
}

function showAddUserForm() {
  const modal = createModal('Agregar Nuevo Usuario', `
    <form id="add-user-form">
      <div class="mb-3">
        <label class="form-label">Nombre de Usuario *</label>
        <input type="text" name="nombre_usuario" class="form-control" required>
      </div>
      <div class="mb-3">
        <label class="form-label">Contraseña *</label>
        <input type="password" name="contrasena" class="form-control" required>
      </div>
      <div class="mb-3">
        <label class="form-label">Rol *</label>
        <select name="id_rol" class="form-select" required>
          <option value="">Seleccione un rol</option>
          <option value="1">Administrador</option>
          <option value="2">Diplomado</option>
          <option value="3">Técnico</option>
          <option value="4">Microbiólogo</option>
          <option value="5">Jefatura</option>
        </select>
      </div>
      <div class="mb-3">
        <label class="form-label">Estado</label>
        <select name="estado" class="form-select">
          <option value="Activo">Activo</option>
          <option value="Inactivo">Inactivo</option>
        </select>
      </div>
      <div class="d-grid">
        <button type="submit" class="btn btn-primary">
          <i class="bi bi-person-plus"></i> Crear Usuario
        </button>
      </div>
    </form>
  `);
  
  modal.show();
  
  document.getElementById('add-user-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    await createUser(new FormData(e.target));
    modal.hide();
  });
}

async function loadUsers() {
  try {
    const token = localStorage.getItem('token');
    console.log('🔍 Cargando usuarios con token:', token ? 'PRESENTE' : 'NO HAY TOKEN');
    
    const response = await fetch('http://localhost:5000/api/admin/usuarios', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    console.log('📥 Respuesta del servidor:', response.status, response.statusText);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Error del servidor:', errorText);
      throw new Error(`HTTP ${response.status} - ${errorText}`);
    }
    
    const users = await response.json();
    console.log('Usuarios cargados:', users);
    
    const tbody = document.getElementById('users-table-body');
    
    if (!users || users.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No hay usuarios registrados</td></tr>';
      return;
    }
    
    tbody.innerHTML = users.map(user => `
      <tr>
        <td>${user.id_usuario}</td>
        <td>${user.nombre_usuario}</td>
        <td><span class="badge bg-info">${user.rol}</span></td>
        <td><span class="badge ${user.estado === 'Activo' ? 'bg-success' : 'bg-danger'}">${user.estado}</span></td>
        <td>
          <button class="btn btn-sm btn-outline-primary" onclick="editUser(${user.id_usuario})">
            <i class="bi bi-pencil"></i>
          </button>
          <button class="btn btn-sm btn-outline-danger" onclick="deleteUser(${user.id_usuario})">
            <i class="bi bi-trash"></i>
          </button>
        </td>
      </tr>
    `).join('');
    
  } catch (error) {
    console.error('Error cargando usuarios:', error);
    const tbody = document.getElementById('users-table-body');
    tbody.innerHTML = `<tr><td colspan="5" class="text-danger text-center">Error: ${error.message}</td></tr>`;
  }
}

async function createUser(formData) {
  try {
    const token = localStorage.getItem('token');
    
    if (!token) {
      throw new Error('No hay token de autenticación');
    }
    
    const userData = {
      nombre_usuario: formData.get('nombre_usuario'),
      contrasena: formData.get('contrasena'),
      id_rol: parseInt(formData.get('id_rol')),
      estado: formData.get('estado') || 'Activo'
    };
    
    // Validar datos antes de enviar
    if (!userData.nombre_usuario || !userData.contrasena || !userData.id_rol) {
      throw new Error('Todos los campos son requeridos');
    }
    
    // Asegurar que id_rol sea número
    userData.id_rol = parseInt(userData.id_rol);
    if (isNaN(userData.id_rol) || userData.id_rol < 1 || userData.id_rol > 5) {
      throw new Error('Debe seleccionar un rol válido');
    }
    
    // Validar longitud de campos
    if (userData.nombre_usuario.length < 3) {
      throw new Error('El nombre de usuario debe tener al menos 3 caracteres');
    }
    
    if (userData.contrasena.length < 6) {
      throw new Error('La contraseña debe tener al menos 6 caracteres');
    }
    
    console.log('🔍 Creando usuario:', userData);
    
    const response = await fetch('http://localhost:5000/api/admin/usuarios', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(userData)
    });
    
    console.log('📥 Respuesta crear usuario:', response.status, response.statusText);
    
    let result;
    try {
      result = await response.json();
    } catch {
      result = { error: 'Error de comunicación con el servidor' };
    }
    console.log('📥 Resultado:', result);
    
    if (response.ok) {
      alert('Usuario creado correctamente');
      loadUsers(); // Recargar la lista
    } else {
      throw new Error(result.error || 'Error al crear usuario');
    }
    
  } catch (error) {
    console.error('Error creando usuario:', error);
    alert(`Error al crear usuario:\n\n${error.message}`);
  }
}

// ===== GESTIÓN DE CENTROS =====
function showCenterManagement() {
  const modal = createModal('Gestión de Centros de Donación', `
    <div class="row">
      <div class="col-12 mb-3">
        <button class="btn btn-success" onclick="showAddCenterForm()">
          <i class="bi bi-building-add"></i> Agregar Centro
        </button>
      </div>
    </div>
    <div class="table-responsive">
      <table class="table table-striped">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Dirección</th>
            <th>Teléfono</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody id="centers-table-body">
          <tr><td colspan="5" class="text-center">Cargando centros...</td></tr>
        </tbody>
      </table>
    </div>
  `);
  
  modal.show();
  loadCenters();
}

function showAddCenterForm() {
  const modal = createModal('Agregar Nuevo Centro', `
    <form id="add-center-form">
      <div class="mb-3">
        <label class="form-label">Nombre del Centro *</label>
        <input type="text" name="nombre" class="form-control" required>
      </div>
      <div class="mb-3">
        <label class="form-label">Dirección *</label>
        <input type="text" name="direccion" class="form-control" required>
      </div>
      <div class="mb-3">
        <label class="form-label">Teléfono</label>
        <input type="tel" name="telefono" class="form-control">
      </div>
      <div class="d-grid">
        <button type="submit" class="btn btn-success">
          <i class="bi bi-building-add"></i> Crear Centro
        </button>
      </div>
    </form>
  `);
  
  modal.show();
  
  document.getElementById('add-center-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    await createCenter(new FormData(e.target));
    modal.hide();
  });
}

async function loadCenters() {
  try {
    const token = localStorage.getItem('token');
    console.log('🔍 Cargando centros con token:', token ? 'PRESENTE' : 'NO HAY TOKEN');
    
    const response = await fetch('http://localhost:5000/api/admin/centros', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    console.log('📥 Respuesta del servidor:', response.status, response.statusText);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Error del servidor:', errorText);
      throw new Error(`HTTP ${response.status} - ${errorText}`);
    }
    
    const centers = await response.json();
    console.log('Centros cargados:', centers);
    
    const tbody = document.getElementById('centers-table-body');
    
    if (!centers || centers.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No hay centros registrados</td></tr>';
      return;
    }
    
    tbody.innerHTML = centers.map(center => `
      <tr>
        <td>${center.id_centro}</td>
        <td>${center.nombre}</td>
        <td>${center.direccion || 'N/A'}</td>
        <td>${center.telefono || 'N/A'}</td>
        <td>
          <button class="btn btn-sm btn-outline-primary" onclick="editCenter(${center.id_centro})">
            <i class="bi bi-pencil"></i>
          </button>
          <button class="btn btn-sm btn-outline-danger" onclick="deleteCenter(${center.id_centro})">
            <i class="bi bi-trash"></i>
          </button>
        </td>
      </tr>
    `).join('');
    
  } catch (error) {
    console.error('Error cargando centros:', error);
    const tbody = document.getElementById('centers-table-body');
    tbody.innerHTML = `<tr><td colspan="5" class="text-danger text-center">Error: ${error.message}</td></tr>`;
  }
}

async function createCenter(formData) {
  try {
    const token = localStorage.getItem('token');
    const centerData = {
      nombre: formData.get('nombre'),
      direccion: formData.get('direccion'),
      telefono: formData.get('telefono') || ''
    };
    
    console.log('🔍 Creando centro:', centerData);
    console.log('🔍 Token:', token ? 'PRESENTE' : 'NO HAY TOKEN');
    
    const response = await fetch('http://localhost:5000/api/admin/centros', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(centerData)
    });
    
    console.log('📥 Respuesta crear centro:', response.status, response.statusText);
    
    const result = await response.json();
    console.log('📥 Resultado:', result);
    
    if (response.ok) {
      alert('Centro creado correctamente');
      loadCenters(); // Recargar la lista
    } else {
      throw new Error(result.error || 'Error al crear centro');
    }
    
  } catch (error) {
    console.error('Error creando centro:', error);
    alert(`Error al crear centro:\n\n${error.message}`);
  }
}

// ===== CONFIGURACIÓN DEL SISTEMA =====
function showSystemConfig() {
  const modal = createModal('Configuración del Sistema', `
    <div class="row">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h6><i class="bi bi-droplet"></i> Tipos de Sangre</h6>
          </div>
          <div class="card-body">
            <div class="list-group">
              <div class="list-group-item d-flex justify-content-between">
                <span>A+ (ID: 1)</span>
                <button class="btn btn-sm btn-outline-primary">Editar</button>
              </div>
              <div class="list-group-item d-flex justify-content-between">
                <span>A- (ID: 2)</span>
                <button class="btn btn-sm btn-outline-primary">Editar</button>
              </div>
              <div class="list-group-item d-flex justify-content-between">
                <span>B+ (ID: 3)</span>
                <button class="btn btn-sm btn-outline-primary">Editar</button>
              </div>
              <div class="list-group-item d-flex justify-content-between">
                <span>B- (ID: 4)</span>
                <button class="btn btn-sm btn-outline-primary">Editar</button>
              </div>
            </div>
            <button class="btn btn-sm btn-success mt-2">
              <i class="bi bi-plus"></i> Agregar Tipo
            </button>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h6><i class="bi bi-gear"></i> Parámetros Generales</h6>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <label class="form-label">Volumen mínimo donación (ml)</label>
              <input type="number" class="form-control" value="450">
            </div>
            <div class="mb-3">
              <label class="form-label">Volumen máximo donación (ml)</label>
              <input type="number" class="form-control" value="500">
            </div>
            <div class="mb-3">
              <label class="form-label">Días entre donaciones</label>
              <input type="number" class="form-control" value="56">
            </div>
            <button class="btn btn-primary">
              <i class="bi bi-check"></i> Guardar Configuración
            </button>
          </div>
        </div>
      </div>
    </div>
  `, 'modal-xl');
  
  modal.show();
}

// ===== REPORTES =====
function showReports() {
  const modal = createModal('Reportes y Auditoría', `
    <div class="row">
      <div class="col-md-4 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="bi bi-file-earmark-pdf fs-1 text-danger"></i>
            <h6 class="card-title mt-2">Reporte de Donantes</h6>
            <button class="btn btn-outline-danger btn-sm">
              <i class="bi bi-download"></i> Descargar PDF
            </button>
          </div>
        </div>
      </div>
      <div class="col-md-4 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="bi bi-file-earmark-excel fs-1 text-success"></i>
            <h6 class="card-title mt-2">Reporte de Donaciones</h6>
            <button class="btn btn-outline-success btn-sm">
              <i class="bi bi-download"></i> Descargar Excel
            </button>
          </div>
        </div>
      </div>
      <div class="col-md-4 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="bi bi-file-earmark-text fs-1 text-info"></i>
            <h6 class="card-title mt-2">Log de Actividad</h6>
            <button class="btn btn-outline-info btn-sm">
              <i class="bi bi-eye"></i> Ver Log
            </button>
          </div>
        </div>
      </div>
    </div>
    <div class="mt-4">
      <h6>Actividad Reciente:</h6>
      <div class="list-group">
        <div class="list-group-item">
          <div class="d-flex w-100 justify-content-between">
            <h6 class="mb-1">Donante registrado</h6>
            <small>Hace 3 minutos</small>
          </div>
          <p class="mb-1">Usuario: admin1 registró donante ID: 102340111</p>
        </div>
        <div class="list-group-item">
          <div class="d-flex w-100 justify-content-between">
            <h6 class="mb-1">Donación registrada</h6>
            <small>Hace 15 minutos</small>
          </div>
          <p class="mb-1">Usuario: tecnico1 registró donación ID: 45</p>
        </div>
        <div class="list-group-item">
          <div class="d-flex w-100 justify-content-between">
            <h6 class="mb-1">Login exitoso</h6>
            <small>Hace 1 hora</small>
          </div>
          <p class="mb-1">Usuario: diplomado1 inició sesión</p>
        </div>
      </div>
    </div>
  `, 'modal-lg');
  
  modal.show();
}

// ===== UTILIDADES =====
function createModal(title, content, size = 'modal-lg') {
  const modalId = 'admin-modal-' + Date.now();
  const modalHtml = `
    <div class="modal fade" id="${modalId}" tabindex="-1">
      <div class="modal-dialog ${size}">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">${title}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            ${content}
          </div>
        </div>
      </div>
    </div>
  `;
  
  document.getElementById('modal-container').innerHTML = modalHtml;
  const modalElement = new bootstrap.Modal(document.getElementById(modalId));
  
  // Limpiar modal cuando se cierre
  document.getElementById(modalId).addEventListener('hidden.bs.modal', function() {
    this.remove();
  });
  
  return modalElement;
}

function editUser(id) {
  // Implementar modal de edición
  const modal = createModal('Editar Usuario', `
    <form id="edit-user-form">
      <input type="hidden" name="id_usuario" value="${id}">
      <div class="mb-3">
        <label class="form-label">Nuevo Rol</label>
        <select name="id_rol" class="form-select" required>
          <option value="1">Administrador</option>
          <option value="2">Diplomado</option>
          <option value="3">Técnico</option>
          <option value="4">Microbiólogo</option>
          <option value="5">Jefatura</option>
        </select>
      </div>
      <div class="mb-3">
        <label class="form-label">Estado</label>
        <select name="estado" class="form-select">
          <option value="Activo">Activo</option>
          <option value="Inactivo">Inactivo</option>
        </select>
      </div>
      <div class="d-grid">
        <button type="submit" class="btn btn-primary">
          <i class="bi bi-check"></i> Actualizar Usuario
        </button>
      </div>
    </form>
  `);
  
  modal.show();
  
  document.getElementById('edit-user-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    await updateUser(id, new FormData(e.target));
    modal.hide();
  });
}

function deleteUser(id) {
  if (confirm('¿Está seguro de eliminar este usuario?')) {
    deleteUserConfirmed(id);
  }
}

async function updateUser(id, formData) {
  try {
    const token = localStorage.getItem('token');
    const userData = {
      id_rol: parseInt(formData.get('id_rol')),
      estado: formData.get('estado')
    };
    
    const response = await fetch(`http://localhost:5000/api/admin/usuarios/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(userData)
    });
    
    const result = await response.json();
    
    if (response.ok) {
      alert('Usuario actualizado correctamente');
      loadUsers();
    } else {
      throw new Error(result.error || 'Error al actualizar usuario');
    }
    
  } catch (error) {
    console.error('Error actualizando usuario:', error);
    alert(`Error al actualizar usuario: ${error.message}`);
  }
}

async function deleteUserConfirmed(id) {
  try {
    const token = localStorage.getItem('token');
    
    const response = await fetch(`http://localhost:5000/api/admin/usuarios/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    const result = await response.json();
    
    if (response.ok) {
      alert('Usuario desactivado correctamente');
      loadUsers();
    } else {
      throw new Error(result.error || 'Error al eliminar usuario');
    }
    
  } catch (error) {
    console.error('Error eliminando usuario:', error);
    alert(`Error al eliminar usuario: ${error.message}`);
  }
}

function editCenter(id) {
  const modal = createModal('Editar Centro', `
    <form id="edit-center-form">
      <input type="hidden" name="id_centro" value="${id}">
      <div class="mb-3">
        <label class="form-label">Nombre del Centro</label>
        <input type="text" name="nombre" class="form-control" required>
      </div>
      <div class="mb-3">
        <label class="form-label">Dirección</label>
        <input type="text" name="direccion" class="form-control">
      </div>
      <div class="mb-3">
        <label class="form-label">Teléfono</label>
        <input type="tel" name="telefono" class="form-control">
      </div>
      <div class="d-grid">
        <button type="submit" class="btn btn-success">
          <i class="bi bi-check"></i> Actualizar Centro
        </button>
      </div>
    </form>
  `);
  
  modal.show();
  
  document.getElementById('edit-center-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    await updateCenter(id, new FormData(e.target));
    modal.hide();
  });
}

function deleteCenter(id) {
  if (confirm('¿Está seguro de eliminar este centro?')) {
    alert(`Centro ID: ${id} eliminado (simulado)`);
  }
}

async function updateCenter(id, formData) {
  try {
    const centerData = {
      nombre: formData.get('nombre'),
      direccion: formData.get('direccion'),
      telefono: formData.get('telefono') || ''
    };
    
    console.log('Actualizando centro:', centerData);
    alert('Centro actualizado correctamente (simulado)');
    loadCenters();
    
  } catch (error) {
    console.error('Error actualizando centro:', error);
    alert('Error al actualizar centro');
  }
}

// Exponer funciones globalmente
window.showUserManagement = showUserManagement;
window.showCenterManagement = showCenterManagement;
window.showSystemConfig = showSystemConfig;
window.showReports = showReports;