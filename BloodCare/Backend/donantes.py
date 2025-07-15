from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db_config import get_connection
import oracledb

donantes_bp = Blueprint('donantes', __name__)

@donantes_bp.route('/api/donantes', methods=['POST'])
@jwt_required()
def registrar_donante():
    usuario_actual = get_jwt_identity()
    rol = usuario_actual['rol']
    if rol not in ['Técnico', 'Diplomado', 'Microbiólogo', 'Jefatura', 'Admin BD']:
        return jsonify({'error': 'Acceso denegado: rol no autorizado'}), 403

    data = request.json
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.callproc("PAQ_DONANTE.REGISTRAR_DONANTE", [
            data['id_donante'], data['nombre'], data['apellido'],
            data['direccion'], data['fecha_nacimiento'], data['sexo'],
            data['telefono'], data['correo'], data['id_tipo_sangre']
        ])
        conn.commit()
        return jsonify({'mensaje': 'Donante registrado correctamente'}), 201
    except oracledb.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()