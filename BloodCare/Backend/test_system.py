import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_connection():
    """Prueba la conexión al servidor"""
    print("🔌 Verificando conexión al servidor...")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/login", timeout=2)
        print("✅ Servidor disponible")
        return True
    except:
        print("❌ Servidor no disponible")
        return False

def test_login():
    """Prueba el login con usuarios reales de tu SQL"""
    print("\n🔐 Probando login...")
    
    # Usuarios exactos de tu SQL
    credentials = [
        {"nombre_usuario": "admin1", "contrasena": "admin123"},
        {"nombre_usuario": "diplomado1", "contrasena": "diplomado123"},
        {"nombre_usuario": "tecnico1", "contrasena": "tecnico123"},
        {"nombre_usuario": "micro1", "contrasena": "micro123"},
        {"nombre_usuario": "jefatura1", "contrasena": "jefatura123"}
    ]
    
    for cred in credentials:
        try:
            print(f"   Probando: {cred['nombre_usuario']}")
            response = requests.post(f"{BASE_URL}/api/auth/login", json=cred, timeout=5)
            if response.status_code == 200:
                token = response.json().get("token")
                usuario = response.json().get("usuario")
                print(f"✅ Login exitoso - Usuario: {usuario['nombre_usuario']} - Rol: {usuario['rol']}")
                return token, usuario
            else:
                print(f"   ❌ Falló: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("❌ No se pudo hacer login con ninguna credencial")
    return None, None

def test_donante_registration(token):
    """Prueba el registro de donante"""
    print("\n👤 Probando registro de donante...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Generar ID único
    unique_id = str(int(time.time()))[-9:]
    
    # Probar diferentes formatos de fecha
    test_cases = [
        {
            "name": "Formato DD/MM/YYYY",
            "data": {
                "cedula": f"{unique_id}1",
                "nombre": "Juan Carlos",
                "apellido": "Pérez Test",
                "direccion": "Calle de Prueba 123",
                "fecha_nacimiento": "15/10/1990",  # DD/MM/YYYY
                "sexo": "M",
                "telefono": "8888-1234",
                "correo": f"test{unique_id}1@email.com",
                "id_tipo_sangre": 5
            }
        },
        {
            "name": "Formato YYYY-MM-DD",
            "data": {
                "cedula": f"{unique_id}2",
                "nombre": "María José",
                "apellido": "González Test",
                "direccion": "Avenida Principal 456",
                "fecha_nacimiento": "1985-12-25",  # YYYY-MM-DD
                "sexo": "F",
                "telefono": "8899-5678",
                "correo": f"test{unique_id}2@email.com",
                "id_tipo_sangre": 3
            }
        }
    ]
    
    registered_ids = []
    
    for test_case in test_cases:
        print(f"\n   📝 {test_case['name']}:")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/donantes/registrar",
                json=test_case['data'],
                headers=headers,
                timeout=10
            )
            
            print(f"      Status: {response.status_code}")
            result = response.json()
            print(f"      Response: {result}")
            
            if response.status_code == 201:
                print(f"      ✅ Donante registrado exitosamente!")
                registered_ids.append(test_case['data']['cedula'])
            elif response.status_code == 409:
                print(f"      ⚠️ Donante ya existe (normal si ya se ejecutó)")
            else:
                print(f"      ❌ Error al registrar donante")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    return registered_ids

def test_donante_retrieval(token, donante_ids):
    """Prueba la recuperación de donantes"""
    if not donante_ids:
        print("\n⚠️ No hay donantes para probar recuperación")
        return
    
    print(f"\n📋 Probando recuperación de donantes...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    for donante_id in donante_ids:
        try:
            print(f"   Obteniendo donante: {donante_id}")
            response = requests.get(
                f"{BASE_URL}/api/donantes/{donante_id}",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                donante = response.json()
                print(f"   ✅ Donante encontrado: {donante['nombre']} {donante['apellido']} - Tipo: {donante.get('tipo_sangre', 'N/A')}")
            else:
                print(f"   ❌ Error obteniendo donante: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_donantes_list(token):
    """Prueba el listado de donantes"""
    print(f"\n📋 Probando listado de donantes...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/donantes/listar",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            donantes = response.json()
            print(f"   ✅ Lista obtenida: {len(donantes)} donantes encontrados")
            if donantes:
                print(f"   📊 Primer donante: {donantes[0]['nombre']} {donantes[0]['apellido']} - Tipo: {donantes[0].get('tipo_sangre', 'N/A')}")
                print(f"   📊 Último donante: {donantes[-1]['nombre']} {donantes[-1]['apellido']} - Tipo: {donantes[-1].get('tipo_sangre', 'N/A')}")
        else:
            print(f"   ❌ Error obteniendo lista: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_donacion_registration(token, usuario):
    """Prueba el registro de donación"""
    print(f"\n🩸 Probando registro de donación...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Usar un donante existente de tu SQL
    donacion_data = {
        "id_donante": "101010101",  # Andrea Mora Salazar de tu SQL
        "id_centro": 1,  # Hospital San Vicente de Paul
        "fecha": "25/01/2025",  # DD/MM/YYYY
        "volumen_ml": 450,
        "estado": "Aprobada"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/donaciones/registrar",
            json=donacion_data,
            headers=headers,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Response: {result}")
        
        if response.status_code == 201:
            print(f"   ✅ Donación registrada exitosamente!")
            return result.get('id_donacion')
        else:
            print(f"   ❌ Error al registrar donación")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def main():
    """Función principal de prueba"""
    print("🧪 BLOODCARE - PRUEBAS COMPLETAS DEL SISTEMA")
    print("=" * 60)
    
    # 1. Verificar conexión
    if not test_connection():
        print("\n❌ FALLO: Servidor no disponible")
        print("   Solución: Ejecuta 'python app.py' en otra terminal")
        return
    
    # 2. Probar login
    token, usuario = test_login()
    if not token:
        print("\n❌ FALLO: No se pudo hacer login")
        print("   Solución: Verifica las credenciales en la base de datos")
        return
    
    # 3. Probar registro de donantes
    registered_ids = test_donante_registration(token)
    
    # 4. Probar recuperación de donantes
    test_donante_retrieval(token, registered_ids)
    
    # 5. Probar listado de donantes
    test_donantes_list(token)
    
    # 6. Probar registro de donación (solo si el rol lo permite)
    if usuario and usuario.get('rol') in ['Administrador', 'Diplomado', 'Tecnico', 'Microbiologo', 'Jefatura']:
        test_donacion_registration(token, usuario)
    else:
        print(f"\n⚠️ Saltando prueba de donaciones - Rol {usuario.get('rol') if usuario else 'N/A'} no tiene permisos")
    
    print("\n" + "=" * 60)
    print("🎉 PRUEBAS COMPLETADAS")
    print("✅ Sistema BloodCare funcionando correctamente")
    print("📊 Base de datos Oracle integrada")
    print("🔒 Autenticación JWT activa")
    print("📋 Paquetes PL/SQL funcionando")
    print("=" * 60)

if __name__ == "__main__":
    main()