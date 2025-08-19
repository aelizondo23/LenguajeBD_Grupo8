document.addEventListener("DOMContentLoaded", () => {
  console.log("🩸 BLOODCARE - Sistema Principal Iniciado");

  // Actualizar UI de navegación
  if (typeof updateNavUI === "function") {
    updateNavUI();
  }

  // Cargar donaciones si estamos en la página correspondiente
  if (document.getElementById("lista-donaciones")) {
    if (typeof protectPage === "function") {
      try {
        protectPage();
        cargarDonaciones().catch(console.error);
      } catch (e) {
        console.error("❌ Error en protectPage:", e);
      }
    }
  }

  // Cargar donantes si estamos en la página correspondiente
  if (document.getElementById("lista-donantes")) {
    if (typeof protectPage === "function") {
      try {
        protectPage();
        cargarDonantes().catch(console.error);
      } catch (e) {
        console.error("❌ Error en protectPage:", e);
      }
    }
  }

  // Cargar estadísticas si estamos en la página correspondiente
  if (document.getElementById("estadisticas-container")) {
    if (typeof protectPage === "function") {
      try {
        protectPage();
        cargarEstadisticas().catch(console.error);
      } catch (e) {
        console.error("❌ Error en protectPage:", e);
      }
    }
  }
});

// ===== FUNCIONES PARA CARGAR DATOS =====

async function cargarDonaciones() {
  console.log("📋 Cargando lista de donaciones...");
  
  try {
    const response = await authFetch(`${API}/api/donaciones/listar`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status} - Error al cargar donaciones`);
    }
    
    const donaciones = await response.json();
    console.log(`✅ ${donaciones.length} donaciones cargadas`);
    
    const lista = document.getElementById("lista-donaciones");
    if (!lista) return;
    
    lista.innerHTML = "";
    
    if (donaciones.length === 0) {
      lista.innerHTML = '<li class="list-group-item text-muted">No hay donaciones registradas</li>';
      return;
    }
    
    donaciones.forEach(donacion => {
      const li = document.createElement("li");
      li.className = "list-group-item d-flex justify-content-between align-items-center";
      
      const fecha = donacion.fecha ? new Date(donacion.fecha).toLocaleDateString('es-ES') : 'N/A';
      
      li.innerHTML = `
        <div>
          <strong>ID:</strong> ${donacion.id_donacion} | 
          <strong>Donante:</strong> ${donacion.id_donante} | 
          <strong>Fecha:</strong> ${fecha} | 
          <strong>Volumen:</strong> ${donacion.volumen_ml} ml
        </div>
        <span class="badge ${getEstadoBadgeClass(donacion.estado)}">${donacion.estado}</span>
      `;
      
      lista.appendChild(li);
    });
    
  } catch (error) {
    console.error("❌ Error cargando donaciones:", error);
    const lista = document.getElementById("lista-donaciones");
    if (lista) {
      lista.innerHTML = `<li class="list-group-item text-danger">Error: ${error.message}</li>`;
    }
  }
}

async function cargarDonantes() {
  console.log("👥 Cargando lista de donantes...");
  
  try {
    const response = await authFetch(`${API}/api/donantes/listar`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status} - Error al cargar donantes`);
    }
    
    const donantes = await response.json();
    console.log(`✅ ${donantes.length} donantes cargados`);
    
    const lista = document.getElementById("lista-donantes");
    if (!lista) return;
    
    lista.innerHTML = "";
    
    if (donantes.length === 0) {
      lista.innerHTML = '<li class="list-group-item text-muted">No hay donantes registrados</li>';
      return;
    }
    
    donantes.forEach(donante => {
      const li = document.createElement("li");
      li.className = "list-group-item";
      
      const fechaNac = donante.fecha_nacimiento ? 
        new Date(donante.fecha_nacimiento).toLocaleDateString('es-ES') : 'N/A';
      
      li.innerHTML = `
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <strong>${donante.nombre} ${donante.apellido}</strong><br>
            <small class="text-muted">
              Cédula: ${donante.id_donante} | 
              Tipo: ${donante.tipo_sangre || 'N/A'} | 
              Sexo: ${donante.sexo} | 
              Nacimiento: ${fechaNac}
            </small>
          </div>
          <div>
            <button class="btn btn-sm btn-outline-primary" onclick="verDonante('${donante.id_donante}')">
              Ver Detalles
            </button>
          </div>
        </div>
      `;
      
      lista.appendChild(li);
    });
    
  } catch (error) {
    console.error("❌ Error cargando donantes:", error);
    const lista = document.getElementById("lista-donantes");
    if (lista) {
      lista.innerHTML = `<li class="list-group-item text-danger">Error: ${error.message}</li>`;
    }
  }
}

async function cargarEstadisticas() {
  console.log("📊 Cargando estadísticas...");
  
  try {
    // Cargar donantes y donaciones para generar estadísticas básicas
    const [donantesRes, donacionesRes] = await Promise.all([
      authFetch(`${API}/api/donantes/listar`),
      authFetch(`${API}/api/donaciones/listar`)
    ]);
    
    if (!donantesRes.ok || !donacionesRes.ok) {
      throw new Error('Error al cargar datos para estadísticas');
    }
    
    const donantes = await donantesRes.json();
    const donaciones = await donacionesRes.json();
    
    console.log(`✅ Estadísticas: ${donantes.length} donantes, ${donaciones.length} donaciones`);
    
    // Calcular estadísticas básicas
    const stats = {
      totalDonantes: donantes.length,
      totalDonaciones: donaciones.length,
      volumenTotal: donaciones.reduce((sum, d) => sum + (d.volumen_ml || 0), 0),
      donacionesHoy: donaciones.filter(d => {
        if (!d.fecha) return false;
        const hoy = new Date().toDateString();
        const fechaDonacion = new Date(d.fecha).toDateString();
        return hoy === fechaDonacion;
      }).length
    };
    
    // Mostrar estadísticas
    mostrarEstadisticas(stats);
    
  } catch (error) {
    console.error("❌ Error cargando estadísticas:", error);
    const container = document.getElementById("estadisticas-container");
    if (container) {
      container.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
    }
  }
}

// ===== FUNCIONES AUXILIARES =====

function getEstadoBadgeClass(estado) {
  switch (estado?.toLowerCase()) {
    case 'completada':
    case 'aprobada':
      return 'bg-success';
    case 'pendiente':
      return 'bg-warning text-dark';
    case 'rechazada':
      return 'bg-danger';
    default:
      return 'bg-secondary';
  }
}

function mostrarEstadisticas(stats) {
  const container = document.getElementById("estadisticas-container");
  if (!container) return;
  
  container.innerHTML = `
    <div class="row">
      <div class="col-md-3">
        <div class="card text-center">
          <div class="card-body">
            <h5 class="card-title text-primary">${stats.totalDonantes}</h5>
            <p class="card-text">Total Donantes</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center">
          <div class="card-body">
            <h5 class="card-title text-success">${stats.totalDonaciones}</h5>
            <p class="card-text">Total Donaciones</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center">
          <div class="card-body">
            <h5 class="card-title text-info">${stats.volumenTotal.toLocaleString()} ml</h5>
            <p class="card-text">Volumen Total</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center">
          <div class="card-body">
            <h5 class="card-title text-warning">${stats.donacionesHoy}</h5>
            <p class="card-text">Donaciones Hoy</p>
          </div>
        </div>
      </div>
    </div>
  `;
}

async function verDonante(idDonante) {
  console.log(`👤 Viendo detalles del donante: ${idDonante}`);
  
  try {
    const response = await authFetch(`${API}/api/donantes/${idDonante}`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status} - Error al cargar donante`);
    }
    
    const donante = await response.json();
    
    // Mostrar modal o alert con detalles
    const fechaNac = donante.fecha_nacimiento ? 
      new Date(donante.fecha_nacimiento).toLocaleDateString('es-ES') : 'N/A';
    
    const detalles = `
DETALLES DEL DONANTE

Nombre: ${donante.nombre} ${donante.apellido}
Cédula: ${donante.id_donante}
Fecha de Nacimiento: ${fechaNac}
Sexo: ${donante.sexo}
Tipo de Sangre: ${donante.tipo_sangre || 'N/A'}
Dirección: ${donante.direccion || 'N/A'}
Teléfono: ${donante.telefono || 'N/A'}
Correo: ${donante.correo || 'N/A'}
    `;
    
    alert(detalles);
    
  } catch (error) {
    console.error("❌ Error cargando donante:", error);
    alert(`Error al cargar donante: ${error.message}`);
  }
}

// Exponer funciones globalmente
window.cargarDonaciones = cargarDonaciones;
window.cargarDonantes = cargarDonantes;
window.cargarEstadisticas = cargarEstadisticas;
window.verDonante = verDonante;