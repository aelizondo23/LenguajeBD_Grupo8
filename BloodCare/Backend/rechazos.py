from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db_config import get_connection
import oracledb

rechazos_bp = Blueprint('rechazos', __name__)


@rechazos_bp.route('/api/rechazos', methods=['POST'])
@jwt_required()
def registrar_rechazo():
    usuario_actual = get_jwt_identity()
    rol = usuario_actual.get('rol', '')
    if rol not in ['Diplomado', 'Microbiólogo', 'Jefatura', 'Admin BD']:
        return jsonify({'error': 'Acceso denegado'}), 403

    data = request.json
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.callproc("PAQ_RECHAZO.REGISTRAR_RECHAZO", [
            data['id_donacion'], data['id_causa'], data.get('observaciones', ''), data['usuario_registra']
        ])
        conn.commit()
        return jsonify({'mensaje': 'Rechazo registrado correctamente'}), 201
    except oracledb.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@rechazos_bp.route('/api/rechazos', methods=['GET'])
@jwt_required()
def listar_rechazos():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        salida = cursor.var(oracledb.CURSOR)
        cursor.callproc("PAQ_RECHAZO.LISTAR_RECHAZOS", [salida])

        resultados = []
        for fila in salida.getvalue():
            resultados.append({
                'id_rechazo': fila[0],
                'id_donacion': fila[1],
                'causa': fila[2],
                'observaciones': fila[3],
                'usuario_registra': fila[4]
            })

        return jsonify(resultados), 200
    except oracledb.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@rechazos_bp.route('/api/rechazos/total', methods=['GET'])
@jwt_required()
def total_rechazos():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        total = cursor.callfunc("PAQ_RECHAZO.FN_TOTAL_RECHAZOS", oracledb.NUMBER)
        return jsonify({'total_rechazos': int(total)}), 200
    except oracledb.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
