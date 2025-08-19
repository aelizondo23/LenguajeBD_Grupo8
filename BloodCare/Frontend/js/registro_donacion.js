document.addEventListener("DOMContentLoaded", () => {
  console.log("🩸 BLOODCARE - Registro de Donación Iniciado");
  
  // TEMPORALMENTE SIN VERIFICACIÓN DE AUTENTICACIÓN
  console.log("⚠️ MODO DEBUG: Sin verificación de autenticación");
  
  if (typeof updateNavUI === "function") {
    updateNavUI();
  }

  // Buscar el formulario específico
  const form = document.getElementById("form-donacion");
  
  if (!form) {
    console.error('❌ No se encontró el formulario de donación con ID "form-donacion"');
    return;
  }

  console.log('✅ Formulario de donación encontrado');

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    console.log('\n🚀 === INICIANDO REGISTRO DE DONACIÓN ===');
    
    const fd = new FormData(form);
    
    // Debug: mostrar todos los datos del formulario
    console.log('📋 Datos del formulario:');
    for (let [key, value] of fd.entries()) {
      console.log(`  ${key}: "${value}"`);
    }

    try {
      // Obtener datos específicos del HTML
      const cedula_donante = (fd.get("cedula_donante") || "").toString().trim();
      const fecha_donacion = (fd.get("fecha_donacion") || "").toString().trim();
      
      // Calcular volumen total de los componentes
      const globulos_rojos = Number(fd.get("globulos_rojos") || 0);
      const plasma = Number(fd.get("plasma") || 0);
      const plaquetas = Number(fd.get("plaquetas") || 0);
      
      const volumen_total = globulos_rojos + plasma + plaquetas;
      
      console.log(`🩸 Componentes:`);
      console.log(`  Glóbulos Rojos: ${globulos_rojos} ml`);
      console.log(`  Plasma: ${plasma} ml`);
      console.log(`  Plaquetas: ${plaquetas} ml`);
      console.log(`  TOTAL: ${volumen_total} ml`);

      // Validaciones
      if (!cedula_donante) {
        throw new Error("Debe indicar la cédula del donante");
      }
      if (!fecha_donacion) {
        throw new Error("Debe indicar la fecha de donación");
      }
      if (volumen_total <= 0) {
        throw new Error("Debe indicar al menos un volumen válido en algún componente");
      }

      // Preparar payload para el backend
      const payload = {
        id_donante: cedula_donante,
        id_centro: 1, // Hospital San Vicente de Paul (por defecto)
        fecha: fecha_donacion, // Ya está en formato YYYY-MM-DD
        volumen_ml: volumen_total,
        estado: "Completada"
      };

      console.log('\n📤 PAYLOAD FINAL A ENVIAR:');
      console.log(JSON.stringify(payload, null, 2));

      // Verificar token
      const token = localStorage.getItem('token');
      if (!token) {
        alert('No hay token de autenticación. Por favor, inicie sesión.');
        window.location.href = 'login.html';
        return;
      }

      console.log(`Token encontrado: ${token.substring(0, 50)}...`);

      // Hacer la petición
      console.log('\n🌐 Enviando petición al servidor...');
      const API_URL = window.API || 'http://localhost:5000';
      const response = await fetch(`${API_URL}/api/donaciones/registrar`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      console.log(`\n📥 RESPUESTA DEL SERVIDOR:`);
      console.log(`Status: ${response.status} ${response.statusText}`);

      const responseText = await response.text();
      console.log(`Body (texto): "${responseText}"`);

      let data = {};
      try {
        data = JSON.parse(responseText);
        console.log(`Body (JSON):`, data);
      } catch (parseError) {
        console.error('❌ Error parseando JSON:', parseError);
        data = { error: responseText };
      }

      if (!response.ok) {
        let errorMessage = 'Error al registrar donación';
        
        if (response.status === 401) {
          errorMessage = 'Sesión expirada o token inválido. Redirigiendo al login...';
          console.log('❌ Token expirado, limpiando sesión...');
          localStorage.removeItem('token');
          localStorage.removeItem('access_token');
          localStorage.removeItem('usuario');
          // Redirección inmediata sin alert
          window.location.href = 'login.html';
          return;
        } else if (response.status === 403) {
          errorMessage = 'No tiene permisos para registrar donaciones.';
        } else if (response.status === 404) {
          errorMessage = 'El donante no existe en el sistema.';
        } else if (response.status === 500) {
          errorMessage = 'Error interno del servidor.';
          if (data.error) {
            errorMessage += `\n\nDetalle: ${data.error}`;
          }
        } else if (data.error) {
          errorMessage = data.error;
        } else if (data.message) {
          errorMessage = data.message;
        }
        
        throw new Error(`HTTP ${response.status} - ${errorMessage}`);
      }

      // Éxito
      console.log('\n✅ DONACIÓN REGISTRADA EXITOSAMENTE');
      alert(data.mensaje || 'Donación registrada correctamente');
      form.reset();

    } catch (err) {
      console.error('\n❌ ERROR COMPLETO:');
      console.error('Mensaje:', err.message);
      console.error('Stack:', err.stack);
      
      alert(`Error al registrar donación:\n\n${err.message}`);
    }
  });

  console.log("✅ Event listener del formulario de donación registrado correctamente");
});