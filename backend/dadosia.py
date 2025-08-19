import json
from flask import Blueprint, jsonify, request
import os

# Cria o blueprint
dadosia_bp = Blueprint("dadosia", __name__)

# Caminho absoluto pro dashboard e contexto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_FILE = os.path.join(BASE_DIR, "dashboard.json")
API_CONTEXT_FILE = os.path.join(BASE_DIR, "api_context.txt")

@dadosia_bp.route("/api/dashboard", methods=["GET"])
def get_dashboard():
    """Retorna os dados atuais do dashboard como JSON."""
    if not os.path.exists(DASHBOARD_FILE):
        return jsonify({"error": "Nenhum dado processado ainda."}), 404
    with open(DASHBOARD_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)  # <-- carregando como dict
    return jsonify(data)

@dadosia_bp.route("/api-context", methods=["POST"])
def api_context():
    """Recebe dados do front e salva no backend para o agente."""
    payload = request.json
    try:
        with open(API_CONTEXT_FILE, "w", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False, indent=2))
        return jsonify({"msg": "Dados recebidos e salvos."})
    except Exception as e:
        return jsonify({"error": f"Falha ao salvar dados: {str(e)}"}), 500
