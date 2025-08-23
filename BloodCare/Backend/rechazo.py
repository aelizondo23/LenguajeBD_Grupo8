from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
import oracledb
from database import get_connection

rechazo_bp = Blueprint('rechazo', __name__)

def validate_rechazo_data(data):
    """Valida y normaliza los datos del rechazo"""
    errors = []
    
    # Campos requeridos
    if not data.get('id_donacion'):
        errors.append("Campo id_donacion es requerido")
    if not data.get('id_causa'):
        errors.append("Campo id_causa es requerido")
    
    # Validar que sean numéricos
    if data.get('id_donacion'):
        try:
            data['id_donacion'] = int(data['id_donacion'])
        except ValueError:
            errors.append("ID de donación debe ser numérico")
    
    if data.get('id_causa'):
        try:
            data['id_causa'] = int(data['id_causa'])
        except ValueError:
            errors.append("ID de causa debe ser numérico")
    
    # Campo opcional
    data['observaciones'] = data.get('observaciones', '') or ''
    
    return data, errors


@rechazo_bp.route('/registrar', methods=['POST'])
@jwt_required()
def registrar_rechazo():
    """Registra un nuevo rechazo"""
    try:
        # Verificar permisos
        claims = get_jwt()
        rol = claims.get('rol', '')
        id_usuario = claims.get('id_usuario', get_jwt_identity())
        
        roles_permitidos = ['Administrador', 'Diplomado', 'Tecnico', 'Microbiologo', 'Jefatura']
        if rol not in roles_permitidos:
            return jsonify({'error': 'Acceso denegado'}), 403
        
        # Validar datos
        data = request.get_json() or {}
        data, errors = validate_rechazo_data(data)
        
        if errors:
            return jsonify({'error': 'Datos inválidos', 'detalles': errors}), 400
        
        # Registrar rechazo
        conn = cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.callproc("registrar_rechazo", [
                data['id_donacion'],
                data['id_causa'],
                data['observaciones'],
                str(id_usuario)
            ])
            
            conn.commit()
            return jsonify({'mensaje': 'Rechazo registrado correctamente'}), 201
            
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500


@rechazo_bp.route('/<int:id_rechazo>', methods=['GET'])
@jwt_required()
def obtener_rechazo(id_rechazo):
    """Obtiene un rechazo por ID"""
    try:
        conn = cursor = None
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT r.id_rechazo, r.id_donacion, r.id_causa, r.observaciones, 
               r.usuario_registra, cr.descripcion as causa_descripcion
        FROM rechazo r
        JOIN causa_rechazo cr ON r.id_causa = cr.id_causa
        WHERE r.id_rechazo = :1
        """
        
        cursor.execute(query, [id_rechazo])
        row = cursor.fetchone()
        
        if not row:
            return jsonify({'error': 'Rechazo no encontrado'}), 404
        
        rechazo = {
            'id_rechazo': row[0],
            'id_donacion': row[1],
            'id_causa': row[2],
            'observaciones': row[3],
            'usuario_registra': row[4],
            'causa_descripcion': row[5]
        }
        
        return jsonify(rechazo), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@rechazo_bp.route('/listar', methods=['GET'])
@jwt_required()
def listar_rechazos():
    """Lista todos los rechazos"""
    try:
        conn = cursor = None
        conn = get_connection()
        cursor = conn.cursor()
        
        resultado_cursor = cursor.var(oracledb.CURSOR)
        cursor.callproc("listar_rechazos", [resultado_cursor])
        data_cursor = resultado_cursor.getvalue()
        data = data_cursor.fetchall()
        data_cursor.close()
        
        rechazos = []
        for row in data:
            rechazos.append({
                'id_rechazo': row[0],
                'id_donacion': row[1],
                'id_causa': row[2],
                'observaciones': row[3],
                'usuario_registra': row[4],
                'causa_descripcion': row[5]
            })
        
        return jsonify(rechazos), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@rechazo_bp.route('/<int:id_rechazo>', methods=['PUT'])
@jwt_required()
def actualizar_rechazo(id_rechazo):
    """Actualiza un rechazo"""
    try:
        # Verificar permisos
        claims = get_jwt()
        rol = claims.get('rol', '')
        
        roles_permitidos = ['Administrador', 'Diplomado', 'Microbiologo', 'Jefatura']
        if rol not in roles_permitidos:
            return jsonify({'error': 'Acceso denegado'}), 403
        
        # Validar datos
        data = request.get_json() or {}
        if not data.get('id_causa'):
            return jsonify({'error': 'ID de causa es requerido'}), 400
        
        try:
            id_causa = int(data['id_causa'])
        except ValueError:
            return jsonify({'error': 'ID de causa debe ser numérico'}), 400
        
        observaciones = data.get('observaciones', '') or ''
        
        # Actualizar rechazo
        conn = cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.callproc("actualizar_rechazo", [
                id_rechazo,
                data['id_donacion'],
                id_causa,
                observaciones,
                str(claims.get('id_usuario', get_jwt_identity()))
            ])
            
            conn.commit()
            return jsonify({'mensaje': 'Rechazo actualizado correctamente'}), 200
            
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500


@rechazo_bp.route('/<int:id_rechazo>', methods=['DELETE'])
@jwt_required()
def eliminar_rechazo(id_rechazo):
    """Elimina un rechazo"""
    try:
        # Verificar permisos
        claims = get_jwt()
        rol = claims.get('rol', '')
        
        roles_permitidos = ['Administrador', 'Jefatura']
        if rol not in roles_permitidos:
            return jsonify({'error': 'Acceso denegado'}), 403
        
        # Eliminar rechazo usando procedimiento almacenado
        conn = cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Variable para recibir las filas afectadas
            filas_afectadas = cursor.var(int)
            
            # Llamar al procedimiento
            cursor.callproc("eliminar_rechazo", [id_rechazo, filas_afectadas])
            
            # Verificar si se eliminó algo
            if filas_afectadas.getvalue() == 0:
                return jsonify({'error': 'Rechazo no encontrado'}), 404
            
            conn.commit()
            return jsonify({'mensaje': 'Rechazo eliminado correctamente'}), 200
            
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500