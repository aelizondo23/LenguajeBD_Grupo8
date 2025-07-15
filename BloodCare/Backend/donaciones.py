from flask import Blueprint, jsonify
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

