from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
import oracledb
from database import get_connection

tipo_sangre_bp = Blueprint('tipo_sangre', __name__)

@tipo_sangre_bp.route('/listar', methods=['GET'])
@jwt_required()
def listar_tipos_sangre():
    """Lista todos los tipos de sangre disponibles"""
    print("📋 Listando tipos de sangre")
    
    try:
        conn = cursor = None
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id_tipo_sangre, tipo 
            FROM tipo_sangre 
            ORDER BY id_tipo_sangre
        """)
        
        data = cursor.fetchall()
        
        tipos_sangre = []
        for row in data:
            tipos_sangre.append({
                'id_tipo_sangre': row[0],
                'tipo': row[1]
            })
        
        print(f"✅ {len(tipos_sangre)} tipos de sangre encontrados")
        return jsonify(tipos_sangre), 200
        
    except Exception as e:
        print(f"❌ Error listando tipos de sangre: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()