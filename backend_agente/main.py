from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from qa_engine import setup_engine, answer_with_context
from qa_crud import router as qa_router
import uvicorn
import os
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Liberado para qualquer origem
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar as rotas de CRUD
app.include_router(qa_router)

# Carrega o index (engine) do RAG
index = setup_engine()

def reload_engine():
    global index
    index = setup_engine()

def log_pergunta_sem_resposta(pergunta, resposta):
    import csv
    from datetime import datetime
    log_path = "data/perguntas_sem_resposta.csv"
    existe = os.path.exists(log_path)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(["data_hora", "pergunta", "resposta"])
        writer.writerow([datetime.now().isoformat(), pergunta, resposta])

# Pydantic model para a pergunta
class Query(BaseModel):
    pergunta: str

# Configura a URL do backend
BACKEND_URL = os.getenv("BACKEND_URL", "https://horus-production.up.railway.app")

# Endpoint inteligente
@app.post("/ask")
def ask(query: Query):
    dashboard_data = None
    api_context = None

    # --- Busca dashboard via API ---
    try:
        resp = requests.get(f"{BACKEND_URL}/api/dashboard", timeout=5)
        if resp.status_code == 200:
            dashboard_data = resp.json()
        else:
            print(f"[WARN] Dashboard não encontrado: {resp.status_code}")
    except Exception as e:
        print(f"[ERROR] Falha ao buscar dashboard: {e}")

    # --- Busca contexto via API ---
    try:
        resp = requests.get(f"{BACKEND_URL}/api-context", timeout=5)
        if resp.status_code == 200:
            api_context = resp.json()
        else:
            print(f"[WARN] Contexto não encontrado: {resp.status_code}")
    except Exception as e:
        print(f"[ERROR] Falha ao buscar contexto: {e}")

    resposta_obj = answer_with_context(index, query.pergunta, dashboard_data, api_context)
    resposta = str(resposta_obj.text) if hasattr(resposta_obj, "text") else str(resposta_obj)

    if "não sei" in resposta.lower() or "não tenho resposta" in resposta.lower():
        log_pergunta_sem_resposta(query.pergunta, resposta)

    return {"resposta": resposta}

# Endpoint para reload manual
@app.post("/reload")
def reload():
    reload_engine()
    print("Agente recarregado manualmente por API.")
    return {"ok": True}

# Servir frontend localmente (opcional)
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend"))
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
