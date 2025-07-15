from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db_config import get_connection

inventario_bp = Blueprint('inventario', __name__)

@inventario_bp.route('/api/inventario', methods=['GET'])
@jwt_required()
def obtener_inventario():
    usuario_actual = get_jwt_identity()
    rol = usuario_actual['rol']
    if rol not in ['Diplomado', 'Microbiólogo', 'Jefatura', 'Admin BD']:
        return jsonify({'error': 'Acceso denegado'}), 403

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM VISTA_INVENTARIO")  # Asegúrate de tener esta vista creada
        columnas = [col[0].lower() for col in cursor.description]
        resultados = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
        return jsonify(resultados)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()