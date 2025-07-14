from flask import Flask, request, jsonify
import oracledb as cx_Oracle

app = Flask(__name__)

# Configuración de conexión
conn = cx_Oracle.connect(user="sys", password="123", dsn="192.168.100.157/ORCLPDB")

@app.route('/api/donantes', methods=['POST'])
def registrar_donante():
    try:
        data = request.get_json()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO donante (
                id_donante, nombre, apellido, direccion, fecha_nacimiento, sexo,
                telefono, correo, id_tipo_sangre
            )
            VALUES (
                :1, :2, :3, :4, TO_DATE(:5, 'YYYY-MM-DD'), :6, :7, :8,
                (SELECT id_tipo_sangre FROM tipo_sangre WHERE tipo = :9)
            )
        """, (
            data['cedula'], data['nombre'], data['apellido'], data.get('direccion', ''),
            data['fecha_nacimiento'], data['sexo'], data.get('telefono', ''),
            data.get('correo', ''), data['tipo_sangre']
        ))

        conn.commit()
        return jsonify({"mensaje": "✅ Donante registrado exitosamente"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/donaciones', methods=['POST'])
def registrar_donacion():
    try:
        data = request.get_json()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO donacion (
                id_donante, id_centro, fecha, volumen_ml, estado, id_usuario_registra
            )
            VALUES (:1, :2, TO_DATE(:3, 'YYYY-MM-DD'), :4, :5, :6)
        """, (
            data['id_donante'], data['id_centro'], data['fecha'],
            data['volumen_ml'], data['estado'], data['id_usuario_registra']
        ))

        conn.commit()
        return jsonify({"mensaje": "✅ Donación registrada exitosamente"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/rechazos', methods=['POST'])
def registrar_rechazo():
    try:
        data = request.get_json()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO rechazo (
                id_donacion, id_causa, observaciones, usuario_registra
            )
            VALUES (:1, :2, :3, :4)
        """, (
            data['id_donacion'], data['id_causa'],
            data.get('observaciones', ''), data['usuario_registra']
        ))

        conn.commit()
        return jsonify({"mensaje": "✅ Rechazo registrado exitosamente"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/inventario', methods=['GET'])
def obtener_inventario():
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT ts.tipo AS tipo_sangre, cs.nombre AS componente, i.unidades_disponibles
            FROM inventario i
            JOIN tipo_sangre ts ON i.id_tipo_sangre = ts.id_tipo_sangre
            JOIN componente_sanguineo cs ON i.id_componente = cs.id_componente
            ORDER BY tipo_sangre, componente
        """)
        columnas = [desc[0].lower() for desc in cur.description]
        resultados = [dict(zip(columnas, fila)) for fila in cur.fetchall()]
        return jsonify(resultados)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
