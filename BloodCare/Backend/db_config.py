
import oracledb

def get_connection():
    dsn = oracledb.makedsn("192.168.100.157", 1521, service_name="orclpdb")
    return oracledb.connect(user="BLOODCARE", password="admin123", dsn=dsn)

