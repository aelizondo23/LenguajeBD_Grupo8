from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import oracledb
from db_config import get_connection

donantes_bp = Blueprint('donantes', __name__)

@donantes_bp.route('/api/donantes', methods=['POST'])
@jwt_required()
def registrar_donante():
    data = request.json
    usuario_actual = get_jwt_identity()
    id_usuario = usuario_actual['id_usuario']
    rol = usuario_actual['rol']

    # Verificación de roles permitidos
    roles_permitidos = ['Técnico', 'Diplomado', 'Microbiólogo', 'Jefatura', 'Admin BD']
    if rol not in roles_permitidos:
        return jsonify({'error': 'Acceso denegado: rol no autorizado'}), 403

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.callproc("PAQ_DONANTE.REGISTRAR_DONANTE", [
            data['id_donante'],
            data['nombre'],
            data['apellido'],
            data['direccion'],
            data['fecha_nacimiento'],
            data['sexo'],
            data['telefono'],
            data['correo'],
            data['id_tipo_sangre']
        ])

        connection.commit()
        return jsonify({'mensaje': 'Donante registrado correctamente'}), 201

    except oracledb.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()
