from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from qa_engine import setup_engine, answer_with_context
from qa_crud import router as qa_router
import uvicorn
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS Middleware (sempre antes das rotas)
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
    import csv, os
    from datetime import datetime
    log_path = "data/perguntas_sem_resposta.csv"
    existe = os.path.exists(log_path)
    with open(log_path, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(["data_hora", "pergunta", "resposta"])
        writer.writerow([datetime.now().isoformat(), pergunta, resposta])

# Pydantic model para a pergunta
class Query(BaseModel):
    pergunta: str

# Endpoint inteligente
@app.post("/ask")
def ask(query: Query):
    # Carrega dados atuais do dashboard
    dashboard_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'dashboard.json'))
    dashboard_data = None
    
    if os.path.exists(dashboard_path):
        import json
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            dashboard_data = json.load(f)
    
    # Carrega contexto da API
    api_context_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'api_context.txt'))
    api_context = None
    
    if os.path.exists(api_context_path):
        with open(api_context_path, 'r', encoding='utf-8') as f:
            api_context = f.read()
    
    resposta_obj = answer_with_context(index, query.pergunta, dashboard_data, api_context)
    resposta = str(resposta_obj.text) if hasattr(resposta_obj, "text") else str(resposta_obj)

    if "não sei" in resposta.lower() or "não tenho resposta" in resposta.lower():
        log_pergunta_sem_resposta(query.pergunta, resposta)

    return {"resposta": resposta}

# ========== NOVO ENDPOINT PARA RELOAD MANUAL ==========
@app.post("/reload")
def reload():
    reload_engine()
    print("Agente recarregado manualmente por API.")
    return {"ok": True}

# (Opcional) Servir frontend localmente. Em produção, não precisa!
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend"))
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
