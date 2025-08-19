import os
from dotenv import load_dotenv
from loader import load_qa_from_csv
load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
print("DEBUG: OPENAI_API_KEY =", openai_key)


class SimpleDoc:
    def __init__(self, text):
        self.text = text


class SimpleEngine:
    def __init__(self):
        try:
            qa_pairs = load_qa_from_csv("data/base.csv")
            self.knowledge_base = "\n".join(qa_pairs)
        except Exception:
            self.knowledge_base = "Base de conhecimento não disponível."

    def as_query_engine(self):
        return self

    def retrieve(self, query):
        # Sempre retorna um SimpleDoc com a base, pode ser melhorado futuramente
        return [SimpleDoc(self.knowledge_base)]


def setup_engine():
    print("Carregando agente IA simplificado...")
    return SimpleEngine()


def answer_with_context(index, pergunta, dashboard_data=None, api_context=None):
    """
    Retorna resposta do agente com base no dashboard, contexto da API e fallback local.
    Sempre retorna SimpleResponse(text)
    """
    class SimpleResponse:
        def __init__(self, text):
            self.text = text

    # Prepara contexto seguro
    dashboard_data = dashboard_data or {}
    api_context = api_context or ""

    dashboard_context = ""
    if dashboard_data:
        meses = ", ".join(dashboard_data.get("meses", []))
        dashboard_context = (
            f"DADOS DO DASHBOARD:\n"
            f"- Receita Total: R$ {dashboard_data.get('receita_total', 0):,.2f}\n"
            f"- Despesa Total: R$ {dashboard_data.get('despesa_total', 0):,.2f}\n"
            f"- Saldo: R$ {dashboard_data.get('saldo', 0):,.2f}\n"
            f"- Lucro Total: R$ {dashboard_data.get('lucro_total', 0):,.2f}\n"
            f"- Meses: {meses}"
        )

    system_prompt = (
        "Você é o assistente de IA do Hórus, especializado em gestão hoteleira e análise financeira. "
        "Responda de forma clara, objetiva e útil baseado nos dados fornecidos. Se não souber algo específico, diga que não sabe."
    )

    user_prompt = f"{dashboard_context}\n{api_context}\n\nPergunta do usuário: {pergunta}"

    # Chamada OpenAI segura
    if openai_key and pergunta.strip():
        import requests
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openai_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": 500,
                    "temperature": 0.7
                },
                timeout=20
            )
            if response.status_code == 200:
                result = response.json()
                return SimpleResponse(result['choices'][0]['message']['content'])
            else:
                print(f"[OpenAI Error] {response.status_code}: {response.text}")
        except Exception as e:
            print(f"[Erro conexão OpenAI] {e}")

    # Fallback offline
    pergunta_lower = pergunta.lower()
    if any(g in pergunta_lower for g in ["oi", "olá", "hello", "hi", "ola"]):
        resposta = "Olá! 😊 Sou o assistente do Hórus. Posso ajudar com análises financeiras e dados de reservas."
    elif "reserva" in pergunta_lower:
        total = "não disponível"
        import re
        match = re.search(r'Total de reservas: (\d+)', api_context)
        if match:
            total = match.group(1)
        resposta = f"Foram encontradas {total} reservas nos dados da API."        
    elif any(word in pergunta_lower for word in ["receita", "vendas", "faturamento"]):
        resposta = f"💰 Receita Total: R$ {dashboard_data.get('receita_total', 0):,.2f}"
    elif any(word in pergunta_lower for word in ["lucro", "resultado"]):
        resposta = f"📈 Lucro Total: R$ {dashboard_data.get('lucro_total', 0):,.2f}"
    elif "despesa" in pergunta_lower:
        resposta = f"📉 Despesas Totais: R$ {dashboard_data.get('despesa_total', 0):,.2f}"
    else:
        resposta = "🤖 Sistema Hórus Ativo. Pergunte sobre receitas, despesas, lucros ou reservas!"

    return SimpleResponse(resposta)
