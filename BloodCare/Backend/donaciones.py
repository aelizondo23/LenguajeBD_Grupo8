from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import oracledb
from database import get_connection

donaciones_bp = Blueprint('donaciones', __name__)

@donaciones_bp.route('/registrar', methods=['POST'])
@jwt_required()
def registrar_donacion():
    """Registra una nueva donación con componentes sanguíneos"""
    print("🩸 Solicitud de registro de donación con componentes recibida")
    
    try:
        # Obtener usuario del JWT
        usuario_id = get_jwt_identity()
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        
        rol = claims.get('rol', '')
        id_usuario = claims.get('id_usuario')
        nombre_usuario = claims.get('nombre_usuario', '')
        
        print(f"Usuario: {nombre_usuario} - Rol: {rol}")
        
        # Manejar ID de usuario - MANTENER COMO STRING
        if not id_usuario:
            id_usuario = usuario_id
        id_usuario = str(id_usuario)
        
        print(f"ID de usuario final (como string): {id_usuario}")
        
        # Roles que pueden registrar donaciones
        roles_permitidos = ['Administrador', 'Diplomado', 'Tecnico', 'Microbiologo', 'Jefatura']
        
        if rol not in roles_permitidos:
            print(f"❌ Acceso denegado para rol: {rol}")
            return jsonify({'error': 'Acceso denegado'}), 403
        
        data = request.get_json() or {}
        print(f"Datos recibidos: {data}")
        
        # Validar campos requeridos
        required_fields = ['id_donante', 'id_centro', 'fecha', 'estado', 'componentes']
        for field in required_fields:
            if not data.get(field):
                print(f"❌ Campo faltante: {field}")
                return jsonify({'error': f'Campo {field} es requerido'}), 400
        
        # Validar componentes
        componentes = data.get('componentes', {})
        globulos_rojos = float(componentes.get('globulos_rojos', 0))
        plaquetas = float(componentes.get('plaquetas', 0))
        plasma = float(componentes.get('plasma', 0))
        
        # Calcular volumen total
        volumen_total = globulos_rojos + plaquetas + plasma
        
        print(f"Componentes: GR={globulos_rojos}, PLQ={plaquetas}, PLS={plasma}, Total={volumen_total}")
        
        # Validar que al menos un componente tenga valor
        if volumen_total <= 0:
            return jsonify({'error': 'Debe especificar al menos un componente con valor mayor a 0'}), 400
        
        # Validar volumen mínimo
        if volumen_total < 350:
            return jsonify({'error': 'El volumen total debe ser de al menos 350 ml'}), 400
        
        # Procesar fecha
        fecha_str = str(data['fecha']).strip()
        try:
            if '/' in fecha_str:
                day, month, year = fecha_str.split('/')
                fecha_obj = datetime(int(year), int(month), int(day))
            else:
                fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
        except Exception as e:
            print(f"❌ Error procesando fecha: {e}")
            return jsonify({'error': 'Formato de fecha inválido'}), 400
        
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
            
            print("1️⃣ Registrando donación principal...")
            
            # Llamar al procedimiento para registrar la donación
            cursor.callproc("pkg_donacion.registrar_donacion", [
                data['id_donante'],
                centro,
                fecha_obj,
                int(volumen_total),
                data['estado'],
                id_usuario,
                id_donacion_out
            ])
            
            # Obtener el ID generado
            nuevo_id = int(id_donacion_out.getvalue())
            print(f"✅ Donación registrada con ID: {nuevo_id}")
            
            # 2️⃣ Registrar componentes sanguíneos
            print("2️⃣ Registrando componentes sanguíneos...")
            
            # Mapeo de componentes: ID en base de datos
            componentes_map = {
                'globulos_rojos': 1,  # ID 1 en componente_sanguineo
                'plaquetas': 2,       # ID 2 en componente_sanguineo  
                'plasma': 3           # ID 3 en componente_sanguineo
            }
            
            componentes_valores = {
                'globulos_rojos': globulos_rojos,
                'plaquetas': plaquetas,
                'plasma': plasma
            }
            
            # Insertar cada componente que tenga valor > 0
            for componente_nombre, componente_id in componentes_map.items():
                valor = componentes_valores[componente_nombre]
                if valor > 0:
                    print(f"  - Registrando {componente_nombre}: {valor} ml")
                    cursor.callproc("pkg_donacion.agregar_componente", [
                        nuevo_id,
                        componente_id,
                        valor
                    ])
            
            conn.commit()
            
            print(f"✅ Donación y componentes registrados correctamente")
            return jsonify({
                'mensaje': 'Donación y componentes registrados correctamente',
                'id_donacion': nuevo_id,
                'volumen_total': volumen_total,
                'componentes_registrados': {k: v for k, v in componentes_valores.items() if v > 0}
            }), 201
            
        except oracledb.Error as e:
            if conn:
                conn.rollback()
            print(f"❌ Error de Oracle: {e}")
            error_msg = str(e)
            
            if "ORA-01403" in error_msg:
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
    """Lista todas las donaciones con sus componentes"""
    print("📋 Listando donaciones con componentes")
    
    try:
        conn = cursor = None
        conn = get_connection()
        cursor = conn.cursor()
        
        # Obtener donaciones
        out_cursor = cursor.var(oracledb.CURSOR)
        cursor.callproc("pkg_donacion.listar_donaciones", [out_cursor])
        
        data = out_cursor.getvalue().fetchall()
        
        donaciones = []
        for row in data:
            id_donacion = row[0]
            
            # Obtener componentes para esta donación
            componentes = obtener_componentes_donacion(cursor, id_donacion)
            
            donacion = {
                'id_donacion': id_donacion,
                'id_donante': row[1],
                'id_centro': row[2],
                'fecha': str(row[3]) if row[3] else None,
                'volumen_ml': row[4],
                'estado': row[5],
                'id_usuario_registra': row[6],
                'centro': row[7] if len(row) > 7 else None,
                'usuario_registra': row[8] if len(row) > 8 else None,
                'componentes': componentes
            }
            donaciones.append(donacion)
        
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
    """Obtiene una donación por ID con sus componentes"""
    print(f"📋 Obteniendo donación: {id_donacion}")
    
    conn = cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Obtener donación
        sql = """
        SELECT d.id_donacion, d.id_donante, d.id_centro, d.fecha,
               d.volumen_ml, d.estado, d.id_usuario_registra,
               cd.nombre AS centro, 
               u.nombre_usuario AS usuario_registra
        FROM donacion d
        LEFT JOIN centro_donacion cd ON cd.id_centro = d.id_centro
        LEFT JOIN usuario u ON u.id_usuario = d.id_usuario_registra
        WHERE d.id_donacion = :id_param
        """
        
        cursor.execute(sql, {'id_param': id_donacion})
        data = cursor.fetchall()
        
        if not data:
            return jsonify({'error': 'Donación no encontrada'}), 404
        
        row = data[0]
        
        # Obtener componentes
        componentes = obtener_componentes_donacion(cursor, id_donacion)
        
        donacion = {
            'id_donacion': row[0],
            'id_donante': row[1],
            'id_centro': row[2],
            'fecha': str(row[3]) if row[3] else None,
            'volumen_ml': row[4],
            'estado': row[5],
            'id_usuario_registra': row[6],
            'centro': row[7],
            'usuario_registra': row[8],
            'componentes': componentes
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

@donaciones_bp.route('/editar/<int:id_donacion>', methods=['PUT'])
@jwt_required()
def editar_donacion(id_donacion):
    """Edita una donación existente y sus componentes"""
    print(f"✏️ Solicitud de edición de donación ID: {id_donacion}")
    
    try:
        # Obtener usuario del JWT
        usuario_id = get_jwt_identity()
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        
        rol = claims.get('rol', '')
        id_usuario = claims.get('id_usuario')
        nombre_usuario = claims.get('nombre_usuario', '')
        
        # Roles que pueden editar donaciones
        roles_permitidos = ['Administrador', 'Diplomado', 'Tecnico', 'Microbiologo', 'Jefatura']
        
        if rol not in roles_permitidos:
            print(f"❌ Acceso denegado para rol: {rol}")
            return jsonify({'error': 'Acceso denegado'}), 403
        
        data = request.get_json() or {}
        print(f"Datos recibidos para edición: {data}")
        
        # Validar campos requeridos
        required_fields = ['id_donante', 'id_centro', 'fecha', 'estado', 'componentes']
        for field in required_fields:
            if not data.get(field):
                print(f"❌ Campo faltante: {field}")
                return jsonify({'error': f'Campo {field} es requerido'}), 400
        
        # Validar componentes
        componentes = data.get('componentes', {})
        globulos_rojos = float(componentes.get('globulos_rojos', 0))
        plaquetas = float(componentes.get('plaquetas', 0))
        plasma = float(componentes.get('plasma', 0))
        
        # Calcular volumen total
        volumen_total = globulos_rojos + plaquetas + plasma
        
        if volumen_total <= 0:
            return jsonify({'error': 'Debe especificar al menos un componente con valor mayor a 0'}), 400
        
        if volumen_total < 350:
            return jsonify({'error': 'El volumen total debe ser de al menos 350 ml'}), 400
        
        # Procesar fecha
        fecha_str = str(data['fecha']).strip()
        try:
            if '/' in fecha_str:
                day, month, year = fecha_str.split('/')
                fecha_obj = datetime(int(year), int(month), int(day))
            else:
                fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
        except Exception as e:
            print(f"❌ Error procesando fecha: {e}")
            return jsonify({'error': 'Formato de fecha inválido'}), 400
        
        # Validar centro
        try:
            centro = int(data['id_centro'])
        except ValueError:
            return jsonify({'error': 'ID de centro inválido'}), 400
        
        if not id_usuario:
            id_usuario = usuario_id
        
        conn = cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            print("1️⃣ Actualizando donación principal...")
            
            # Actualizar la donación
            cursor.callproc("pkg_donacion.actualizar_donacion", [
                id_donacion,
                data['id_donante'],
                centro,
                fecha_obj,
                int(volumen_total),
                data['estado'],
                id_usuario
            ])
            
            print("2️⃣ Actualizando componentes...")
            
            # Eliminar componentes existentes
            cursor.execute("DELETE FROM donacion_componente WHERE id_donacion = :1", [id_donacion])
            print(f"  - Componentes anteriores eliminados")
            
            # Insertar nuevos componentes
            componentes_map = {
                'globulos_rojos': 1,
                'plaquetas': 2,
                'plasma': 3
            }
            
            componentes_valores = {
                'globulos_rojos': globulos_rojos,
                'plaquetas': plaquetas,
                'plasma': plasma
            }
            
            for componente_nombre, componente_id in componentes_map.items():
                valor = componentes_valores[componente_nombre]
                if valor > 0:
                    print(f"  - Insertando {componente_nombre}: {valor} ml")
                    cursor.callproc("pkg_donacion.agregar_componente", [
                        id_donacion,
                        componente_id,
                        valor
                    ])
            
            conn.commit()
            
            print(f"✅ Donación {id_donacion} y componentes actualizados correctamente")
            return jsonify({
                'mensaje': 'Donación y componentes actualizados correctamente',
                'id_donacion': id_donacion,
                'volumen_total': volumen_total,
                'componentes_actualizados': {k: v for k, v in componentes_valores.items() if v > 0}
            }), 200
            
        except oracledb.Error as e:
            if conn:
                conn.rollback()
            print(f"❌ Error de Oracle: {e}")
            error_msg = str(e)
            
            if "ORA-01403" in error_msg or "NO_DATA_FOUND" in error_msg:
                return jsonify({'error': 'La donación especificada no existe'}), 404
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
        print(f"❌ Error editando donación: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

@donaciones_bp.route('/<int:id_donacion>', methods=['DELETE'])
@jwt_required()
def eliminar_donacion(id_donacion):
    """Elimina una donación y todos sus componentes"""
    print(f"🗑️ Solicitud de eliminación de donación ID: {id_donacion}")
    
    try:
        # Obtener usuario del JWT
        usuario_id = get_jwt_identity()
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        
        rol = claims.get('rol', '')
        id_usuario = claims.get('id_usuario')
        nombre_usuario = claims.get('nombre_usuario', '')
        
        print(f"Usuario: {nombre_usuario} - Rol: {rol}")
        
        # Solo Administradores y Jefatura pueden eliminar donaciones
        roles_permitidos = ['Administrador', 'Jefatura']
        
        if rol not in roles_permitidos:
            print(f"❌ Acceso denegado para rol: {rol}")
            return jsonify({'error': 'Solo Administradores y Jefatura pueden eliminar donaciones'}), 403
        
        # Manejar ID de usuario
        if not id_usuario:
            id_usuario = usuario_id
        
        conn = cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Verificar que la donación existe
            print(f"Verificando existencia de donación: {id_donacion}")
            cursor.execute("SELECT COUNT(*) FROM donacion WHERE id_donacion = :1", [id_donacion])
            count = cursor.fetchone()[0]
            
            if count == 0:
                print(f"❌ Donación {id_donacion} no encontrada")
                return jsonify({'error': 'La donación especificada no existe'}), 404
            
            print("El procedimiento pkg_donacion.eliminar_donacion ya maneja la eliminación en cascada")
            
            # El procedimiento ya elimina los componentes en cascada
            cursor.callproc("pkg_donacion.eliminar_donacion", [
                id_donacion,
                id_usuario
            ])
            
            conn.commit()
            
            print(f"✅ Donación {id_donacion} y sus componentes eliminados correctamente")
            return jsonify({
                'mensaje': 'Donación y componentes eliminados correctamente',
                'id_donacion': id_donacion
            }), 200
            
        except oracledb.Error as e:
            if conn:
                conn.rollback()
            print(f"❌ Error de Oracle: {e}")
            error_msg = str(e)
            
            if "ORA-01403" in error_msg or "NO_DATA_FOUND" in error_msg:
                return jsonify({'error': 'La donación especificada no existe'}), 404
            elif "integrity constraint" in error_msg.lower():
                return jsonify({'error': 'No se puede eliminar la donación porque tiene registros relacionados'}), 409
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
        print(f"❌ Error eliminando donación: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

@donaciones_bp.route('/<int:id_donacion>/componentes', methods=['GET'])
@jwt_required()
def listar_componentes_donacion(id_donacion):
    """Lista los componentes de una donación específica"""
    print(f"📋 Listando componentes de donación: {id_donacion}")
    
    try:
        conn = cursor = None
        conn = get_connection()
        cursor = conn.cursor()
        
        componentes = obtener_componentes_donacion(cursor, id_donacion)
        
        return jsonify({
            'id_donacion': id_donacion,
            'componentes': componentes
        }), 200
        
    except Exception as e:
        print(f"❌ Error listando componentes: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def obtener_componentes_donacion(cursor, id_donacion):
    """Función auxiliar para obtener componentes de una donación"""
    try:
        sql = """
        SELECT dc.id_componente, cs.nombre, dc.unidades
        FROM donacion_componente dc
        JOIN componente_sanguineo cs ON cs.id_componente = dc.id_componente
        WHERE dc.id_donacion = :id_donacion
        ORDER BY dc.id_componente
        """
        
        cursor.execute(sql, {'id_donacion': id_donacion})
        data = cursor.fetchall()
        
        # Inicializar componentes con valores en 0
        componentes = {
            'globulos_rojos': 0,
            'plaquetas': 0,
            'plasma': 0
        }
        
        # Mapear los componentes según su ID
        for row in data:
            componente_id = row[0]
            unidades = row[2]
            
            if componente_id == 1:  # Glóbulos Rojos
                componentes['globulos_rojos'] = float(unidades)
            elif componente_id == 2:  # Plaquetas
                componentes['plaquetas'] = float(unidades)
            elif componente_id == 3:  # Plasma
                componentes['plasma'] = float(unidades)
        
        return componentes
        
    except Exception as e:
        print(f"❌ Error obteniendo componentes: {e}")
        return {'globulos_rojos': 0, 'plaquetas': 0, 'plasma': 0}

@donaciones_bp.route('/componente', methods=['POST'])
@jwt_required()
def agregar_componente():
    """Agrega un componente específico a una donación"""
    print("🧬 Agregando componente a donación")
    
    try:
        data = request.get_json() or {}
        
        required_fields = ['id_donacion', 'id_componente', 'unidades']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} es requerido'}), 400
        
        conn = cursor = None
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.callproc("pkg_donacion.agregar_componente", [
            data['id_donacion'],
            data['id_componente'],
            data['unidades']
        ])
        
        conn.commit()
        
        print("✅ Componente agregado correctamente")
        return jsonify({'mensaje': 'Componente agregado correctamente'}), 201
        
    except Exception as e:
        print(f"❌ Error agregando componente: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@donaciones_bp.route('/buscar', methods=['GET'])
@jwt_required()
def buscar_donaciones():
    """Busca donaciones por diferentes criterios con componentes"""
    print("🔍 Búsqueda de donaciones con filtros")
    
    try:
        # Obtener parámetros de consulta
        id_donante = request.args.get('id_donante')
        id_centro = request.args.get('id_centro')
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        estado = request.args.get('estado')
        
        print(f"Filtros aplicados: donante={id_donante}, centro={id_centro}, "
              f"desde={fecha_desde}, hasta={fecha_hasta}, estado={estado}")
        
        conn = cursor = None
        conn = get_connection()
        cursor = cursor()
        
        # Construir consulta SQL dinámicamente
        where_conditions = []
        params = {}
        
        base_sql = """
        SELECT d.id_donacion, d.id_donante, d.id_centro, d.fecha,
               d.volumen_ml, d.estado, d.id_usuario_registra,
               cd.nombre AS centro, 
               u.nombre_usuario AS usuario_registra
        FROM donacion d
        LEFT JOIN centro_donacion cd ON cd.id_centro = d.id_centro
        LEFT JOIN usuario u ON u.id_usuario = d.id_usuario_registra
        """
        
        if id_donante:
            where_conditions.append("d.id_donante = :id_donante")
            params['id_donante'] = id_donante
        
        if id_centro:
            where_conditions.append("d.id_centro = :id_centro")
            params['id_centro'] = int(id_centro)
        
        if fecha_desde:
            where_conditions.append("d.fecha >= :fecha_desde")
            params['fecha_desde'] = datetime.strptime(fecha_desde, '%Y-%m-%d')
        
        if fecha_hasta:
            where_conditions.append("d.fecha <= :fecha_hasta")
            params['fecha_hasta'] = datetime.strptime(fecha_hasta, '%Y-%m-%d')
        
        if estado:
            where_conditions.append("d.estado = :estado")
            params['estado'] = estado
        
        if where_conditions:
            base_sql += " WHERE " + " AND ".join(where_conditions)
        
        base_sql += " ORDER BY d.fecha DESC, d.id_donacion DESC"
        
        cursor.execute(base_sql, params)
        data = cursor.fetchall()
        
        donaciones = []
        for row in data:
            id_donacion = row[0]
            
            # Obtener componentes para esta donación
            componentes = obtener_componentes_donacion(cursor, id_donacion)
            
            donacion = {
                'id_donacion': id_donacion,
                'id_donante': row[1],
                'id_centro': row[2],
                'fecha': str(row[3]) if row[3] else None,
                'volumen_ml': row[4],
                'estado': row[5],
                'id_usuario_registra': row[6],
                'centro': row[7] if len(row) > 7 else None,
                'usuario_registra': row[8] if len(row) > 8 else None,
                'componentes': componentes
            }
            donaciones.append(donacion)
        
        print(f"✅ {len(donaciones)} donaciones encontradas con los filtros aplicados")
        return jsonify({
            'donaciones': donaciones,
            'total': len(donaciones),
            'filtros_aplicados': {
                'id_donante': id_donante,
                'id_centro': id_centro,
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta,
                'estado': estado
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error buscando donaciones: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()