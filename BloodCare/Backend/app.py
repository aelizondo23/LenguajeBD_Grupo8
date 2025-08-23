from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config

# Importar blueprints
from auth import auth_bp
from donantes import donantes_bp
from donaciones import donaciones_bp
from admin import admin_bp
from tipo_sangre import tipo_sangre_bp
from inventario import inventario_bp
from rechazo import rechazo_bp
from causa_rechazo import causa_rechazo_bp

def create_app():
    """Factory para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Configuración
    app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = Config.JWT_ACCESS_TOKEN_EXPIRES
    
    # Extensiones
    CORS(app)
    jwt = JWTManager(app)
    
    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(donantes_bp, url_prefix="/api/donantes")
    app.register_blueprint(donaciones_bp, url_prefix="/api/donaciones")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(tipo_sangre_bp, url_prefix="/api/tipo_sangre")
    app.register_blueprint(inventario_bp, url_prefix="/api/inventario")
    app.register_blueprint(rechazo_bp, url_prefix="/api/rechazo")
    app.register_blueprint(causa_rechazo_bp, url_prefix="/api/causa_rechazo")
    return app

if __name__ == '__main__':
    app = create_app()
    print("🩸 BLOODCARE - Sistema de Gestión de Donantes")
    print("=" * 60)
    print(f"🚀 Servidor iniciando...")
    print(f"🌐 URL: http://localhost:{Config.PORT}")
    print(f"📊 Base de datos: Oracle en {Config.DB_HOST}:{Config.DB_PORT}")
    print(f"🔧 Modo debug: {Config.DEBUG}")
    print("=" * 60)
    print("📋 Endpoints disponibles:")
    print("   🔐 AUTH:")
    print("      POST /api/auth/login")
    print("   👤 DONANTES:")
    print("      POST /api/donantes/registrar")
    print("      GET  /api/donantes/<id>")
    print("      PUT  /api/donantes/<id>")
    print("      DELETE /api/donantes/<id>")
    print("      GET  /api/donantes/listar")
    print("   🩸 DONACIONES:")
    print("      POST /api/donaciones/registrar")
    print("      GET  /api/donaciones/<id>")
    print("      GET  /api/donaciones/listar")
    print("      PUT  /api/donaciones/<id>")
    print("      DELETE  /api/donaciones/<id>")
    print("   🔧 ADMIN:")
    print("      GET  /api/admin/usuarios")
    print("      POST /api/admin/usuarios")
    print("      PUT  /api/admin/usuarios/<id>")
    print("      DELETE /api/admin/usuarios/<id>")
    print("      GET  /api/admin/centros")
    print("      POST /api/admin/centros")
    print("      PUT  /api/admin/centros/<id>")
    print("      DELETE /api/admin/centros/<id>")
    print("      GET  /api/admin/estadisticas")
    print("=" * 60)
    print("👥 Usuarios disponibles:")
    print("   admin1 / admin123 (Administrador)")
    print("   diplomado1 / diplomado123 (Diplomado)")
    print("   tecnico1 / tecnico123 (Tecnico)")
    print("   micro1 / micro123 (Microbiologo)")
    print("   jefatura1 / jefatura123 (Jefatura)")
    print("=" * 60)
    
    print("Tipo de sangre disponibles:")
    print("      GET  /api/tipo_sangre/listar")
    print("=" * 60)
    print("Roles")
    print("      GET  /api/admin/roles")
    print("=" * 60)
    print("Inventario")
    print("      GET  /api/inventario/listar")
    print("=" * 60)

    app.run(
        debug=Config.DEBUG,
        host=Config.HOST,
        port=Config.PORT
    )