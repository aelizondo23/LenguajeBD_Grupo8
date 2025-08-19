from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config

# Importar blueprints
from auth import auth_bp
from donantes import donantes_bp
from donaciones import donaciones_bp
from admin import admin_bp

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
    
    app.run(
        debug=Config.DEBUG,
        host=Config.HOST,
        port=Config.PORT
    )