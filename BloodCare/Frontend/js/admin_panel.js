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


// ===== GESTIÓN DE CENTROS =====
function redirigirA(url) {
    window.location.href =url;
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


// Exponer funciones globalmente
window.showUserManagement = showUserManagement;
window.showSystemConfig = showSystemConfig;
window.showReports = showReports;