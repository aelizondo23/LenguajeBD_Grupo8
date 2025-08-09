
import oracledb

def get_connection():
    try:
        dsn = oracledb.makedsn(
            host="192.168.100.157",
            port=1521,
            service_name="orclpdb"
        )
        connection = oracledb.connect(
            user="BLOODCARE",
            password="admin123",
            dsn=dsn,
            encoding="UTF-8"
        )
        return connection
    except oracledb.Error as e:
        print("Error al conectar con la base de datos:", e)
        raise

