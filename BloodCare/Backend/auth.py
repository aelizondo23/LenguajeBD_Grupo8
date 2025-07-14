from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import oracledb as cx_Oracle

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'clave_secreta_bloodcare'
jwt = JWTManager(app)

# Conexión a Oracle
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="ORCLPDB")
connection = cx_Oracle.connect(user="BLOODCARE", password="admin123", dsn=dsn)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    usuario = data.get("nombre_usuario")
    contrasena = data.get("contrasena")

    cursor = connection.cursor()
    cursor.execute("""
        SELECT id_usuario, nombre_usuario, contrasena, id_rol
        FROM usuario
        WHERE nombre_usuario = :1
    """, [usuario])

    result = cursor.fetchone()
    cursor.close()

    if not result:
        return jsonify({"msg": "Usuario no encontrado"}), 401

    id_usuario, nombre_usuario, contrasena_bd, id_rol = result

    if contrasena != contrasena_bd:
        return jsonify({"msg": "Contraseña incorrecta"}), 401

    cursor = connection.cursor()
    cursor.execute("SELECT nombre_rol FROM rol WHERE id_rol = :1", [id_rol])
    rol_result = cursor.fetchone()
    cursor.close()

    rol = rol_result[0] if rol_result else "Sin rol"

    access_token = create_access_token(identity={
        "id_usuario": id_usuario,
        "rol": rol
    })

    return jsonify(access_token=access_token)

@app.route('/api/donantes', methods=['POST'])
@jwt_required()
def registrar_donante():
    data = request.json
    usuario_actual = get_jwt_identity()
    rol = usuario_actual['rol']

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
