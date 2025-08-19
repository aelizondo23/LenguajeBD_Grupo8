import os

class Config:
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'bloodcare_secret_key_2025')
    JWT_ACCESS_TOKEN_EXPIRES = 7 * 24 * 60 * 60  # 7 días
    
    # Base de datos Oracle
    DB_HOST = "172.20.10.4"
    DB_PORT = 1521
    DB_SERVICE = "orclpdb"
    DB_USER = "bloodcare"
    DB_PASSWORD = "123"
    
    # Flask
    DEBUG = True
    PORT = 5000
    HOST = '0.0.0.0'