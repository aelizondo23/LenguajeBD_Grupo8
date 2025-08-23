from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
import oracledb
from database import get_connection

inventario_bp = Blueprint('inventario', __name__)

@inventario_bp.route('/listar', methods=['GET'])
@jwt_required()
def listar_inventario():
    """Lista los componentes sanguíneos con sus totales usando obtener_total_componentes"""
    print("📋 Listando inventario de componentes")
    try:
        conn = cursor = None
        conn = get_connection()
        cursor = conn.cursor()

        out_cursor = cursor.var(oracledb.CURSOR)

        cursor.callproc("obtener_total_componentes", [out_cursor])

        data = out_cursor.getvalue().fetchall()

        inventario = []
        for row in data:
            inventario.append({
                'id_componente': row[0],
                'componente': row[1],
                'total_unidades': row[2]
            })

        print(f"✅ {len(inventario)} registros de inventario encontrados")
        return jsonify(inventario), 200

    except Exception as e:
        print(f"❌ Error listando inventario: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
