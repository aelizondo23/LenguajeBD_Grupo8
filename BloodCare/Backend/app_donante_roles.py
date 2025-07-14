from flask import Flask, request, jsonify
import oracledb as cx_Oracle

app = Flask(__name__)

# Configuración de conexión a Oracle
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="ORCLPDB")
connection = cx_Oracle.connect(user="BLOODCARE", password="admin123", dsn=dsn)

# Función de verificación de rol por usuario
def obtener_rol_usuario(id_usuario):
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT r.nombre_rol
            FROM usuario u
            JOIN rol r ON u.id_rol = r.id_rol
            WHERE u.id_usuario = :id_usuario
        """, id_usuario=id_usuario)
        row = cursor.fetchone()
        return row[0] if row else None
    except Exception as e:
        return None
    finally:
        cursor.close()

@app.route('/api/donantes', methods=['POST'])
def registrar_donante():
    data = request.json
    id_usuario = data.get('id_usuario')
    rol = obtener_rol_usuario(id_usuario)

    if rol not in ['Técnico', 'Diplomado', 'Microbiólogo', 'Jefatura', 'Admin BD']:
        return jsonify({'error': 'Acceso denegado: rol no autorizado'}), 403

    try:
        cursor = connection.cursor()
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
        connection.commit()
        return jsonify({"mensaje": "Donante registrado correctamente"}), 201
    except cx_Oracle.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

if __name__ == '__main__':
    app.run(debug=True)