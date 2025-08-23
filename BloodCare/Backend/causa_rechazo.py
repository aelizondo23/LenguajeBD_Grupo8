# archivo_causa_rechazo.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from database import get_connection

causa_rechazo_bp = Blueprint('causa_rechazo', __name__)

@causa_rechazo_bp.route('/listar', methods=['GET'])
@jwt_required()
def listar_causas_rechazo():
    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT id_causa, descripcion
            FROM causa_rechazo
            ORDER BY id_causa
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        causas = []
        for row in rows:
            causas.append({
                'id_causa': row[0],
                'descripcion': row[1]
            })

        return jsonify(causas), 200

    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
