from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import oracledb as cx_Oracle
from db_config import get_connection

donaciones_bp = Blueprint("donaciones", __name__)


@donaciones_bp.route("/api/donaciones", methods=["GET"])
@jwt_required()
def listar_donaciones():
    try:
        connection = get_connection()
        cursor = connection.cursor()

        salida = cursor.var(cx_Oracle.CURSOR)
        cursor.callproc("PAQ_DONACION.LISTAR_DONACIONES", [salida])

        resultado = []
        for fila in salida.getvalue():
            resultado.append({
                "id_donacion": fila[0],
                "id_donante": fila[1],
                "fecha": str(fila[2]),
                "volumen_ml": fila[3],
                "estado": fila[4],
                "centro": fila[5]
            })

        return jsonify(resultado), 200

    except cx_Oracle.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


@donaciones_bp.route("/api/donaciones/registrar", methods=["POST"])
@jwt_required()
def registrar_donacion():
    try:
        data = request.json
        connection = get_connection()
        cursor = connection.cursor()

        # Llama a procedimiento SP_REGISTRAR_DONACION desde el paquete
        cursor.callproc("PAQ_DONACION.SP_REGISTRAR_DONACION", [
            data["id_donante"],
            data["id_centro"],
            data["fecha"],
            data["volumen_ml"],
            data["estado"],
            data["id_usuario_registra"]
        ])

        connection.commit()
        return jsonify({"mensaje": "Donación registrada correctamente"}), 201

    except cx_Oracle.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


@donaciones_bp.route("/api/donaciones/total", methods=["GET"])
@jwt_required()
def total_donaciones():
    try:
        connection = get_connection()
        cursor = connection.cursor()

        total = cursor.callfunc("PAQ_DONACION.FN_TOTAL_DONACIONES", cx_Oracle.NUMBER)
        return jsonify({"total_donaciones": int(total)}), 200

    except cx_Oracle.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()