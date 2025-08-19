document.addEventListener("DOMContentLoaded", () => {
  console.log("🩸 BLOODCARE - Registro de Donante Iniciado");
  console.log("API URL:", window.API || "NO DEFINIDA");
  console.log("authFetch disponible:", typeof (window.authFetch || authFetch));
  console.log("Token actual:", localStorage.getItem('token') ? "PRESENTE" : "NO PRESENTE");

  // Proteger página y actualizar UI
  if (typeof protectPage === "function") {
    try {
      protectPage();
      console.log("✅ Página protegida correctamente");
    } catch (e) {
      console.error("❌ Error en protectPage:", e);
    }
  }
  
  if (typeof updateNavUI === "function") {
    updateNavUI();
  }

  // Buscar el formulario
  const form = document.getElementById('form-donante') ||
               document.getElementById('donanteForm') ||
               document.querySelector('form');
  
  if (!form) {
    console.error('❌ No se encontró el formulario de donante');
    return;
  }

  console.log('✅ Formulario encontrado:', form.id || 'sin ID');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    console.log('\n🚀 === INICIANDO REGISTRO DE DONANTE ===');
    
    const fd = new FormData(form);
    
    // Debug: mostrar todos los datos del formulario
    console.log('📋 Datos del formulario:');
    for (let [key, value] of fd.entries()) {
      console.log(`  ${key}: "${value}"`);
    }

    try {
      // 1. VALIDAR Y PROCESAR CÉDULA
      let id_donante = (fd.get('cedula') || fd.get('id_donante') || '')
        .toString().trim().replace(/\D/g, '');
      
      console.log(`🆔 Cédula procesada: "${id_donante}"`);
      
      if (id_donante.length < 8 || id_donante.length > 14) {
        throw new Error('La cédula debe tener entre 8 y 14 dígitos.');
      }

      // 2. VALIDAR Y PROCESAR FECHA
      let fecha_nacimiento = (fd.get('fecha_nacimiento') || '').toString().trim();
      console.log(`📅 Fecha original: "${fecha_nacimiento}"`);
      
      // Si viene en formato DD/MM/YYYY, convertir a YYYY-MM-DD
      if (fecha_nacimiento.includes('/')) {
        try {
          const [d, m, y] = fecha_nacimiento.split('/');
          fecha_nacimiento = `${y}-${m.padStart(2, '0')}-${d.padStart(2, '0')}`;
          console.log(`📅 Fecha convertida: "${fecha_nacimiento}"`);
        } catch {
          throw new Error('Formato de fecha inválido. Use DD/MM/AAAA o seleccione del calendario.');
        }
      }
      
      if (!/^\d{4}-\d{2}-\d{2}$/.test(fecha_nacimiento)) {
        throw new Error('Formato de fecha inválido. Debe ser YYYY-MM-DD.');
      }

      // 3. VALIDAR Y PROCESAR SEXO
      let sexo = (fd.get('sexo') || '').toString().trim().toUpperCase();
      console.log(`👤 Sexo original: "${fd.get('sexo')}" -> procesado: "${sexo}"`);
      
      if (sexo.startsWith('M') || sexo === 'MASCULINO') {
        sexo = 'M';
      } else if (sexo.startsWith('F') || sexo === 'FEMENINO') {
        sexo = 'F';
      } else {
        throw new Error(`Sexo inválido: "${sexo}". Debe ser Masculino o Femenino.`);
      }

      // 4. VALIDAR Y PROCESAR TIPO DE SANGRE
      let tipo_sangre_raw = (fd.get('tipo_sangre') || '').toString().trim();
      console.log(`🩸 Tipo de sangre raw: "${tipo_sangre_raw}"`);
      
      let id_tipo_sangre;
      
      // Si es un número directo (1-8)
      if (/^\d+$/.test(tipo_sangre_raw)) {
        id_tipo_sangre = parseInt(tipo_sangre_raw);
      } else {
        // Si es texto, mapear
        const mapTipo = {
          'A+': 1, 'A-': 2, 'B+': 3, 'B-': 4,
          'O+': 5, 'O-': 6, 'AB+': 7, 'AB-': 8
        };
        id_tipo_sangre = mapTipo[tipo_sangre_raw.toUpperCase()];
      }
      
      console.log(`🩸 ID tipo de sangre: ${id_tipo_sangre}`);
      
      if (!id_tipo_sangre || id_tipo_sangre < 1 || id_tipo_sangre > 8) {
        throw new Error(`Tipo de sangre inválido: "${tipo_sangre_raw}"`);
      }

      // 5. VALIDAR CAMPOS REQUERIDOS
      const nombre = (fd.get('nombre') || '').toString().trim();
      const apellido = (fd.get('apellido') || '').toString().trim();
      
      if (!nombre) throw new Error('El nombre es requerido');
      if (!apellido) throw new Error('El apellido es requerido');

      // 6. PREPARAR PAYLOAD FINAL
      const payload = {
        id_donante,
        cedula: id_donante,
        nombre,
        apellido,
        direccion: (fd.get('direccion') || '').toString().trim(),
        fecha_nacimiento,
        sexo,
        telefono: (fd.get('telefono') || '').toString().trim(),
        correo: (fd.get('correo') || '').toString().trim(),
        id_tipo_sangre
      };

      console.log('\n📤 PAYLOAD FINAL A ENVIAR:');
      console.log(JSON.stringify(payload, null, 2));

      // 7. VERIFICAR AUTENTICACIÓN
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No hay token de autenticación. Por favor, inicie sesión.');
      }

      // 8. HACER LA PETICIÓN
      console.log('\n🌐 Enviando petición al servidor...');
      
      const API_URL = window.API || 'http://localhost:5000';
      const url = `${API_URL}/api/donantes/registrar`;
      
      console.log(`URL: ${url}`);
      console.log(`Token: ${token.substring(0, 20)}...`);

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      console.log(`\n📥 RESPUESTA DEL SERVIDOR:`);
      console.log(`Status: ${response.status} ${response.statusText}`);
      console.log(`Headers:`, Object.fromEntries(response.headers.entries()));

      // 9. PROCESAR RESPUESTA
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
        let errorMessage = 'Error al registrar donante';
        
        if (response.status === 401) {
          errorMessage = 'Sesión expirada. Por favor, inicie sesión nuevamente.';
          localStorage.removeItem('token');
          setTimeout(() => window.location.href = 'login.html', 2000);
        } else if (response.status === 403) {
          errorMessage = 'No tiene permisos para registrar donantes.';
        } else if (response.status === 409) {
          errorMessage = 'El donante ya existe en el sistema.';
        } else if (response.status === 422) {
          errorMessage = 'Datos inválidos enviados al servidor.';
          if (data.error) {
            errorMessage += `\n\nDetalle: ${data.error}`;
          }
          if (data.detalles && Array.isArray(data.detalles)) {
            errorMessage += '\n\nErrores específicos:\n• ' + data.detalles.join('\n• ');
          }
        } else if (data.error) {
          errorMessage = data.error;
        } else if (data.message) {
          errorMessage = data.message;
        }
        
        throw new Error(`HTTP ${response.status} - ${errorMessage}`);
      }

      // 10. ÉXITO
      console.log('\n✅ DONANTE REGISTRADO EXITOSAMENTE');
      alert(data.mensaje || 'Donante registrado correctamente');
      form.reset();

    } catch (err) {
      console.error('\n❌ ERROR COMPLETO:');
      console.error('Mensaje:', err.message);
      console.error('Stack:', err.stack);
      
      alert(`Error al registrar donante:\n\n${err.message}`);
    }
  });

  console.log("✅ Event listener del formulario registrado correctamente");
});