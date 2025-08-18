# Configurações da API de Reservas
import os
from dotenv import load_dotenv

load_dotenv()

API_CONFIG = {
    "BASE_URL": "https://artaxnet.com/pms-api/v1/bookings",
    "HEADERS": {
        "Accept": "application/json",
        "clientid": os.getenv("API_CLIENT_ID", "client_id_982dpzYGPfFHNG02o03vSY7HYlmL"),
        "clientsecret": os.getenv("API_CLIENT_SECRET", "client_secret_982N6kNMy8wCg2uFgVRc8eu")
    },
    "DEFAULT_PER_PAGE": 200,
    "TIMEOUT": 60
}