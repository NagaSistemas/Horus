from flask import jsonify, request
from flask import jsonify
import time
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import pandas as pd
from myutils import process_financial_data, process_reservations_data
import json
from myutils import buscar_coluna, COLUNAS_ALIAS
from dadosia import dadosia_bp  # importa o blueprint
import calendar
import re

# Configurações de caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_FOLDER = os.path.join(BASE_DIR, 'frontend')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
DASHBOARD_DATA_FILE = os.path.join(BASE_DIR, 'dashboard.json')
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

print(
    f"[DEBUG] FRONTEND_FOLDER={FRONTEND_FOLDER}, exists={os.path.isdir(FRONTEND_FOLDER)}")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Flask
app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.register_blueprint(dadosia_bp)

# --- Funções utilitárias ---


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_dashboard_data(result):
    """Salva os dados processados para acesso futuro sem upload."""
    with open(DASHBOARD_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def load_dashboard_data():
    """Carrega o dashboard salvo, caso exista."""
    if os.path.exists(DASHBOARD_DATA_FILE):
        with open(DASHBOARD_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

# --- Rotas frontend estático ---


@app.route('/')
def index():
    return send_from_directory(FRONTEND_FOLDER, 'index.html')


@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(FRONTEND_FOLDER, 'css'), filename)


@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(FRONTEND_FOLDER, 'js'), filename)

# --- Upload e processamento ---


@app.route('/upload/<data_type>', methods=['POST'])
def upload_file(data_type):
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado.'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio.'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Formato de arquivo não suportado.'}), 400

    filename = secure_filename(file.filename)
    upload_folder = app.config['UPLOAD_FOLDER']
    filepath = os.path.join(upload_folder, filename)

    # ---- NOVO: impede sobrescrita ----
    if os.path.exists(filepath):
        name, ext = os.path.splitext(filename)
        i = 1
        # incrementa até achar um nome livre
        while os.path.exists(os.path.join(upload_folder, f"{name}_{i}{ext}")):
            i += 1
        filename = f"{name}_{i}{ext}"
        filepath = os.path.join(upload_folder, filename)
    # ---- FIM do NOVO bloco ----

    file.save(filepath)
    ext = filename.rsplit('.', 1)[1].lower()
    try:
        if ext in ['xlsx', 'xls']:
            df = pd.read_excel(filepath)
        else:
            from myutils import read_any_csv
            df = read_any_csv(filepath)
    except Exception as e:
        return jsonify({'error': f'Erro ao ler arquivo: {str(e)}'}), 400

    if data_type == 'financial':
        result = process_financial_data(df)
        save_dashboard_data(result)
        # Notifica o agente de IA sobre os novos dados
        try:
            import requests
            requests.post('https://perceptive-essence-production.up.railway.app/reload', timeout=2)
        except:
            pass  # Ignora se o agente não estiver rodando
    elif data_type == 'reservations':
        result = process_reservations_data(df)
        # save_dashboard_data(result)
    else:
        return jsonify({'error': 'Tipo de dado inválido.'}), 400
    return jsonify(result)

# --- API para buscar último dashboard processado ---


@app.route('/api/dashboard', methods=['GET'])
def api_dashboard():
    data = load_dashboard_data()
    if data:
        return jsonify(data)
    else:
        return jsonify({'error': 'Nenhum dado processado ainda.'}), 404

# --- Health check ---


@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({'status': 'ok', 'message': 'Backend Horus rodando!'}), 200


# --- API: Lista de arquivos enviados ---


@app.route('/api/lista-arquivos', methods=['GET'])
def lista_arquivos():
    arquivos = []
    pasta = app.config['UPLOAD_FOLDER']
    for nome in os.listdir(pasta):
        caminho = os.path.join(pasta, nome)
        if os.path.isfile(caminho):
            stat = os.stat(caminho)
            arquivos.append({
                "nome": nome,
                "data_upload": time.strftime('%Y-%m-%d %H:%M', time.localtime(stat.st_ctime)),
                "data_modificacao": time.strftime('%Y-%m-%d %H:%M', time.localtime(stat.st_mtime)),
                "tamanho": stat.st_size
            })
    arquivos.sort(key=lambda a: a['data_upload'], reverse=True)
    return jsonify(arquivos)

# --- API: Download de arquivo específico ---


@app.route('/api/download-arquivo/<nome>', methods=['GET'])
def download_arquivo(nome):
    nome = secure_filename(nome)
    return send_from_directory(app.config['UPLOAD_FOLDER'], nome, as_attachment=True)

# ------API:  rota Flask para processar o arquivo e atualizar o dashboard------


@app.route('/api/usefile/<nome_arquivo>', methods=['GET'])
def usar_arquivo(nome_arquivo):
    import pandas as pd
    from werkzeug.utils import secure_filename
    nome_arquivo = secure_filename(nome_arquivo)
    caminho = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo)
    if not os.path.exists(caminho):
        return jsonify({'error': 'Arquivo não encontrado'}), 404

    ext = nome_arquivo.rsplit('.', 1)[-1].lower()
    try:
        if ext in ['xlsx', 'xls']:
            df = pd.read_excel(caminho)
        else:
            from myutils import read_any_csv
            df = read_any_csv(caminho)
    except Exception as e:
        return jsonify({'error': f'Erro ao ler arquivo: {str(e)}'}), 400

    # Processa o arquivo
    result = process_financial_data(df)
    save_dashboard_data(result)
    
    # Notifica o agente de IA sobre os novos dados
    try:
        import requests
        requests.post('https://perceptive-essence-production.up.railway.app/reload', timeout=2)
    except:
        pass  # Ignora se o agente não estiver rodando
        
    return jsonify(result)


@app.route('/api/comparar-relatorios', methods=['POST'])
def comparar_relatorios():
    data = request.get_json()
    arquivos = data.get('arquivos', [])
    if not (2 <= len(arquivos) <= 6):
        return jsonify({'error': 'Selecione de 2 a 6 arquivos para comparar!'}), 400

    from myutils import buscar_coluna, COLUNAS_ALIAS
    padronizados = []
    nomes_metricas = ['Receita', 'Meta', 'Despesa', 'Lucro']
    nomes_padrao = {
        'Receita': 'vendas',
        'Meta': 'meta_vendas',
        'Despesa': 'despesas',
        'Lucro': 'lucro_mensal'
    }

    # 1. Padroniza cada arquivo para [Mês, Receita, Meta, Despesa, Lucro] com nome sufixado
    for nome_arquivo in arquivos:
        caminho = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo)
        ext = nome_arquivo.rsplit('.', 1)[-1].lower()
        if ext in ['xlsx', 'xls']:
            df = pd.read_excel(caminho)
        else:
            from myutils import read_any_csv
            df = read_any_csv(caminho)

        mes_col = buscar_coluna(df, COLUNAS_ALIAS['mes'])
        if not mes_col:
            return jsonify({'error': f'Coluna de mês não encontrada em {nome_arquivo}'}), 400

        novo = pd.DataFrame()
        novo['Mês'] = df[mes_col].astype(str)
        for metrica, alias in nomes_padrao.items():
            metrica_col = buscar_coluna(df, COLUNAS_ALIAS[alias])
            if metrica_col:
                novo[f'{metrica}_{nome_arquivo}'] = pd.to_numeric(
                    df[metrica_col], errors='coerce')
            else:
                # Preenche zero se não achar
                novo[f'{metrica}_{nome_arquivo}'] = 0

        padronizados.append(novo)

    # 2. Merge por mês de todos os DataFrames
    dfc = padronizados[0]
    for df_next in padronizados[1:]:
        dfc = pd.merge(dfc, df_next, on='Mês', how='outer')

    dfc = dfc.fillna(0)

    # 3. Para cada métrica, calcula maior/menor/média/diferença/percentual para o mês
    for metrica in nomes_metricas:
        colunas_metricas = [f'{metrica}_{nome}' for nome in arquivos]
        # Absoluto
        dfc[f'{metrica}_maior'] = dfc[colunas_metricas].max(axis=1)
        dfc[f'{metrica}_menor'] = dfc[colunas_metricas].min(axis=1)
        dfc[f'{metrica}_dif'] = dfc[f'{metrica}_maior'] - \
            dfc[f'{metrica}_menor']
        # Percentual
        dfc[f'{metrica}_perc'] = dfc.apply(
            lambda row: (100 * row[f'{metrica}_dif'] / row[f'{metrica}_menor']
                         ) if row[f'{metrica}_menor'] != 0 else 0,
            axis=1
        )

        import calendar
    import re

    def ordena_mes(val):
        val = str(val).strip()
        
        # Se for apenas um número (ano), retorna como tal
        if val.isdigit() and len(val) == 4:
            return int(val) * 100
        
        # Dicionário de meses em português
        meses = {
            'janeiro': 1, 'jan': 1,
            'fevereiro': 2, 'fev': 2,
            'março': 3, 'mar': 3,
            'abril': 4, 'abr': 4,
            'maio': 5, 'mai': 5,
            'junho': 6, 'jun': 6,
            'julho': 7, 'jul': 7,
            'agosto': 8, 'ago': 8,
            'setembro': 9, 'set': 9,
            'outubro': 10, 'out': 10,
            'novembro': 11, 'nov': 11,
            'dezembro': 12, 'dez': 12
        }
        
        val_lower = val.lower()
        
        # Procura por nome de mês
        for nome_mes, num_mes in meses.items():
            if nome_mes in val_lower:
                # Procura por ano no texto
                ano_match = re.search(r'(\d{4})', val)
                if ano_match:
                    ano = int(ano_match.group(1))
                else:
                    # Se não encontrar ano, usa 2024 como padrão
                    ano = 2024
                return ano * 100 + num_mes
        
        # Se não encontrou mês, tenta extrair ano
        ano_match = re.search(r'(\d{4})', val)
        if ano_match:
            return int(ano_match.group(1)) * 100
            
        return 999999

    dfc['__ordem__'] = dfc['Mês'].map(ordena_mes)
    dfc = dfc.sort_values('__ordem__').drop(columns=['__ordem__'])
    # --- FIM DO BLOCO DE ORDENAÇÃO ---

    # 4. Retorna tabela
    resultado = dfc.to_dict(orient='records')
    return jsonify({
        "arquivos": arquivos,
        "colunas_metricas": nomes_metricas,
        "dados": resultado
    })


@app.route('/uploads', methods=['GET'])
def list_uploaded_files():
    arquivos = []
    pasta = app.config['UPLOAD_FOLDER']
    for nome in os.listdir(pasta):
        caminho = os.path.join(pasta, nome)
        if os.path.isfile(caminho):
            stat = os.stat(caminho)
            arquivos.append({
                "name": nome,
                "uploaded_at": time.strftime('%Y-%m-%d %H:%M', time.localtime(stat.st_ctime)),
                "modified_at": time.strftime('%Y-%m-%d %H:%M', time.localtime(stat.st_mtime)),
                "size": f"{stat.st_size / 1024:.1f} KB"
            })
    arquivos.sort(key=lambda a: a['uploaded_at'], reverse=True)
    return jsonify({'files': arquivos})

@app.route('/uploads/<nome>', methods=['DELETE'])
def delete_file(nome):
    nome = secure_filename(nome)
    caminho = os.path.join(app.config['UPLOAD_FOLDER'], nome)
    if not os.path.exists(caminho):
        return jsonify({'error': 'Arquivo não encontrado'}), 404
    try:
        os.remove(caminho)
        return jsonify({'success': True, 'message': f'Arquivo {nome} excluído com sucesso'})
    except Exception as e:
        return jsonify({'error': f'Erro ao excluir arquivo: {str(e)}'}), 500

@app.route('/api/fetch-reservas', methods=['POST'])
def fetch_reservas_api():
    import requests
    from urllib.parse import urlencode
    from api_config import API_CONFIG
    
    data = request.get_json()
    
    # Parâmetros da API
    BASE_URL = API_CONFIG["BASE_URL"]
    params = {
        "per_page": data.get('per_page', API_CONFIG["DEFAULT_PER_PAGE"]),
        "include": "financial,rates,rooms,pricing",  # Tenta incluir dados financeiros
        "expand": "all",  # Expande todos os campos
        "with_financial": "true",  # Força inclusão de dados financeiros
        "detailed": "true"  # Dados detalhados
    }
    
    # Adiciona filtros opcionais
    for field in ['period_one', 'period_two', 'status', 'guest', 'booking_id', 'checkin', 'checkout', 'created']:
        if data.get(field):
            params[field] = data[field]
    
    # Usa credenciais do arquivo de configuração
    headers = API_CONFIG["HEADERS"].copy()
    
    try:
        print(f"[DEBUG] Fazendo requisição para: {BASE_URL}")
        print(f"[DEBUG] Parâmetros: {params}")
        print(f"[DEBUG] Headers: {headers}")
        
        all_bookings = []
        url = f"{BASE_URL}?{urlencode(params)}"
        
        print(f"[DEBUG] URL completa: {url}")
        
        while url:
            print(f"[DEBUG] Requisição para: {url}")
            resp = requests.get(url, headers=headers, timeout=API_CONFIG["TIMEOUT"])
            print(f"[DEBUG] Status code: {resp.status_code}")
            print(f"[DEBUG] Response headers: {dict(resp.headers)}")
            
            if resp.status_code != 200:
                print(f"[DEBUG] Erro na resposta: {resp.text}")
                return jsonify({'error': f'API retornou status {resp.status_code}: {resp.text}'}), resp.status_code
            
            api_data = resp.json()
            print(f"[DEBUG] Estrutura da resposta: {list(api_data.keys())}")
            
            bookings = api_data.get("bookings", [])
            print(f"[DEBUG] Encontradas {len(bookings)} reservas nesta página")
            
            all_bookings.extend(bookings)
            url = api_data.get("next_page")
            print(f"[DEBUG] Próxima página: {url}")
        
        # Captura metadados da primeira página
        first_page_data = None
        if all_bookings:
            # Faz nova requisição para capturar metadados
            first_resp = requests.get(f"{BASE_URL}?{urlencode(params)}", headers=headers, timeout=API_CONFIG["TIMEOUT"])
            if first_resp.status_code == 200:
                first_page_data = first_resp.json()
        
        # Converte para DataFrame e processa
        df = pd.DataFrame(all_bookings)
        result = process_reservations_data(df)
        
        # Gera nome do arquivo baseado no período
        period_start = data.get('period_one', 'inicio').replace('-', '')
        period_end = data.get('period_two', 'fim').replace('-', '')
        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reservas_API_{period_start}_{period_end}_{timestamp}.csv"
        
        # Salva como arquivo CSV na pasta uploads
        csv_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not df.empty:
            # Adiciona metadados como cabeçalho
            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                if first_page_data:
                    f.write(f"# METADADOS DA API\n")
                    f.write(f"# Total de Reservas: {first_page_data.get('total_bookings', 0)}\n")
                    f.write(f"# Total de Páginas: {first_page_data.get('total_pages', 0)}\n")
                    f.write(f"# Página Atual: {first_page_data.get('current_page', 1)}\n")
                    f.write(f"# Período: {data.get('period_one', 'N/A')} a {data.get('period_two', 'N/A')}\n")
                    f.write(f"# Data de Extração: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"#\n")
                
                # Salva os dados
                df.to_csv(f, index=False)
        else:
            # Arquivo vazio com metadados
            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write(f"# METADADOS DA API\n")
                if first_page_data:
                    f.write(f"# Total de Reservas: {first_page_data.get('total_bookings', 0)}\n")
                    f.write(f"# Total de Páginas: {first_page_data.get('total_pages', 0)}\n")
                f.write(f"# Período: {data.get('period_one', 'N/A')} a {data.get('period_two', 'N/A')}\n")
                f.write(f"# Nenhuma reserva encontrada no período\n")
        
        # Salva contexto para o agente IA
        total_bookings_api = first_page_data.get('total_bookings', len(all_bookings)) if first_page_data else len(all_bookings)
        total_pages = first_page_data.get('total_pages', 1) if first_page_data else 1
        
        context_text = f"""
DADOS DE RESERVAS DA API:
Arquivo salvo: {filename}
Período: {data.get('period_one', 'N/A')} até {data.get('period_two', 'N/A')}
Total de reservas no sistema: {total_bookings_api}
Total de páginas: {total_pages}
Reservas carregadas nesta consulta: {len(all_bookings)}
Última atualização: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

Resumo dos dados:
{df.describe().to_string() if not df.empty else 'Nenhum dado encontrado'}
"""
        
        # Salva contexto
        context_file = os.path.join(BASE_DIR, 'api_context.txt')
        with open(context_file, 'w', encoding='utf-8') as f:
            f.write(context_text)
        
        # Notifica agente IA
        try:
            requests.post('https://perceptive-essence-production.up.railway.app/reload', timeout=2)
        except:
            pass
        
        return jsonify({
            'success': True,
            'message': f'{len(all_bookings)} reservas processadas e salvas como {filename}',
            'total_reservas': len(all_bookings),
            'filename': filename,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar dados da API: {str(e)}'}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Railway define a porta
    app.run(host="0.0.0.0", port=port, debug=True)
