import os
import requests
from dotenv import load_dotenv

load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

print(f"Testando chave OpenAI: {openai_key[:20]}...")

try:
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {openai_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Diga apenas 'funcionando'"}],
            "max_tokens": 10
        },
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ OpenAI funcionando!")
        print("Resposta:", result['choices'][0]['message']['content'])
    else:
        print(f"❌ Erro {response.status_code}: {response.text}")
        
except Exception as e:
    print(f"❌ Erro de conexão: {e}")