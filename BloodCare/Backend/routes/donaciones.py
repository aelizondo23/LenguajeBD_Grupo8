from flask import Blueprint, jsonify

donaciones_bp = Blueprint("donaciones", __name__)

@donaciones_bp.route("/", methods=["GET"])
def listar_donaciones():
    donaciones = [
        {"id": 1, "fecha": "2025-07-01", "volumen": 450, "estado": "aceptada"},
        {"id": 2, "fecha": "2025-07-03", "volumen": 420, "estado": "rechazada"}
    ]
    return jsonify(donaciones)
