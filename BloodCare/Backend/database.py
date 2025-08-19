import oracledb
from config import Config

def get_connection():
    """Obtiene una conexión a la base de datos Oracle"""
    try:
        dsn = oracledb.makedsn(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            service_name=Config.DB_SERVICE
        )
        
        connection = oracledb.connect(
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            dsn=dsn
        )
        return connection
        
    except oracledb.Error as e:
        print(f"❌ Error conectando a Oracle: {e}")
        raise

def execute_procedure(proc_name, params=None):
    """Ejecuta un procedimiento almacenado"""
    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.callproc(proc_name, params)
        else:
            cursor.callproc(proc_name)
            
        conn.commit()
        return True
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def execute_function(func_name, return_type, params=None):
    """Ejecuta una función almacenada"""
    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if params:
            result = cursor.callfunc(func_name, return_type, params)
        else:
            result = cursor.callfunc(func_name, return_type)
            
        return result
        
    except Exception as e:
        raise e
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_cursor_data(proc_name, params=None):
    """Obtiene datos de un procedimiento que retorna cursor"""
    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        out_cursor = cursor.var(oracledb.CURSOR)
        
        if params:
            params.append(out_cursor)
            cursor.callproc(proc_name, params)
        else:
            cursor.callproc(proc_name, [out_cursor])
            
        return out_cursor.getvalue().fetchall()
        
    except Exception as e:
        raise e
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
