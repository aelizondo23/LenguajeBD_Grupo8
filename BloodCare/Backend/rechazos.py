from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db_config import get_connection
import oracledb

rechazos_bp = Blueprint('rechazos', __name__)

@rechazos_bp.route('/api/rechazos', methods=['POST'])
@jwt_required()
def registrar_rechazo():
    usuario_actual = get_jwt_identity()
    rol = usuario_actual['rol']
    if rol not in ['Diplomado', 'Microbiólogo', 'Jefatura', 'Admin BD']:
        return jsonify({'error': 'Acceso denegado'}), 403

    data = request.json
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.callproc("PAQ_RECHAZO.REGISTRAR_RECHAZO", [
            data['id_donacion'], data['id_causa'], data['observaciones'], data['usuario_registra']
        ])
        conn.commit()
        return jsonify({'mensaje': 'Rechazo registrado correctamente'}), 201
    except oracledb.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()