(function () {
  const form = document.getElementById("loginForm") || document.querySelector("form");
  if (!form) return;
  const errorBox = document.getElementById("errorMessage");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const nombre_usuario = (document.getElementById("usuario") || {}).value?.trim();
    const contrasena = (document.getElementById("contrasena") || {}).value;

    if (errorBox) { errorBox.classList.add("d-none"); errorBox.textContent = ""; }

    try {
      const res = await fetch(`${API}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre_usuario, contrasena })
      });
      const data = await res.json();

      if (!res.ok) {
        const msg = data?.message || data?.error || "Usuario o contraseña inválidos";
        if (errorBox) { errorBox.textContent = msg; errorBox.classList.remove("d-none"); }
        else alert(msg);
        return;
      }
      // Guarda sesión y dirige al index
      saveSession(data);
      goHome();
    } catch (err) {
      console.error(err);
      const msg = "No se pudo conectar con el servidor.";
      if (errorBox) { errorBox.textContent = msg; errorBox.classList.remove("d-none"); }
      else alert(msg);
    }
  });
})();
