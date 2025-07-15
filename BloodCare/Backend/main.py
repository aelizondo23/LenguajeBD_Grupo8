from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from auth import auth_bp
from donantes import donantes_bp
from donaciones import donaciones_bp
from inventario import inventario_bp
from rechazos import rechazos_bp

# Crear la app
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'clave_secreta_bloodcare'
CORS(app)  # OTROS PUERTOS
jwt = JWTManager(app)

# Registro de Blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(donantes_bp, url_prefix="/api/donantes")
app.register_blueprint(donaciones_bp, url_prefix="/api/donaciones")
app.register_blueprint(inventario_bp, url_prefix="/api/inventario")
app.register_blueprint(rechazos_bp, url_prefix="/api/rechazos")

if __name__ == '__main__':
    app.run(debug=True, port=5000)

