# backend/config.py

import os

# Caminho absoluto para a pasta raiz (backend)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Caminho absoluto para a pasta uploads
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
