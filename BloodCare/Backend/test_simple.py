import socket
import oracledb
from config import Config

def test_network_connection():
    """Prueba si el puerto está abierto"""
    print("🌐 Probando conectividad de red...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((Config.DB_HOST, Config.DB_PORT))
        sock.close()
        
        if result == 0:
            print(f"✅ Puerto {Config.DB_HOST}:{Config.DB_PORT} está abierto")
            return True
        else:
            print(f"❌ Puerto {Config.DB_HOST}:{Config.DB_PORT} está cerrado o no responde")
            return False
    except Exception as e:
        print(f"❌ Error de red: {e}")
        return False

def test_oracle_connection():
    """Prueba la conexión a Oracle"""
    print("🔍 Probando conexión a Oracle...")
    try:
        dsn = oracledb.makedsn(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            service_name=Config.DB_SERVICE
        )
        print(f"DSN: {dsn}")
        
        connection = oracledb.connect(
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            dsn=dsn
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT 'Conexión exitosa' FROM dual")
        result = cursor.fetchone()
        
        print(f"✅ Oracle conectado: {result[0]}")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error Oracle: {e}")
        return False

def main():
    print("🧪 DIAGNÓSTICO DE CONEXIÓN ORACLE")
    print("=" * 50)
    print(f"Host: {Config.DB_HOST}")
    print(f"Puerto: {Config.DB_PORT}")
    print(f"Servicio: {Config.DB_SERVICE}")
    print(f"Usuario: {Config.DB_USER}")
    print("=" * 50)
    
    # Paso 1: Probar conectividad de red
    network_ok = test_network_connection()
    
    if not network_ok:
        print("\n🚨 PROBLEMA DE RED:")
        print("1. Verifica que Oracle esté ejecutándose en el servidor")
        print("2. Verifica que el puerto 1521 esté abierto")
        print("3. Verifica que no haya firewall bloqueando")
        print("4. Prueba hacer ping al servidor:")
        print(f"   ping {Config.DB_HOST}")
        return
    
    # Paso 2: Probar conexión Oracle
    oracle_ok = test_oracle_connection()
    
    if not oracle_ok:
        print("\n🚨 PROBLEMA DE ORACLE:")
        print("1. Verifica que el servicio 'orclpdb' esté disponible")
        print("2. Verifica las credenciales")
        print("3. Prueba con diferentes configuraciones:")
        print("   - Servicio: 'xe' en lugar de 'orclpdb'")
        print("   - SID en lugar de SERVICE_NAME")

if __name__ == "__main__":
    main()