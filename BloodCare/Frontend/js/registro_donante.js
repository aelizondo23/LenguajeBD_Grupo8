document.getElementById('form-donante').addEventListener('submit', function(e) {
  e.preventDefault();
  const datos = new FormData(this);
  const obj = {};
  datos.forEach((v, k) => obj[k] = v);
  fetch('/api/donantes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(obj)
  })
  .then(r => r.json())
  .then(data => { alert(data.mensaje || data.error); this.reset(); })
  .catch(err => alert("Error: " + err));
});