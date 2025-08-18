import os
import pandas as pd


def read_any_csv(path):
    """
    Lê um CSV de forma flexível, tentando diferentes separadores.
    """
    try:
        return pd.read_csv(path, sep=",")
    except Exception:
        try:
            return pd.read_csv(path, sep=";")
        except Exception as e:
            raise ValueError(f"Não foi possível ler o CSV {path}: {e}")


def load_qa_from_csv(path):
    df = read_any_csv(path)
    docs = [
        f"Pergunta: {row['pergunta']}\nResposta: {row['resposta']}"
        for _, row in df.iterrows()
    ]
    return docs


def load_uploaded_files(uploads_dir):
    texts = []
    if not os.path.exists(uploads_dir):
        return texts
    
    for filename in os.listdir(uploads_dir):
        filepath = os.path.join(uploads_dir, filename)
        if os.path.isfile(filepath):
            try:
                # Tenta ler como Excel/CSV primeiro
                if filename.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(filepath)
                    text = df.to_string()
                    texts.append(f"Arquivo: {filename}\n{text}")
                elif filename.endswith('.csv'):
                    df = read_any_csv(filepath)
                    text = df.to_string()
                    texts.append(f"Arquivo: {filename}\n{text}")
                else:
                    # Para outros tipos de arquivo, tenta ler como texto
                    with open(filepath, encoding="utf-8", errors='ignore') as f:
                        texts.append(f"Arquivo: {filename}\n{f.read()}")
            except Exception as e:
                print(f"Erro ao ler arquivo {filename}: {e}")
                continue
    return texts
