from flask import Flask
from flask_jwt_extended import JWTManager
from auth import auth_bp
from donantes import donantes_bp
from donaciones import donaciones_bp
from rechazos import rechazos_bp
from inventario import inventario_bp

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'clave_secreta_bloodcare'

jwt = JWTManager(app)

# Registro de Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(donantes_bp, url_prefix='/api/donantes')
app.register_blueprint(donaciones_bp, url_prefix='/api/donaciones')
app.register_blueprint(rechazos_bp, url_prefix='/api/rechazos')
app.register_blueprint(inventario_bp, url_prefix='/api/inventario')