document.addEventListener("DOMContentLoaded", () => {
  console.log("❌ BLOODCARE - Registro de Rechazo Iniciado");
  
  // Proteger página y actualizar UI
  if (typeof protectPage === "function") {
    try {
      protectPage();
      console.log("✅ Página protegida correctamente");
    } catch (e) {
      console.error("❌ Error en protectPage:", e);
      return;
    }
  }
  
  if (typeof updateNavUI === "function") {
    updateNavUI();
  }

  // Buscar el formulario
  const form = document.getElementById("form-rechazo") ||
               document.getElementById("rechazoForm") ||
               document.querySelector("form");
  
  if (!form) {
    console.error('❌ No se encontró el formulario de rechazo');
    return;
  }

  console.log('✅ Formulario de rechazo encontrado:', form.id || 'sin ID');

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    console.log('\n🚀 === INICIANDO REGISTRO DE RECHAZO ===');

    const fd = new FormData(form);
    
    // Debug: mostrar todos los datos del formulario
    console.log('📋 Datos del formulario:');
    for (let [key, value] of fd.entries()) {
      console.log(`  ${key}: "${value}"`);
    }

    try {
      // Obtener datos del formulario
      const id_donacion = Number(fd.get('id_donacion') || fd.get('rec_id_donacion') || 0);
      const id_causa = Number(fd.get('id_causa') || fd.get('rec_id_causa') || 0);
      const observaciones = (fd.get('observaciones') || fd.get('rec_observaciones') || '').toString().trim();

      console.log(`📋 Datos procesados:`);
      console.log(`  ID Donación: ${id_donacion}`);
      console.log(`  ID Causa: ${id_causa}`);
      console.log(`  Observaciones: "${observaciones}"`);

      // Validaciones
      if (!id_donacion || id_donacion <= 0) {
        throw new Error("Debe indicar un ID de donación válido");
      }
      if (!id_causa || id_causa <= 0) {
        throw new Error("Debe seleccionar una causa de rechazo válida");
      }

      // Preparar payload
      const payload = {
        id_donacion,
        id_causa,
        observaciones
      };

      console.log('\n📤 PAYLOAD FINAL A ENVIAR:');
      console.log(JSON.stringify(payload, null, 2));

      // Verificar token
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No hay token de autenticación. Por favor, inicie sesión.');
      }

      // Hacer la petición
      console.log('\n🌐 Enviando petición al servidor...');
      const response = await fetch(`${API}/api/rechazos/registrar`, {
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
        let errorMessage = 'Error al registrar rechazo';
        
        if (response.status === 401) {
          errorMessage = 'Sesión expirada. Por favor, inicie sesión nuevamente.';
          localStorage.removeItem('token');
          setTimeout(() => window.location.href = 'login.html', 2000);
        } else if (response.status === 403) {
          errorMessage = 'No tiene permisos para registrar rechazos.';
        } else if (response.status === 404) {
          errorMessage = 'La donación especificada no existe.';
        } else if (data.error) {
          errorMessage = data.error;
        } else if (data.message) {
          errorMessage = data.message;
        }
        
        throw new Error(`HTTP ${response.status} - ${errorMessage}`);
      }

      // Éxito
      console.log('\n✅ RECHAZO REGISTRADO EXITOSAMENTE');
      alert(data.mensaje || 'Rechazo registrado correctamente');
      form.reset();

    } catch (err) {
      console.error('\n❌ ERROR COMPLETO:');
      console.error('Mensaje:', err.message);
      console.error('Stack:', err.stack);
      
      alert(`Error al registrar rechazo:\n\n${err.message}`);
    }
  });

  console.log("✅ Event listener del formulario de rechazo registrado correctamente");
});