import oracledb

try:
    conn = oracledb.connect(
        user="BLOODCARE",
        password="admin123",
        dsn="192.168.100.157:1521/orclpdb"
    )
    print(" Conexión con BLOODCARE exitosa")
    conn.close()
except Exception as e:
    print(" Error:", e)


