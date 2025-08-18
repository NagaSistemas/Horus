from fastapi import APIRouter, HTTPException
import pandas as pd
import os
import unicodedata
from datetime import datetime
import csv

router = APIRouter()
DATA_PATH = "data/base.csv"
LOG_PATH = "data/qa_log.csv"

reload_engine_callback = None

def set_reload_engine_callback(cb):
    global reload_engine_callback
    reload_engine_callback = cb

def pergunta_normalizada(texto):
    texto = texto.lower().strip()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    return texto

def load_qa():
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(columns=["pergunta", "resposta"])
        df.to_csv(DATA_PATH, index=False)
    return pd.read_csv(DATA_PATH)

def save_qa(df):
    df.to_csv(DATA_PATH, index=False)

def log_alteracao(acao, idx, pergunta, resposta):
    existe = os.path.exists(LOG_PATH)
    with open(LOG_PATH, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(["acao", "data_hora", "idx", "pergunta", "resposta"])
        writer.writerow([acao, datetime.now().isoformat(), idx, pergunta, resposta])

@router.get("/qa")
def list_qa():
    return load_qa().to_dict(orient="records")

@router.post("/qa")
def add_qa(item: dict):
    pergunta = item.get("pergunta", "").strip()
    resposta = item.get("resposta", "").strip()
    if not pergunta or not resposta:
        raise HTTPException(400, detail="Pergunta e resposta não podem ser vazias.")
    df = load_qa()
    perguntas_existentes = [pergunta_normalizada(q) for q in df["pergunta"]]
    if pergunta_normalizada(pergunta) in perguntas_existentes:
        raise HTTPException(400, detail="Pergunta já existe na base.")
    new_idx = len(df)
    df = pd.concat([df, pd.DataFrame([{"pergunta": pergunta, "resposta": resposta}])], ignore_index=True)
    save_qa(df)
    log_alteracao("add", new_idx, pergunta, resposta)
    if reload_engine_callback:
        reload_engine_callback()
    return {"ok": True}

@router.put("/qa/{idx}")
def update_qa(idx: int, item: dict):
    pergunta = item.get("pergunta", "").strip()
    resposta = item.get("resposta", "").strip()
    if not pergunta or not resposta:
        raise HTTPException(400, detail="Pergunta e resposta não podem ser vazias.")
    df = load_qa()
    if idx < 0 or idx >= len(df):
        raise HTTPException(404)
    # Checa duplicidade (exceto na própria linha que está editando)
    perguntas_existentes = [pergunta_normalizada(q) for i, q in enumerate(df["pergunta"]) if i != idx]
    if pergunta_normalizada(pergunta) in perguntas_existentes:
        raise HTTPException(400, detail="Pergunta já existe na base.")
    # Log do antigo
    log_alteracao("edit", idx, df.at[idx, "pergunta"], df.at[idx, "resposta"])
    df.at[idx, "pergunta"] = pergunta
    df.at[idx, "resposta"] = resposta
    save_qa(df)
    if reload_engine_callback:
        reload_engine_callback()
    return {"ok": True}

@router.delete("/qa/{idx}")
def delete_qa(idx: int):
    df = load_qa()
    if idx < 0 or idx >= len(df):
        raise HTTPException(404)
    # Log do registro antes de apagar
    log_alteracao("delete", idx, df.at[idx, "pergunta"], df.at[idx, "resposta"])
    df = df.drop(idx).reset_index(drop=True)
    save_qa(df)
    if reload_engine_callback:
        reload_engine_callback()
    return {"ok": True}
