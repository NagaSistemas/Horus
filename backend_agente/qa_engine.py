import os
from dotenv import load_dotenv

from loader import load_qa_from_csv, load_uploaded_files
from llama_index.core.schema import Document
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
print("DEBUG: OPENAI_API_KEY =", os.getenv("OPENAI_API_KEY"))


class SimpleEngine:
    def __init__(self):
        # Carrega dados estáticos
        try:
            qa_pairs = load_qa_from_csv("data/base.csv")
            self.knowledge_base = "\n".join(qa_pairs)
        except:
            self.knowledge_base = "Base de conhecimento não disponível."
    
    def as_query_engine(self):
        return self
    
    def retrieve(self, query):
        return [SimpleDoc(self.knowledge_base)]
        
class SimpleDoc:
    def __init__(self, text):
        self.text = text

def setup_engine():
    print("Carregando agente IA simplificado...")
    return SimpleEngine()


# NOVA FUNÇÃO:


def answer_with_context(index, pergunta, dashboard_data=None, api_context=None):
    # Monta contexto completo
    dashboard_context = ""
    if dashboard_data:
        dashboard_context = f"""
DADOS ATUAIS DO DASHBOARD:
- Receita Total: R$ {dashboard_data.get('receita_total', 0):,.2f}
- Despesa Total: R$ {dashboard_data.get('despesa_total', 0):,.2f}
- Saldo: R$ {dashboard_data.get('saldo', 0):,.2f}
- Lucro Total: R$ {dashboard_data.get('lucro_total', 0):,.2f}
- Mêses: {', '.join(dashboard_data.get('meses', []))}
"""
    
    api_context_text = ""
    if api_context:
        api_context_text = f"\n{api_context}"

    # Usa requisição HTTP direta para OpenAI
    import requests
    import json
    
    system_prompt = "Você é o assistente de IA do Hórus, especializado em gestão hoteleira e análise financeira. Responda de forma clara, objetiva e útil baseado nos dados fornecidos. Se não souber algo específico, diga que não sabe."
    
    user_prompt = f"""{dashboard_context}{api_context_text}

Pergunta do usuário: {pergunta}"""

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {openai_key}",
                "Content-Type": "application/json"
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
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            resposta_text = result['choices'][0]['message']['content']
            
            class SimpleResponse:
                def __init__(self, text):
                    self.text = text
            
            return SimpleResponse(resposta_text)
        else:
            error_detail = response.text
            print(f"Erro OpenAI {response.status_code}: {error_detail}")
            
            # Resposta inteligente baseada nos dados
            if "reservas" in pergunta.lower():
                if "API" in api_context_text:
                    resposta = "Com base nos dados da API de reservas carregados, verifique o contexto da API acima para informações sobre reservas."
                else:
                    resposta = "Não há dados de reservas carregados no momento. Use o botão 'Buscar Reservas' no dashboard para carregar dados da API."
            elif any(word in pergunta.lower() for word in ['receita', 'vendas', 'lucro', 'despesa']):
                resposta = f"Com base nos dados do dashboard: Receita total de R$ {dashboard_data.get('receita_total', 0):,.2f}, Despesas de R$ {dashboard_data.get('despesa_total', 0):,.2f}, resultando em um lucro de R$ {dashboard_data.get('lucro_total', 0):,.2f}."
            else:
                resposta = "Olá! Sou o assistente do Hórus. Posso ajudar com análises financeiras e dados de reservas. Como posso ajudar?"
            
            class SimpleResponse:
                def __init__(self, text):
                    self.text = text
            
            return SimpleResponse(resposta)
            
    except Exception as e:
        print(f"Erro de conexão: {e}")
        
        # Resposta inteligente offline
        if "reservas" in pergunta.lower():
            if "Total de reservas:" in api_context_text:
                import re
                match = re.search(r'Total de reservas: (\d+)', api_context_text)
                if match:
                    total = match.group(1)
                    resposta = f"Foram encontradas {total} reservas nos dados da API carregados."
                else:
                    resposta = "Dados de reservas carregados. Verifique os detalhes no contexto da API."
            else:
                resposta = "Não há dados de reservas carregados. Use 'Buscar Reservas' no dashboard para carregar dados da API."
        elif pergunta.lower() in ['oi', 'olá', 'hello', 'hi', 'ola']:
            resposta = "Olá! 😊 Sou o assistente do Hórus. Posso ajudar com:\n\n• Análises financeiras\n• Dados de reservas\n• Relatórios comparativos\n\nComo posso ajudar?"
        elif any(word in pergunta.lower() for word in ['receita', 'vendas', 'faturamento']):
            if dashboard_data:
                resposta = f"💰 **Receita Total:** R$ {dashboard_data.get('receita_total', 0):,.2f}\n\nEsta é a receita total baseada nos dados carregados no dashboard."
            else:
                resposta = "Não há dados financeiros carregados no momento."
        elif any(word in pergunta.lower() for word in ['lucro', 'resultado']):
            if dashboard_data:
                resposta = f"📈 **Lucro Total:** R$ {dashboard_data.get('lucro_total', 0):,.2f}\n\n**Detalhamento:**\n• Receita: R$ {dashboard_data.get('receita_total', 0):,.2f}\n• Despesas: R$ {dashboard_data.get('despesa_total', 0):,.2f}\n• Saldo: R$ {dashboard_data.get('saldo', 0):,.2f}"
            else:
                resposta = "Não há dados financeiros carregados no momento."
        elif "despesa" in pergunta.lower():
            if dashboard_data:
                resposta = f"📉 **Despesas Totais:** R$ {dashboard_data.get('despesa_total', 0):,.2f}\n\nEste valor representa o total de despesas nos dados carregados."
            else:
                resposta = "Não há dados de despesas carregados no momento."
        else:
            resposta = f"🤖 **Sistema Hórus Ativo**\n\n{dashboard_context.strip()}\n\n💡 **Dica:** Pergunte sobre receitas, despesas, lucros ou reservas!"
        
        class SimpleResponse:
            def __init__(self, text):
                self.text = text
        
        return SimpleResponse(resposta)
