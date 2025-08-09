from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from db_config import get_connection
import oracledb

inventario_bp = Blueprint('inventario', __name__)


@inventario_bp.route('/api/inventario', methods=['GET'])
@jwt_required()
def obtener_inventario():
    usuario_actual = get_jwt_identity()
    rol = usuario_actual.get('rol', '')
    if rol not in ['Diplomado', 'Microbiólogo', 'Jefatura', 'Admin BD']:
        return jsonify({'error': 'Acceso denegado'}), 403

    try:
        conn = get_connection()
        cursor = conn.cursor()

        salida = cursor.var(oracledb.CURSOR)
        cursor.callproc("PAQ_INVENTARIO.LISTAR_INVENTARIO", [salida])

        inventario = []
        for fila in salida.getvalue():
            inventario.append({
                'id_inventario': fila[0],
                'componente': fila[1],
                'tipo_sangre': fila[2],
                'unidades_disponibles': fila[3],
                'fecha_actualiza': str(fila[4]),
                'usuario_actualiza': fila[5]
            })

        return jsonify(inventario), 200
    except oracledb.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@inventario_bp.route('/api/inventario/entrada', methods=['POST'])
@jwt_required()
def registrar_entrada_inventario():
    data = request.json
    usuario_actual = get_jwt_identity()

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.callproc("PAQ_INVENTARIO.REGISTRAR_ENTRADA", [
            data['id_componente'],
            data['id_tipo_sangre'],
            data['unidades'],
            usuario_actual['usuario']
        ])
        conn.commit()
        return jsonify({'mensaje': 'Inventario actualizado exitosamente'}), 201
    except oracledb.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@inventario_bp.route('/api/inventario/total', methods=['GET'])
@jwt_required()
def total_por_componente_tipo():
    componente = request.args.get('id_componente')
    tipo = request.args.get('id_tipo_sangre')

    try:
        conn = get_connection()
        cursor = conn.cursor()
        total = cursor.callfunc(
            "PAQ_INVENTARIO.FN_TOTAL_UNIDADES_TIPO",
            oracledb.NUMBER,
            [componente, tipo]
        )
        return jsonify({'total_unidades': int(total)}), 200
    except oracledb.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()