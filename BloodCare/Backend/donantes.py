from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import oracledb
from database import get_connection, execute_procedure, execute_function, get_cursor_data

donantes_bp = Blueprint('donantes', __name__)

def validate_donante_data(data):
    """Valida y normaliza los datos del donante"""
    print("🔍 Validando datos del donante...")
    print(f"Datos recibidos: {data}")
    
    errors = []
    
    # Campos requeridos
    required_fields = ['nombre', 'apellido', 'fecha_nacimiento', 'sexo', 'id_tipo_sangre', 'id_centro']
    for field in required_fields:
        if not data.get(field):
            errors.append(f"Campo {field} es requerido")
    
    # Validar cédula/id_donante
    cedula = data.get('cedula') or data.get('id_donante')
    if not cedula:
        errors.append("Cédula es requerida")
    else:
        data['id_donante'] = str(cedula).strip()
        print(f"ID Donante: {data['id_donante']}")
    
    # Validar fecha - ACEPTA MÚLTIPLES FORMATOS
    if data.get('fecha_nacimiento'):
        try:
            fecha_str = str(data['fecha_nacimiento']).strip()
            print(f"Fecha recibida: {fecha_str}")
            
            if '/' in fecha_str:  # DD/MM/YYYY
                parts = fecha_str.split('/')
                if len(parts) == 3:
                    day, month, year = parts
                    fecha_obj = datetime(int(year), int(month), int(day))
                    print(f"Fecha convertida desde DD/MM/YYYY: {fecha_obj}")
            elif '-' in fecha_str and len(fecha_str.split('-')[0]) <= 2:  # DD-MM-YYYY
                parts = fecha_str.split('-')
                if len(parts) == 3:
                    day, month, year = parts
                    fecha_obj = datetime(int(year), int(month), int(day))
                    print(f"Fecha convertida desde DD-MM-YYYY: {fecha_obj}")
            else:  # YYYY-MM-DD
                fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
                print(f"Fecha en formato YYYY-MM-DD: {fecha_obj}")
            
            # Convertir a DATE de Oracle
            data['fecha_nacimiento'] = fecha_obj
            print(f"Fecha final: {data['fecha_nacimiento']}")
            
        except Exception as e:
            print(f"❌ Error procesando fecha: {e}")
            errors.append("Formato de fecha inválido")
    
    # Validar sexo
    if data.get('sexo'):
        sexo = str(data['sexo']).upper().strip()
        print(f"Sexo recibido: '{data['sexo']}' -> procesado: '{sexo}'")
        if sexo.startswith('M'):
            data['sexo'] = 'M'
        elif sexo.startswith('F'):
            data['sexo'] = 'F'
        else:
            errors.append(f"Sexo inválido: '{sexo}'. Debe ser M o F")
        print(f"Sexo: {data['sexo']}")
    else:
        errors.append("Campo sexo es requerido")
    
    # Validar tipo de sangre (1-8 según tu SQL)
    if data.get('id_tipo_sangre'):
        try:
            tipo_sangre = int(data['id_tipo_sangre'])
            if tipo_sangre < 1 or tipo_sangre > 8:
                errors.append("Tipo de sangre debe estar entre 1 y 8")
            data['id_tipo_sangre'] = tipo_sangre
            print(f"Tipo de sangre: {data['id_tipo_sangre']}")
        except ValueError:
            errors.append("Tipo de sangre debe ser numérico")
    else:
        errors.append("Campo tipo de sangre es requerido")
    
    # Campos opcionales con valores por defecto
    data['direccion'] = data.get('direccion', '') or ''
    data['telefono'] = data.get('telefono', '') or ''
    data['correo'] = data.get('correo', '') or ''
    
    # Validar centro de donación (ahora opcional, se usa el configurado)
    if data.get('id_centro'):
        try:
            centro = int(data['id_centro'])
            if centro < 1 or centro > 3:
                errors.append("Centro de donación debe estar entre 1 y 3")
            data['id_centro'] = centro
            print(f"Centro de donación: {data['id_centro']}")
        except ValueError:
            errors.append("Centro de donación debe ser numérico")
    else:
        # Si no se especifica centro, usar el por defecto (1)
        data['id_centro'] = 1
        print(f"Centro de donación por defecto: {data['id_centro']}")
    
    if errors:
        print(f"❌ Errores de validación: {errors}")
    else:
        print("✅ Datos validados correctamente")
    
    return data, errors

@donantes_bp.route('/registrar', methods=['POST'])
@jwt_required()
def registrar_donante():
    """Registra un nuevo donante usando PAQ_DONANTE.REGISTRAR_DONANTE"""
    print("👤 Solicitud de registro de donante recibida")
    
    try:
        # Verificar permisos según tu SQL
        usuario = get_jwt_identity()
        
        # Obtener claims adicionales
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        
        rol = claims.get('rol', '')
        nombre_usuario = claims.get('nombre_usuario', '')
        id_usuario = claims.get('id_usuario', usuario)
        
        print(f"Usuario ID: {usuario}")
        print(f"Usuario: {nombre_usuario} - Rol: {rol}")
        
        # Roles que pueden registrar donantes según tu estructura
        roles_permitidos = ['Administrador', 'Diplomado', 'Tecnico', 'Microbiologo', 'Jefatura']
        
        if rol not in roles_permitidos:
            print(f"❌ Acceso denegado para rol: {rol}")
            return jsonify({'error': 'Acceso denegado'}), 403
        
        # Obtener y validar datos
        data = request.get_json() or {}
        data, errors = validate_donante_data(data)
        
        if errors:
            return jsonify({
                'error': 'Datos inválidos',
                'detalles': errors
            }), 400
        
        # Verificar si el donante ya existe usando la función del paquete
        print("Verificando si el donante ya existe...")
        try:
            existe = execute_function(
                "PAQ_DONANTE.FN_DONANTE_EXISTE", 
                oracledb.NUMBER, 
                [data['id_donante']]
            )
            if int(existe) == 1:
                print("❌ El donante ya existe")
                return jsonify({'error': 'El donante ya existe'}), 409
        except Exception as e:
            print(f"⚠️ No se pudo verificar existencia: {e}")
        
        # Registrar donante usando el paquete PAQ_DONANTE
        print("Registrando donante usando PAQ_DONANTE.REGISTRAR_DONANTE...")
        
        conn = cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Llamar al procedimiento del paquete
            cursor.callproc("PAQ_DONANTE.REGISTRAR_DONANTE", [
                data['id_donante'],
                data['nombre'],
                data['apellido'],
                data['direccion'],
                data['fecha_nacimiento'],
                data['sexo'],
                data['telefono'],
                data['correo'],
                data['id_tipo_sangre']
            ])
            
            conn.commit()
            
            # Registrar automáticamente una donación inicial en el centro seleccionado
            print(f"Registrando donación inicial en centro {data['id_centro']}...")
            
            # Obtener usuario actual para la donación
            from flask_jwt_extended import get_jwt
            claims = get_jwt()
            id_usuario = claims.get('id_usuario', 1)
            
            # Variable para capturar el ID de la donación
            id_donacion_out = cursor.var(oracledb.NUMBER)
            
            # Registrar donación inicial con volumen 0 (solo registro)
            cursor.callproc("pkg_donacion.registrar_donacion", [
                data['id_donante'],
                data['id_centro'],
                data['fecha_nacimiento'],  # Usar fecha de nacimiento como fecha de registro
                0,  # Volumen 0 (solo registro inicial)
                'Registrado',  # Estado inicial
                id_usuario,
                id_donacion_out
            ])
            
            conn.commit()
            nuevo_id_donacion = int(id_donacion_out.getvalue())
            
            print(f"✅ Donante registrado correctamente con donación inicial ID: {nuevo_id_donacion}")
            return jsonify({
                'mensaje': 'Donante registrado correctamente en el centro seleccionado',
                'id_donacion_inicial': nuevo_id_donacion
            }), 201
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        
    except Exception as e:
        print(f"❌ Error registrando donante: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

@donantes_bp.route('/<id_donante>', methods=['GET'])
@jwt_required()
def obtener_donante(id_donante):
    """Obtiene un donante por ID usando PAQ_DONANTE.OBTENER_DONANTE"""
    print(f"📋 Obteniendo donante: {id_donante}")
    
    try:
        conn = cursor = None
        conn = get_connection()
        cursor = conn.cursor()
        
        # Usar el procedimiento del paquete que retorna cursor
        out_cursor = cursor.var(oracledb.CURSOR)
        cursor.callproc("PAQ_DONANTE.OBTENER_DONANTE", [id_donante, out_cursor])
        
        data = out_cursor.getvalue().fetchall()
        
        if not data:
            print("❌ Donante no encontrado")
            return jsonify({'error': 'Donante no encontrado'}), 404
        
        row = data[0]
        donante = {
            'id_donante': row[0],
            'nombre': row[1],
            'apellido': row[2],
            'direccion': row[3],
            'fecha_nacimiento': str(row[4]) if row[4] else None,
            'sexo': row[5],
            'telefono': row[6],
            'correo': row[7],
            'id_tipo_sangre': row[8],
            'tipo_sangre': row[9] if len(row) > 9 else None  # Incluye el tipo de sangre del JOIN
        }
        
        print(f"✅ Donante encontrado: {donante['nombre']} {donante['apellido']}")
        return jsonify(donante), 200
        
    except Exception as e:
        print(f"❌ Error obteniendo donante: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@donantes_bp.route('/listar', methods=['GET'])
@jwt_required()
def listar_donantes():
    """Lista todos los donantes usando PAQ_DONANTE.LISTAR_DONANTES"""
    print("📋 Listando todos los donantes")
    
    try:
        conn = cursor = None
        conn = get_connection()
        cursor = conn.cursor()
        
        # Usar el procedimiento del paquete que retorna cursor
        out_cursor = cursor.var(oracledb.CURSOR)
        cursor.callproc("PAQ_DONANTE.LISTAR_DONANTES", [out_cursor])
        
        data = out_cursor.getvalue().fetchall()
        
        donantes = []
        for row in data:
            donantes.append({
                'id_donante': row[0],
                'nombre': row[1],
                'apellido': row[2],
                'direccion': row[3],
                'fecha_nacimiento': str(row[4]) if row[4] else None,
                'sexo': row[5],
                'telefono': row[6],
                'correo': row[7],
                'id_tipo_sangre': row[8],
                'tipo_sangre': row[9] if len(row) > 9 else None
            })
        
        print(f"✅ {len(donantes)} donantes encontrados")
        return jsonify(donantes), 200
        
    except Exception as e:
        print(f"❌ Error listando donantes: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@donantes_bp.route('/<id_donante>', methods=['PUT'])
@jwt_required()
def actualizar_donante(id_donante):
    """Actualiza un donante usando PAQ_DONANTE.ACTUALIZAR_DONANTE"""
    print(f"✏️ Actualizando donante: {id_donante}")
    
    try:
        # Verificar permisos
        usuario = get_jwt_identity()
        rol = usuario.get('rol', '')
        roles_permitidos = ['Administrador', 'Diplomado', 'Microbiologo', 'Jefatura']
        
        if rol not in roles_permitidos:
            return jsonify({'error': 'Acceso denegado'}), 403
        
        # Obtener y validar datos
        data = request.get_json() or {}
        data['id_donante'] = id_donante  # Asegurar que el ID coincida
        data, errors = validate_donante_data(data)
        
        if errors:
            return jsonify({
                'error': 'Datos inválidos',
                'detalles': errors
            }), 400
        
        # Actualizar donante usando el paquete
        conn = cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.callproc("PAQ_DONANTE.ACTUALIZAR_DONANTE", [
                data['id_donante'],
                data['nombre'],
                data['apellido'],
                data['direccion'],
                data['fecha_nacimiento'],
                data['sexo'],
                data['telefono'],
                data['correo'],
                data['id_tipo_sangre']
            ])
            
            conn.commit()
            print("✅ Donante actualizado correctamente")
            return jsonify({'mensaje': 'Donante actualizado correctamente'}), 200
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        
    except Exception as e:
        print(f"❌ Error actualizando donante: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

@donantes_bp.route('/<id_donante>', methods=['DELETE'])
@jwt_required()
def eliminar_donante(id_donante):
    """Elimina un donante usando PAQ_DONANTE.ELIMINAR_DONANTE"""
    print(f"🗑️ Eliminando donante: {id_donante}")
    
    try:
        # Verificar permisos - solo roles altos
        usuario = get_jwt_identity()
        rol = usuario.get('rol', '')
        roles_permitidos = ['Administrador', 'Jefatura']
        
        if rol not in roles_permitidos:
            return jsonify({'error': 'Acceso denegado'}), 403
        
        # Eliminar donante usando el paquete
        conn = cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.callproc("PAQ_DONANTE.ELIMINAR_DONANTE", [id_donante])
            
            conn.commit()
            print("✅ Donante eliminado correctamente")
            return jsonify({'mensaje': 'Donante eliminado correctamente'}), 200
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        
    except Exception as e:
        print(f"❌ Error eliminando donante: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500