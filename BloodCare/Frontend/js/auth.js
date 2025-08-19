const API = "http://localhost:5000";

function getToken() {
  return localStorage.getItem("token") || localStorage.getItem("access_token");
}

function isLoggedIn() { 
  return !!getToken(); 
}

function saveSession(data) {
  const tk = data?.token || data?.access_token;
  if (!tk) throw new Error("Backend no devolvió token");
  localStorage.setItem("token", tk);
  localStorage.setItem("access_token", tk); // compatibilidad
  if (data?.usuario) localStorage.setItem("usuario", JSON.stringify(data.usuario));
}

function clearSession() {
  localStorage.removeItem("token");
  localStorage.removeItem("access_token");
  localStorage.removeItem("usuario");
}

function goHome() { 
  window.location.href = "index.html"; 
}

// Proteger páginas
function protectPage() {
  console.log("🔍 === INICIANDO PROTECTPAGE ===");
  
  // Debug detallado del token
  const token = getToken();
  console.log("Token encontrado:", token ? `${token.substring(0, 50)}...` : "NO HAY TOKEN");
  
  // Verificar localStorage completo
  console.log("localStorage completo:");
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    const value = localStorage.getItem(key);
    console.log(`  ${key}: ${value ? value.substring(0, 100) + '...' : 'null'}`);
  }
  
  const loggedIn = isLoggedIn();
  console.log("isLoggedIn() resultado:", loggedIn);
  
  console.log("🔍 Ejecutando protectPage()...");
  
  
  console.log("🔍 Verificando autenticación...");
  
  if (!isLoggedIn()) {
    console.log("❌ No hay token válido, redirigiendo al login");
    alert("DEBUG: No hay token válido. ¿Hiciste login?");
    alert("No hay sesión activa. Redirigiendo al login...");
    window.location.href = "login.html";
    return false;
  }
  
  console.log("✅ Token válido, página protegida");
  console.log("🔍 === FIN PROTECTPAGE ===");
  return true;
  return true;
}

// ===== Fetch con Authorization =====
async function authFetch(url, options = {}) {
  const t = getToken();
  const headers = new Headers(options.headers || {});
  if (t) headers.set("Authorization", `Bearer ${t}`);
  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }
  
  const res = await fetch(url, { ...options, headers });
  
  if (res.status === 401) {
    alert("Sesión expirada. Vuelve a iniciar sesión.");
    clearSession(); 
    window.location.href = "login.html";
    throw new Error("401 Unauthorized");
  }
  return res;
}

// Navbar: mostrar/ocultar Login/Logout
function updateNavUI() {
  const loginLink = document.getElementById("nav-login") || document.querySelector('a[href="login.html"]');
  const logoutBtn = document.getElementById("logoutBtn") || document.getElementById("nav-logout");
  const adminLink = document.getElementById("nav-admin");
  
  // Obtener usuario actual
  const usuario = JSON.parse(localStorage.getItem("usuario") || "{}");
  
  if (isLoggedIn()) {
    if (loginLink) loginLink.classList.add("d-none");
    if (logoutBtn) logoutBtn.classList.remove("d-none");
    
    // Mostrar panel admin solo para administradores
    if (adminLink && usuario.rol === "Administrador") {
      adminLink.classList.remove("d-none");
    }
  } else {
    if (loginLink) loginLink.classList.remove("d-none");
    if (logoutBtn) logoutBtn.classList.add("d-none");
    if (adminLink) adminLink.classList.add("d-none");
  }
}

// Páginas protegidas (desde la navbar)
const PROTECTED_PAGES = new Set([
  "interfaz_rol.html", "registro_donante.html", "registro_donacion.html",
  "registro_rechazo.html", "inventario.html", "estadisticas.html", "bitacora.html"
]);

function guardNavLinks() {
  document.addEventListener("click", (e) => {
    const a = e.target.closest("a.nav-link");
    if (!a) return;
    const href = a.getAttribute("href");
    if (!href) return;
    if (href.startsWith("http") || href.startsWith("#") || href === "login.html" || href === "index.html") return;
    if (PROTECTED_PAGES.has(href) && !isLoggedIn()) {
      e.preventDefault();
      alert("Inicia sesión para continuar.");
      window.location.href = "login.html";
    }
  });
}

// Eventos globales
document.addEventListener("DOMContentLoaded", () => {
  updateNavUI();
  guardNavLinks();
  const btn = document.getElementById("logoutBtn") || document.getElementById("nav-logout");
  if (btn) {
    btn.addEventListener("click", (e) => { 
      e.preventDefault(); 
      clearSession(); 
      goHome(); 
    });
  }
});

window.addEventListener("storage", (e) => {
  if (e.key === "token" || e.key === "access_token" || e.key === "usuario") {
    updateNavUI();
  }
});

// Exponer funciones globalmente
window.API = API;
window.getToken = getToken;
window.saveSession = saveSession;
window.clearSession = clearSession;
window.isLoggedIn = isLoggedIn;
window.protectPage = protectPage;
window.authFetch = authFetch;
window.goHome = goHome;
window.updateNavUI = updateNavUI;

// Alias de compatibilidad
window.requireAuth = protectPage;
window.wireNavbar = updateNavUI;