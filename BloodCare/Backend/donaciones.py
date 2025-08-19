from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import oracledb
from database import get_connection

donaciones_bp = Blueprint('donaciones', __name__)

@donaciones_bp.route('/registrar', methods=['POST'])
@jwt_required()
def registrar_donacion():
    """Registra una nueva donación usando pkg_donacion.registrar_donacion"""
    print("🩸 Solicitud de registro de donación recibida")
    
    try:
        # Obtener usuario del JWT
        usuario_id = get_jwt_identity()
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        
        rol = claims.get('rol', '')
        id_usuario = claims.get('id_usuario')
        nombre_usuario = claims.get('nombre_usuario', '')
        
        print(f"Usuario JWT Identity: {usuario_id}")
        print(f"Usuario Claims ID: {id_usuario}")
        print(f"Usuario: {nombre_usuario} - Rol: {rol}")
        
        # Manejar ID de usuario - puede ser string o número
        if not id_usuario:
            # Si no hay id_usuario en claims, usar el identity
            id_usuario = usuario_id
        
        # Si es string como "USR001", extraer el número o usar un valor por defecto
        if isinstance(id_usuario, str):
            if id_usuario.startswith('USR'):
                # Extraer número de "USR001" -> 1
                try:
                    id_usuario = int(id_usuario[3:])
                except ValueError:
                    id_usuario = 1  # Usuario por defecto
            else:
                try:
                    id_usuario = int(id_usuario)
                except ValueError:
                    id_usuario = 1  # Usuario por defecto
        
        print(f"ID de usuario final: {id_usuario}")
        
        # Roles que pueden registrar donaciones
        roles_permitidos = ['Administrador', 'Diplomado', 'Tecnico', 'Microbiologo', 'Jefatura']
        
        if rol not in roles_permitidos:
            print(f"❌ Acceso denegado para rol: {rol}")
            return jsonify({'error': 'Acceso denegado'}), 403
        
        data = request.get_json() or {}
        print(f"Datos recibidos: {data}")
        
        # Validar campos requeridos
        required_fields = ['id_donante', 'id_centro', 'fecha', 'volumen_ml', 'estado']
        for field in required_fields:
            if not data.get(field):
                print(f"❌ Campo faltante: {field}")
                return jsonify({'error': f'Campo {field} es requerido'}), 400
        
        # Validar que el donante existe
        print(f"Verificando existencia del donante: {data['id_donante']}")
        
        # Procesar fecha
        fecha_str = str(data['fecha']).strip()
        print(f"Fecha recibida: {fecha_str}")
        
        try:
            if '/' in fecha_str:  # DD/MM/YYYY
                day, month, year = fecha_str.split('/')
                fecha_obj = datetime(int(year), int(month), int(day))
            else:  # YYYY-MM-DD
                fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
        except Exception as e:
            print(f"❌ Error procesando fecha: {e}")
            return jsonify({'error': 'Formato de fecha inválido'}), 400
        
        print(f"Fecha procesada: {fecha_obj}")
        
        # Validar volumen
        try:
            volumen = int(data['volumen_ml'])
            if volumen <= 0:
                return jsonify({'error': 'El volumen debe ser mayor a 0'}), 400
        except ValueError:
            return jsonify({'error': 'El volumen debe ser un número válido'}), 400
        
        # Validar centro
        try:
            centro = int(data['id_centro'])
        except ValueError:
            return jsonify({'error': 'ID de centro inválido'}), 400
        
        conn = cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Variable para capturar el ID de la donación
            id_donacion_out = cursor.var(oracledb.NUMBER)
            
            print("Llamando al procedimiento pkg_donacion.registrar_donacion...")
            
            # Llamar al procedimiento del paquete
            cursor.callproc("pkg_donacion.registrar_donacion", [
                data['id_donante'],
                centro,
                fecha_obj,
                volumen,
                data['estado'],
                id_usuario,
                id_donacion_out
            ])
            
            conn.commit()
            
            # Obtener el ID generado
            nuevo_id = int(id_donacion_out.getvalue())
            
            print(f"✅ Donación registrada con ID: {nuevo_id}")
            return jsonify({
                'mensaje': 'Donación registrada correctamente',
                'id_donacion': nuevo_id
            }), 201
            
        except oracledb.Error as e:
            if conn:
                conn.rollback()
            print(f"❌ Error de Oracle: {e}")
            
            # Debug adicional del error
            error_code = getattr(e, 'code', None)
            error_msg = str(e)
            print(f"🔍 Código de error: {error_code}")
            print(f"🔍 Mensaje completo: {error_msg}")
            
            # Manejar errores específicos de Oracle
            if "ORA-01403" in error_msg:
                print("🔍 Error ORA-01403: Verificando qué datos no se encontraron...")
                # Verificar si el donante existe
                try:
                    cursor.execute("SELECT COUNT(*) FROM donante WHERE id_donante = :1", [data['id_donante']])
                    count = cursor.fetchone()[0]
                    print(f"🔍 Donante {data['id_donante']} existe: {count > 0} (count: {count})")
                except Exception as check_error:
                    print(f"🔍 Error verificando donante: {check_error}")
                
                # Verificar si el centro existe
                try:
                    cursor.execute("SELECT COUNT(*) FROM centro_donacion WHERE id_centro = :1", [centro])
                    count = cursor.fetchone()[0]
                    print(f"🔍 Centro {centro} existe: {count > 0} (count: {count})")
                except Exception as check_error:
                    print(f"🔍 Error verificando centro: {check_error}")
                
                return jsonify({'error': 'El donante especificado no existe'}), 404
            elif "foreign key constraint" in error_msg.lower():
                return jsonify({'error': 'Referencia inválida en los datos'}), 404
            elif "check constraint" in error_msg.lower():
                return jsonify({'error': 'Datos inválidos según las reglas de negocio'}), 400
            else:
                return jsonify({'error': f'Error de base de datos: {error_msg}'}), 500
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ Error general: {e}")
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        
    except Exception as e:
        print(f"❌ Error registrando donación: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

@donaciones_bp.route('/listar', methods=['GET'])
@jwt_required()
def listar_donaciones():
    """Lista todas las donaciones usando pkg_donacion.listar_donaciones"""
    print("📋 Listando todas las donaciones")
    
    try:
        conn = cursor = None
        conn = get_connection()
        cursor = conn.cursor()
        
        out_cursor = cursor.var(oracledb.CURSOR)
        cursor.callproc("pkg_donacion.listar_donaciones", [out_cursor])
        
        data = out_cursor.getvalue().fetchall()
        
        donaciones = []
        for row in data:
            donaciones.append({
                'id_donacion': row[0],
                'id_donante': row[1],
                'id_centro': row[2],
                'fecha': str(row[3]) if row[3] else None,
                'volumen_ml': row[4],
                'estado': row[5],
                'id_usuario_registra': row[6],
                'centro': row[7] if len(row) > 7 else None,
                'usuario_registra': row[8] if len(row) > 8 else None
            })
        
        print(f"✅ {len(donaciones)} donaciones encontradas")
        return jsonify(donaciones), 200
        
    except Exception as e:
        print(f"❌ Error listando donaciones: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@donaciones_bp.route('/<int:id_donacion>', methods=['GET'])
@jwt_required()
def obtener_donacion(id_donacion):
    """Obtiene una donación por ID usando pkg_donacion.obtener_por_id"""
    print(f"📋 Obteniendo donación: {id_donacion}")
    
    try:
        conn = cursor = None
        conn = get_connection()
        cursor = conn.cursor()
        
        out_cursor = cursor.var(oracledb.CURSOR)
        cursor.callproc("pkg_donacion.obtener_por_id", [id_donacion, out_cursor])
        
        data = out_cursor.getvalue().fetchall()
        
        if not data:
            return jsonify({'error': 'Donación no encontrada'}), 404
        
        row = data[0]
        donacion = {
            'id_donacion': row[0],
            'id_donante': row[1],
            'id_centro': row[2],
            'fecha': str(row[3]) if row[3] else None,
            'volumen_ml': row[4],
            'estado': row[5],
            'id_usuario_registra': row[6],
            'centro': row[7] if len(row) > 7 else None,
            'usuario_registra': row[8] if len(row) > 8 else None
        }
        
        return jsonify(donacion), 200
        
    except Exception as e:
        print(f"❌ Error obteniendo donación: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()