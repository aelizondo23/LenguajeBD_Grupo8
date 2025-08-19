from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
import oracledb
from database import get_connection, get_cursor_data

admin_bp = Blueprint('admin', __name__)

def require_admin():
    """Decorador para verificar que el usuario sea administrador"""
    claims = get_jwt()
    rol = claims.get('rol', '')
    
    print(f"🔍 Verificando admin - Rol: {rol}")
    
    if rol != 'Administrador':
        print(f"❌ Acceso denegado para rol: {rol}")
        return jsonify({'error': 'Acceso denegado. Solo administradores.'}), 403
    
    print("✅ Usuario es administrador")
    return None

# ===== GESTIÓN DE USUARIOS =====

@admin_bp.route('/usuarios', methods=['GET'])
@jwt_required()
def listar_usuarios():
    """Lista todos los usuarios del sistema"""
    error = require_admin()
    if error:
        return error
    
    try:
        conn = cursor = None
        conn = get_connection()
        cursor = conn.cursor()
        
        # Usar el paquete PAQ_ADMIN
        out_cursor = cursor.var(oracledb.CURSOR)
        cursor.callproc("PAQ_ADMIN.LISTAR_USUARIOS", [out_cursor])
        
        data = out_cursor.getvalue().fetchall()
        usuarios = []
        for row in data:
            usuarios.append({
                'id_usuario': row[0],
                'nombre_usuario': row[1],
                'rol': row[2],
                'estado': row[3]
            })
        
        return jsonify(usuarios), 200
        
    except Exception as e:
        print(f"❌ Error listando usuarios: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@admin_bp.route('/usuarios', methods=['POST'])
@jwt_required()
def crear_usuario():
    """Crea un nuevo usuario"""
    error = require_admin()
    if error:
        return error
    
    try:
        data = request.get_json() or {}
        print(f"🔍 Datos recibidos para crear usuario: {data}")
        
        # Validar campos requeridos
        required_fields = ['nombre_usuario', 'contrasena', 'id_rol']
        for field in required_fields:
            if not data.get(field):
                print(f"❌ Campo faltante: {field}")
                return jsonify({'error': f'Campo {field} es requerido'}), 400
        
        # Validar y convertir id_rol
        try:
            id_rol = int(str(data['id_rol']).strip())
            if id_rol < 1 or id_rol > 5:
                print(f"❌ ID de rol inválido: {id_rol}")
                return jsonify({'error': 'ID de rol debe estar entre 1 y 5'}), 400
        except (ValueError, TypeError):
            print(f"❌ ID de rol no es numérico: {data['id_rol']}")
            return jsonify({'error': 'ID de rol debe ser un número válido'}), 400
        
        print(f"✅ ID de rol convertido: {id_rol} (tipo: {type(id_rol)})")
        
        conn = cursor = None
        conn = get_connection()
        cursor = conn.cursor()
        
        # Usar el paquete PAQ_ADMIN
        id_usuario_out = cursor.var(oracledb.NUMBER)
        
        print(f"📤 Llamando procedimiento con parámetros:")
        print(f"   nombre_usuario: '{data['nombre_usuario']}'")
        print(f"   contrasena: '{data['contrasena']}'")
        print(f"   id_rol: {id_rol}")
        print(f"   estado: '{data.get('estado', 'Activo')}'")
        
        cursor.callproc("PAQ_ADMIN.REGISTRAR_USUARIO", [
            data['nombre_usuario'],
            data['contrasena'],
            id_rol,
            data.get('estado', 'Activo'),
            id_usuario_out
        ])
        
        nuevo_id = int(id_usuario_out.getvalue())
        print(f"✅ Usuario creado con ID: {nuevo_id}")
        
        return jsonify({
            'mensaje': 'Usuario creado correctamente',
            'id_usuario': nuevo_id
        }), 201
        
    except oracledb.Error as oracle_error:
        if conn:
            conn.rollback()
        error_msg = str(oracle_error)
        print(f"❌ Error de Oracle creando usuario: {error_msg}")
        
        if "ORA-01722" in error_msg:
            return jsonify({'error': 'Error de formato de datos. Verifique que el rol sea un número válido.'}), 400
        elif "ORA-00001" in error_msg:
            return jsonify({'error': 'El nombre de usuario ya existe.'}), 409
        else:
            return jsonify({'error': f'Error de base de datos: {error_msg}'}), 500
            
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Error general creando usuario: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@admin_bp.route('/usuarios/<int:id_usuario>', methods=['PUT'])
@jwt_required()
def actualizar_usuario(id_usuario):
    """Actualiza un usuario existente"""
    error = require_admin()
    if error:
        return error
    
    try:
        data = request.get_json() or {}
        
        conn = cursor = None
        conn = get_connection()
        cursor = conn.cursor()
        
        # Usar el paquete PAQ_ADMIN
        cursor.callproc("PAQ_ADMIN.ACTUALIZAR_USUARIO", [
            id_usuario,
            data.get('nombre_usuario'),
            data.get('contrasena'),
            data.get('id_rol'),
            data.get('estado')
        ])
        
        return jsonify({'mensaje': 'Usuario actualizado correctamente'}), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Error actualizando usuario: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@admin_bp.route('/usuarios/<int:id_usuario>', methods=['DELETE'])
@jwt_required()
def eliminar_usuario(id_usuario):
    """Elimina un usuario (cambiar estado a Inactivo)"""
    error = require_admin()
    if error:
        return error
    
    try:
        conn = cursor = None
        conn = get_connection()
        cursor = conn.cursor()
        
        # Usar el paquete PAQ_ADMIN
        cursor.callproc("PAQ_ADMIN.ELIMINAR_USUARIO", [id_usuario])
        
        return jsonify({'mensaje': 'Usuario desactivado correctamente'}), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Error eliminando usuario: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ===== GESTIÓN DE CENTROS =====

@admin_bp.route('/centros', methods=['GET'])
@jwt_required()
def listar_centros():
    """Lista todos los centros de donación"""
    error = require_admin()
    if error:
        return error
    
    try:
        conn = cursor = None
        conn = get_connection()
        cursor = conn.cursor()
        
        # Usar el paquete PAQ_ADMIN
        out_cursor = cursor.var(oracledb.CURSOR)
        cursor.callproc("PAQ_ADMIN.LISTAR_CENTROS", [out_cursor])
        
        data = out_cursor.getvalue().fetchall()
        centros = []
        for row in data:
            centros.append({
                'id_centro': row[0],
                'nombre': row[1],
                'ubicacion': row[2],
                'tipo': row[3]
            })
        
        return jsonify(centros), 200
        
    except Exception as e:
        print(f"❌ Error listando centros: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@admin_bp.route('/centros', methods=['POST'])
@jwt_required()
def crear_centro():
    """Crea un nuevo centro de donación"""
    print("🏥 Solicitud para crear centro")
    
    error = require_admin()
    if error:
        return error
    
    try:
        data = request.get_json() or {}
        print(f"Datos recibidos: {data}")
        
        # Validar campos requeridos
        if not data.get('nombre'):
            print("❌ Nombre del centro es requerido")
            return jsonify({'error': 'El nombre del centro es requerido'}), 400
        
        conn = cursor = None
        conn = get_connection()
        cursor = conn.cursor()
        
        # Usar el paquete PAQ_ADMIN
        id_centro_out = cursor.var(oracledb.NUMBER)
        
        cursor.callproc("PAQ_ADMIN.REGISTRAR_CENTRO", [
            data['nombre'],
            data.get('direccion', ''),
            id_centro_out
        ])
        
        nuevo_id = int(id_centro_out.getvalue())
        print(f"✅ Centro creado con ID: {nuevo_id}")
        
        return jsonify({
            'mensaje': 'Centro creado correctamente',
            'id_centro': nuevo_id
        }), 201
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Error creando centro: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@admin_bp.route('/centros/<int:id_centro>', methods=['PUT'])
@jwt_required()
def actualizar_centro(id_centro):
    """Actualiza un centro de donación"""
    error = require_admin()
    if error:
        return error
    
    try:
        data = request.get_json() or {}
        
        conn = cursor = None
        conn = get_connection()
        cursor = conn.cursor()
        
        # Usar el paquete PAQ_ADMIN
        cursor.callproc("PAQ_ADMIN.ACTUALIZAR_CENTRO", [
            id_centro,
            data.get('nombre'),
            data.get('direccion')
        ])
        
        return jsonify({'mensaje': 'Centro actualizado correctamente'}), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Error actualizando centro: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@admin_bp.route('/centros/<int:id_centro>', methods=['DELETE'])
@jwt_required()
def eliminar_centro(id_centro):
    """Elimina un centro de donación"""
    error = require_admin()
    if error:
        return error
    
    try:
        conn = cursor = None
        conn = get_connection()
        cursor = conn.cursor()
        
        # Usar el paquete PAQ_ADMIN
        cursor.callproc("PAQ_ADMIN.ELIMINAR_CENTRO", [id_centro])
        
        return jsonify({'mensaje': 'Centro eliminado correctamente'}), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Error eliminando centro: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ===== ESTADÍSTICAS PARA ADMIN =====

@admin_bp.route('/estadisticas', methods=['GET'])
@jwt_required()
def obtener_estadisticas_admin():
    """Obtiene estadísticas generales para el panel de admin"""
    error = require_admin()
    if error:
        return error
    
    try:
        conn = cursor = None
        conn = get_connection()
        cursor = conn.cursor()
        
        # Usar el paquete PAQ_ADMIN
        out_cursor = cursor.var(oracledb.CURSOR)
        cursor.callproc("PAQ_ADMIN.OBTENER_ESTADISTICAS", [out_cursor])
        
        data = out_cursor.getvalue().fetchall()
        row = data[0] if data else [0, 0, 0, 0]
        
        estadisticas = {
            'total_usuarios': row[0],
            'total_centros': row[1],
            'total_donantes': row[2],
            'total_donaciones': row[3]
        }
        
        return jsonify(estadisticas), 200
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()