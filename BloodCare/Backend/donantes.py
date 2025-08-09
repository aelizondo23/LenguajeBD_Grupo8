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


@donantes_bp.route('/api/donantes', methods=['GET'])
@jwt_required()
def listar_donantes():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        salida = cursor.var(oracledb.CURSOR)
        cursor.callproc("PAQ_DONANTE.LISTAR_DONANTES", [salida])
        donantes = []
        for fila in salida.getvalue():
            donantes.append({
                'id_donante': fila[0],
                'nombre': fila[1],
                'apellido': fila[2],
                'direccion': fila[3],
                'fecha_nacimiento': str(fila[4]),
                'sexo': fila[5],
                'telefono': fila[6],
                'correo': fila[7],
                'tipo_sangre': fila[8]
            })
        return jsonify(donantes), 200
    except oracledb.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@donantes_bp.route('/api/donantes/<id_donante>', methods=['GET'])
@jwt_required()
def obtener_donante(id_donante):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        salida = cursor.var(oracledb.CURSOR)
        cursor.callproc("PAQ_DONANTE.OBTENER_DONANTE", [id_donante, salida])
        fila = salida.getvalue().fetchone()
        if not fila:
            return jsonify({'error': 'Donante no encontrado'}), 404
        donante = {
            'id_donante': fila[0],
            'nombre': fila[1],
            'apellido': fila[2],
            'direccion': fila[3],
            'fecha_nacimiento': str(fila[4]),
            'sexo': fila[5],
            'telefono': fila[6],
            'correo': fila[7],
            'tipo_sangre': fila[8]
        }
        return jsonify(donante), 200
    except oracledb.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@donantes_bp.route('/api/donantes/<id_donante>', methods=['DELETE'])
@jwt_required()
def eliminar_donante(id_donante):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.callproc("PAQ_DONANTE.ELIMINAR_DONANTE", [id_donante])
        conn.commit()
        return jsonify({'mensaje': 'Donante eliminado'}), 200
    except oracledb.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@donantes_bp.route('/api/donantes/existe/<id_donante>', methods=['GET'])
@jwt_required()
def donante_existe(id_donante):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        resultado = cursor.callfunc("PAQ_DONANTE.FN_DONANTE_EXISTE", oracledb.NUMBER, [id_donante])
        existe = bool(resultado)
        return jsonify({'existe': existe}), 200
    except oracledb.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
