document.addEventListener("DOMContentLoaded", () => {
  console.log("🏥 Centro Config - Iniciado");
  
  // Cargar centro guardado o usar por defecto
  loadCentroConfig();
  
  // Si estamos en la página de configuración de centro
  const centroForm = document.getElementById("centro-config-form");
  if (centroForm) {
    centroForm.addEventListener("submit", saveCentroConfig);
  }
  
  // Si estamos en registro de donante, aplicar centro automáticamente
  if (document.getElementById("form-donante")) {
    applyCentroToDonanteForm();
  }
});

function getCentroActual() {
  return localStorage.getItem("centro_actual") || "1"; // Por defecto Hospital San Vicente
}

function setCentroActual(centroId) {
  localStorage.setItem("centro_actual", centroId);
  console.log(`🏥 Centro actual cambiado a: ${centroId}`);
}

function getCentroNombre(centroId) {
  const centros = {
    "1": "Hospital San Vicente de Paul",
    "2": "Hospital Nacional de Niños", 
    "3": "Hospital México"
  };
  return centros[centroId] || "Centro Desconocido";
}

function loadCentroConfig() {
  const centroActual = getCentroActual();
  console.log(`🏥 Centro actual: ${centroActual} - ${getCentroNombre(centroActual)}`);
  
  // Mostrar en navbar si existe el elemento
  const centroDisplay = document.getElementById("centro-display");
  if (centroDisplay) {
    centroDisplay.textContent = `Centro: ${getCentroNombre(centroActual)}`;
  }
  
  // Preseleccionar en formularios
  const centroSelect = document.querySelector("select[name='id_centro']");
  if (centroSelect) {
    centroSelect.value = centroActual;
  }
}

function applyCentroToDonanteForm() {
  const centroActual = getCentroActual();
  const centroSelect = document.querySelector("select[name='id_centro']");
  
  if (centroSelect) {
    centroSelect.value = centroActual;
    
    // Hacer el campo menos prominente ya que es automático
    const centroGroup = centroSelect.closest(".mb-3");
    if (centroGroup) {
      centroGroup.style.opacity = "0.7";
      const label = centroGroup.querySelector("label");
      if (label) {
        label.innerHTML = `Centro de Donación (Actual: ${getCentroNombre(centroActual)})`;
      }
    }
  }
}

function saveCentroConfig(e) {
  e.preventDefault();
  const formData = new FormData(e.target);
  const nuevoCentro = formData.get("centro_id");
  
  setCentroActual(nuevoCentro);
  
  alert(`Centro cambiado a: ${getCentroNombre(nuevoCentro)}`);
  
  // Recargar configuración en toda la página
  loadCentroConfig();
}

function showCentroConfig() {
  const centroActual = getCentroActual();
  
  const modal = `
    <div class="modal fade" id="centroModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Configurar Centro de Donación</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form id="centro-config-form">
              <div class="mb-3">
                <label class="form-label">Centro Actual:</label>
                <p class="fw-bold text-primary">${getCentroNombre(centroActual)}</p>
              </div>
              <div class="mb-3">
                <label class="form-label">Cambiar a:</label>
                <select name="centro_id" class="form-select" required>
                  <option value="1" ${centroActual === "1" ? "selected" : ""}>Hospital San Vicente de Paul</option>
                  <option value="2" ${centroActual === "2" ? "selected" : ""}>Hospital Nacional de Niños</option>
                  <option value="3" ${centroActual === "3" ? "selected" : ""}>Hospital México</option>
                </select>
              </div>
              <div class="d-grid">
                <button type="submit" class="btn btn-primary">Cambiar Centro</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  `;
  
  // Insertar modal en el DOM
  document.body.insertAdjacentHTML('beforeend', modal);
  
  // Mostrar modal
  const modalElement = new bootstrap.Modal(document.getElementById('centroModal'));
  modalElement.show();
  
  // Limpiar modal cuando se cierre
  document.getElementById('centroModal').addEventListener('hidden.bs.modal', function() {
    this.remove();
  });
  
  // Agregar event listener al formulario
  document.getElementById("centro-config-form").addEventListener("submit", (e) => {
    saveCentroConfig(e);
    modalElement.hide();
  });
}

// Exponer funciones globalmente
window.getCentroActual = getCentroActual;
window.setCentroActual = setCentroActual;
window.getCentroNombre = getCentroNombre;
window.showCentroConfig = showCentroConfig;