from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
import oracledb
from database import get_connection

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
        
        cursor.execute("""
            SELECT u.id_usuario, u.nombre_usuario, r.nombre_rol, u.estado
            FROM usuario u
            JOIN rol r ON u.id_rol = r.id_rol
            ORDER BY u.id_usuario
        """)
        
        usuarios = []
        for row in cursor.fetchall():
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
        
        # Validar campos requeridos
        required_fields = ['nombre_usuario', 'contrasena', 'id_rol']
        for field in required_fields:
            if not data.get(field):
                print(f"❌ Campo faltante: {field}")
                return jsonify({'error': f'Campo {field} es requerido'}), 400
        
        # Validar y convertir id_rol
        try:
            id_rol = int(data['id_rol'])
            if id_rol < 1 or id_rol > 5:
                print(f"❌ ID de rol inválido: {id_rol}")
                return jsonify({'error': 'ID de rol debe estar entre 1 y 5'}), 400
            data['id_rol'] = id_rol
        except (ValueError, TypeError):
            print(f"❌ ID de rol no es numérico: {data['id_rol']}")
            return jsonify({'error': 'ID de rol debe ser un número válido'}), 400
        
        conn = cursor = None
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verificar que el usuario no exista
        cursor.execute("SELECT COUNT(*) FROM usuario WHERE nombre_usuario = ?", [data['nombre_usuario']])
        if cursor.fetchone()[0] > 0:
            print(f"❌ Usuario ya existe: {data['nombre_usuario']}")
            return jsonify({'error': 'El usuario ya existe'}), 409
        
        # Obtener el próximo ID
        cursor.execute("SELECT NVL(MAX(id_usuario), 0) + 1 FROM usuario")
        nuevo_id = cursor.fetchone()[0]
        
        # Insertar usuario
        cursor.execute("""
            INSERT INTO usuario (id_usuario, nombre_usuario, contrasena, id_rol, estado)
            VALUES (?, ?, ?, ?, ?)
        """, [
            nuevo_id,
            data['nombre_usuario'],
            data['contrasena'],
            int(data['id_rol']),
            data.get('estado', 'Activo')
        ])
        
        conn.commit()
        
        return jsonify({
            'mensaje': 'Usuario creado correctamente',
            'id_usuario': nuevo_id
        }), 201
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Error creando usuario: {e}")
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
        
        # Construir query dinámicamente
        updates = []
        params = []
        
        if data.get('nombre_usuario'):
            updates.append("nombre_usuario = :1")
            params.append(data['nombre_usuario'])
        
        if data.get('contrasena'):
            updates.append(f"contrasena = :{len(params) + 1}")
            params.append(data['contrasena'])
        
        if data.get('id_rol'):
            updates.append(f"id_rol = :{len(params) + 1}")
            params.append(data['id_rol'])
        
        if data.get('estado'):
            updates.append(f"estado = :{len(params) + 1}")
            params.append(data['estado'])
        
        if not updates:
            return jsonify({'error': 'No hay campos para actualizar'}), 400
        
        params.append(id_usuario)
        query = f"UPDATE usuario SET {', '.join(updates)} WHERE id_usuario = :{len(params)}"
        
        cursor.execute(query, params)
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        conn.commit()
        
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
        
        # No eliminar físicamente, solo cambiar estado
        cursor.execute("UPDATE usuario SET estado = 'Inactivo' WHERE id_usuario = :1", [id_usuario])
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        conn.commit()
        
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
        
        cursor.execute("SELECT id_centro, nombre, direccion, telefono FROM centro_donacion ORDER BY id_centro")
        
        centros = []
        for row in cursor.fetchall():
            centros.append({
                'id_centro': row[0],
                'nombre': row[1],
                'direccion': row[2],
                'telefono': row[3]
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
        
        # Obtener el próximo ID
        cursor.execute("SELECT NVL(MAX(id_centro), 0) + 1 FROM centro_donacion")
        nuevo_id = cursor.fetchone()[0]
        print(f"Nuevo ID de centro: {nuevo_id}")
        
        # Insertar centro
        cursor.execute("""
            INSERT INTO centro_donacion (id_centro, nombre, direccion, telefono)
            VALUES (:1, :2, :3, :4)
        """, [
            nuevo_id,
            data['nombre'],
            data.get('direccion', ''),
            data.get('telefono', '')
        ])
        
        conn.commit()
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
        
        # Construir query dinámicamente
        updates = []
        params = []
        
        if data.get('nombre'):
            updates.append("nombre = :1")
            params.append(data['nombre'])
        
        if 'direccion' in data:
            updates.append(f"direccion = :{len(params) + 1}")
            params.append(data['direccion'])
        
        if 'telefono' in data:
            updates.append(f"telefono = :{len(params) + 1}")
            params.append(data['telefono'])
        
        if not updates:
            return jsonify({'error': 'No hay campos para actualizar'}), 400
        
        params.append(id_centro)
        query = f"UPDATE centro_donacion SET {', '.join(updates)} WHERE id_centro = :{len(params)}"
        
        cursor.execute(query, params)
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Centro no encontrado'}), 404
        
        conn.commit()
        
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
        
        # Verificar que no tenga donaciones asociadas
        cursor.execute("SELECT COUNT(*) FROM donacion WHERE id_centro = :1", [id_centro])
        if cursor.fetchone()[0] > 0:
            return jsonify({'error': 'No se puede eliminar el centro porque tiene donaciones asociadas'}), 409
        
        cursor.execute("DELETE FROM centro_donacion WHERE id_centro = :1", [id_centro])
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Centro no encontrado'}), 404
        
        conn.commit()
        
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
        
        # Contar usuarios activos
        cursor.execute("SELECT COUNT(*) FROM usuario WHERE estado = 'Activo'")
        total_usuarios = cursor.fetchone()[0]
        
        # Contar centros
        cursor.execute("SELECT COUNT(*) FROM centro_donacion")
        total_centros = cursor.fetchone()[0]
        
        # Contar donantes
        cursor.execute("SELECT COUNT(*) FROM donante")
        total_donantes = cursor.fetchone()[0]
        
        # Contar donaciones
        cursor.execute("SELECT COUNT(*) FROM donacion")
        total_donaciones = cursor.fetchone()[0]
        
        estadisticas = {
            'total_usuarios': total_usuarios,
            'total_centros': total_centros,
            'total_donantes': total_donantes,
            'total_donaciones': total_donaciones
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