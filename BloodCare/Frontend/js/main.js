function cargarDonaciones() {
  fetch("http://127.0.0.1:5000/api/donaciones/")
    .then(res => res.json())
    .then(data => {
      const lista = document.getElementById("lista-donaciones");
      lista.innerHTML = "";
      data.forEach(d => {
        const li = document.createElement("li");
        li.textContent = `ID: ${d.id} | Fecha: ${d.fecha} | Volumen: ${d.volumen} ml | Estado: ${d.estado}`;
        lista.appendChild(li);
      });
    });
}
