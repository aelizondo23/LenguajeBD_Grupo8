from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
import oracledb as cx_Oracle
from db_config import get_connection

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    usuario = data.get("usuario") 
    contrasena = data.get("contrasena")

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Buscar el usuario
        cursor.execute("""
            SELECT id_usuario, nombre_usuario, contrasena, id_rol
            FROM usuario
            WHERE nombre_usuario = :1
        """, [usuario])

        result = cursor.fetchone()
        cursor.close()

        if not result:
            return jsonify({"error": "Usuario no encontrado"}), 401

        id_usuario, nombre_usuario, contrasena_bd, id_rol = result

        if contrasena != contrasena_bd:
            return jsonify({"error": "Contraseña incorrecta"}), 401

        # Obtener rol
        cursor = connection.cursor()
        cursor.execute("SELECT nombre_rol FROM rol WHERE id_rol = :1", [id_rol])
        rol_result = cursor.fetchone()
        cursor.close()

        rol = rol_result[0] if rol_result else "Sin rol"

        # Genera token
        token = create_access_token(identity={"id_usuario": id_usuario, "rol": rol})

        return jsonify({
            "token": token,
            "usuario": {
                "id_usuario": id_usuario,
                "nombre_usuario": nombre_usuario,
                "rol": rol
            }
        }), 200

    except cx_Oracle.Error as e:
        return jsonify({"error": str(e)}), 500

