from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from datetime import timedelta
import oracledb
from database import get_connection
from config import Config

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    """Endpoint de login"""
    print("🔐 Intento de login recibido")
    
    data = request.get_json() or {}
    username = data.get("nombre_usuario") or data.get("usuario")
    password = data.get("contrasena") or data.get("password")

    print(f"Usuario: {username}")

    if not username or not password:
        print("❌ Faltan credenciales")
        return jsonify({"error": "Faltan credenciales"}), 400

    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verificar usuario usando la estructura exacta de tu SQL
        print("Verificando credenciales en la base de datos...")
        cursor.execute("""
            SELECT u.id_usuario, u.nombre_usuario, r.nombre_rol
            FROM usuario u
            JOIN rol r ON u.id_rol = r.id_rol
            WHERE u.nombre_usuario = :username 
            AND u.contrasena = :password
            AND u.estado = 'Activo'
        """, {"username": username, "password": password})
        
        user = cursor.fetchone()
        
        if not user:
            print("❌ Credenciales incorrectas o usuario inactivo")
            return jsonify({"error": "Credenciales incorrectas"}), 401

        print(f"✅ Usuario autenticado: {user[1]} - Rol: {user[2]}")

        # Crear token
        expires = timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)
        token = create_access_token(
            identity=str(user[0]),  # Usar el ID numérico como string
            additional_claims={
                "id_usuario": user[0],
                "nombre_usuario": user[1],
                "rol": user[2]
            },
            expires_delta=expires
        )

        return jsonify({
            "token": token,
            "usuario": {
                "id_usuario": user[0],
                "nombre_usuario": user[1],
                "rol": user[2]
            }
        }), 200

    except Exception as e:
        print(f"❌ Error en login: {e}")
        return jsonify({"error": f"Error interno: {str(e)}"}), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()