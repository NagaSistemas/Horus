import pandas as pd
import numpy as np

def read_any_csv(filepath):
    """
    Tenta ler CSV com diferentes combinações de encoding e separador.
    Ordem: utf-8 vírgula, latin1 vírgula, utf-8 ponto-vírgula, latin1 ponto-vírgula
    """
    combinacoes = [
        {'encoding': 'utf-8', 'sep': ','},
        {'encoding': 'latin1', 'sep': ','},
        {'encoding': 'utf-8', 'sep': ';'},
        {'encoding': 'latin1', 'sep': ';'}
    ]
    
    for combo in combinacoes:
        try:
            df = pd.read_csv(filepath, **combo)
            # Verifica se leu corretamente (mais de 1 coluna ou dados válidos)
            if len(df.columns) > 1 or (len(df.columns) == 1 and len(df) > 0):
                return df
        except Exception:
            continue
    
    # Se nenhuma combinação funcionou, tenta leitura padrão
    return pd.read_csv(filepath)

# Dicionário com aliases (sinônimos) para cada campo importante FINANCEIRO
COLUNAS_ALIAS = {
    "mes": ["Mês", "Mes", "Competência", "Data", "Periodo", "P. Cs. Zanotto"],
    "vendas": ["Vendas", "Venda", "Faturamento", "Receita", "Receitas"],
    "meta_vendas": ["META VENDAS", "Meta Venda", "Meta Faturamento"],
    "despesas": ["Despesas", "Despesa", "Gastos", "Saídas", "Saida"],
    "meta_despesas": ["META DESPESAS", "Meta Despesa", "Meta Gastos"],
    "lucro_mensal": ["Lucro Mensal", "Lucro", "Resultado Mensal", "Resultado"],
    "reserva_cx": ["RESERVA CX 10%", "Reserva", "Reserva Caixa"],
    "soma_lucros": ["soma dos lucros", "Acumulado Lucro", "Lucro Acumulado"],
    "margem_lucro_mensal": ["margem de lucro mensal", "Margem Mensal", "Margem Lucro Mensal"],
    "margem_lucro_geral": ["margem de lucro geral", "Margem Lucro Geral"],
    "crescimento_anual": ["cresc. lucro anual 2025=2025/2024", "Crescimento Anual", "Crescimento Lucro"],
}


def buscar_coluna(df, aliases):
    """
    Busca a coluna mais próxima (por nome ou aproximação) dentre os aliases definidos.
    Corrigido: converte todos os nomes para string antes de aplicar lower/strip.
    """
    cols = {str(c).lower().strip(): c for c in df.columns}
    for alias in aliases:
        nome = alias.lower().strip()
        if nome in cols:
            return cols[nome]
        for col in cols:
            if nome in col or col in nome:
                return cols[col]
    return None  # Não achou


def safe_numeric(series):
    return pd.to_numeric(series, errors='coerce').fillna(0).tolist()


def process_financial_data(df):
    """
    Processa um DataFrame flexível (de XLSX ou CSV) para alimentar o dashboard.
    """
    # 1. Procurar cada campo-chave usando o dicionário de aliases
    campos = {}
    for campo, aliases in COLUNAS_ALIAS.items():
        col = buscar_coluna(df, aliases)
        campos[campo] = col

    # 2. Extrair os arrays de dados
    meses = df.get(campos["mes"], pd.Series(dtype=str)
                   ).astype(str).fillna("").tolist()
    vendas = safe_numeric(df.get(campos["vendas"], pd.Series()))
    meta_vendas = safe_numeric(df.get(campos["meta_vendas"], pd.Series()))
    despesas = safe_numeric(df.get(campos["despesas"], pd.Series()))
    meta_despesas = safe_numeric(df.get(campos["meta_despesas"], pd.Series()))
    lucro_mensal = safe_numeric(df.get(campos["lucro_mensal"], pd.Series()))
    reserva_cx = safe_numeric(df.get(campos["reserva_cx"], pd.Series()))
    soma_lucros = safe_numeric(df.get(campos["soma_lucros"], pd.Series()))
    margem_lucro_mensal = safe_numeric(
        df.get(campos["margem_lucro_mensal"], pd.Series()))
    margem_lucro_geral = safe_numeric(
        df.get(campos["margem_lucro_geral"], pd.Series()))
    crescimento_anual = safe_numeric(
        df.get(campos["crescimento_anual"], pd.Series()))

    # 3. Limpeza
    def limpa(arr):
        return [x for x in arr if str(x).strip() not in ["", "nan", "None", "NaT"]]

    meses = limpa(meses)
    vendas = limpa(vendas)
    meta_vendas = limpa(meta_vendas)
    despesas = limpa(despesas)
    meta_despesas = limpa(meta_despesas)
    lucro_mensal = limpa(lucro_mensal)
    reserva_cx = limpa(reserva_cx)
    soma_lucros = limpa(soma_lucros)
    margem_lucro_mensal = limpa(margem_lucro_mensal)
    margem_lucro_geral = limpa(margem_lucro_geral)
    crescimento_anual = limpa(crescimento_anual)

    # 4. Cálculos para KPIs/cards
    receita_total = float(np.nansum(vendas)) if vendas else 0
    despesa_total = float(np.nansum(despesas)) if despesas else 0
    lucro_total = float(np.nansum(lucro_mensal)) if lucro_mensal else 0
    reserva_total = float(np.nansum(reserva_cx)) if reserva_cx else 0
    saldo = receita_total - despesa_total
    meta_vendas_total = float(np.nansum(meta_vendas)) if meta_vendas else 0
    meta_despesas_total = float(
        np.nansum(meta_despesas)) if meta_despesas else 0
    margem_lucro_geral_atual = float(
        margem_lucro_geral[-1]) if margem_lucro_geral else 0
    crescimento_anual_atual = float(
        crescimento_anual[-1]) if crescimento_anual else 0

    # 5. Montar tabela mês a mês (aproveita os dados disponíveis)
    dados_tabela = []
    total_meses = max(
        [len(meses), len(vendas), len(despesas), len(lucro_mensal)])
    for i in range(total_meses):
        dados_tabela.append({
            "mes": meses[i] if i < len(meses) else "",
            "vendas": vendas[i] if i < len(vendas) else 0,
            "meta_vendas": meta_vendas[i] if i < len(meta_vendas) else 0,
            "despesas": despesas[i] if i < len(despesas) else 0,
            "meta_despesas": meta_despesas[i] if i < len(meta_despesas) else 0,
            "lucro_mensal": lucro_mensal[i] if i < len(lucro_mensal) else 0,
            "reserva_cx": reserva_cx[i] if i < len(reserva_cx) else 0,
            "soma_lucros": soma_lucros[i] if i < len(soma_lucros) else 0,
            "margem_lucro_mensal": margem_lucro_mensal[i] if i < len(margem_lucro_mensal) else 0,
            "margem_lucro_geral": margem_lucro_geral[i] if i < len(margem_lucro_geral) else 0,
            "crescimento_anual": crescimento_anual[i] if i < len(crescimento_anual) else 0,
        })

    # 6. Exemplo de distribuição de vendas (adaptável)
    if receita_total > 0:
        distribuicao_vendas = [round(100 * v / receita_total, 1)
                               for v in vendas[:5]]
    else:
        distribuicao_vendas = [0 for _ in range(5)]

    # 7. Retorno JSON amigável para o frontend
    return {
        "meses": meses,
        "receita_por_mes": vendas,
        "meta_vendas": meta_vendas,
        "despesa_por_mes": despesas,
        "meta_despesas": meta_despesas,
        "lucro_mensal": lucro_mensal,
        "reserva_cx": reserva_cx,
        "soma_lucros": soma_lucros,
        "margem_lucro_mensal": margem_lucro_mensal,
        "margem_lucro_geral": margem_lucro_geral,
        "margem_lucro_geral_atual": margem_lucro_geral_atual,
        "crescimento_anual": crescimento_anual,
        "crescimento_anual_atual": crescimento_anual_atual,
        "receita_total": receita_total,
        "despesa_total": despesa_total,
        "saldo": saldo,
        "lucro_total": lucro_total,
        "reserva_total": reserva_total,
        "meta_vendas_total": meta_vendas_total,
        "meta_despesas_total": meta_despesas_total,
        "dados_tabela": dados_tabela,
        "distribuicao_vendas": distribuicao_vendas,
        "campos_detectados": {k: v for k, v in campos.items() if v}
    }

# ---------- NOVO: Processamento de planilhas de reservas ----------


def process_reservations_data(df):
    """
    Processa DataFrame de reservas em formato flexível, aceitando nomes variados de colunas.
    Retorna JSON estruturado para alimentar dashboards/tabelas.
    """

    # Aliases para possíveis nomes de colunas
    COLUNAS_RESERVA = {
        "data": ["Data", "data", "Check-in", "Checkin", "Entrada"],
        "cliente": ["Cliente", "Nome", "Hóspede", "Hospede", "Guest"],
        "status": ["Status", "Situação", "Confirmada", "Cancelada", "Pendente"],
        "valor": ["Valor", "Total", "Preço", "Preco", "Amount", "R$"],
        "origem": ["Origem", "Canal", "Fonte", "Plataforma", "OTA"]
    }

    def buscar_col(df, aliases):
        cols = {str(c).lower().strip(): c for c in df.columns}
        for alias in aliases:
            nome = alias.lower().strip()
            if nome in cols:
                return cols[nome]
            for col in cols:
                if nome in col or col in nome:
                    return cols[col]
        return None

    campos = {campo: buscar_col(df, aliases)
              for campo, aliases in COLUNAS_RESERVA.items()}

    # Extrair arrays
    datas = df.get(campos["data"], pd.Series(dtype=str)
                   ).astype(str).fillna("").tolist()
    clientes = df.get(campos["cliente"], pd.Series(
        dtype=str)).astype(str).fillna("").tolist()
    status = df.get(campos["status"], pd.Series(
        dtype=str)).astype(str).fillna("").tolist()
    valores = pd.to_numeric(
        df.get(campos["valor"], pd.Series()), errors='coerce').fillna(0).tolist()
    origens = df.get(campos["origem"], pd.Series(
        dtype=str)).astype(str).fillna("").tolist()

    # Limpeza rápida
    def limpa(arr):
        return [x for x in arr if str(x).strip() not in ["", "nan", "None", "NaT"]]

    datas = limpa(datas)
    clientes = limpa(clientes)
    status = limpa(status)
    valores = limpa(valores)
    origens = limpa(origens)

    # KPIs
    total_reservas = len(datas)
    total_confirmadas = sum(
        1 for s in status if s.lower().startswith('c'))  # Ex: "Confirmada"
    total_canceladas = sum(1 for s in status if "cancel" in s.lower())
    receita_total = float(sum(v for v, s in zip(
        valores, status) if s.lower().startswith('c')))
    receita_cancelada = float(sum(v for v, s in zip(
        valores, status) if "cancel" in s.lower()))

    # Distribuição por origem
    from collections import Counter
    origem_count = Counter(origens)
    origem_labels = list(origem_count.keys())
    origem_data = [origem_count[o] for o in origem_labels]

    # Montar tabela de reservas
    tabela_reservas = []
    total_linhas = max(len(datas), len(clientes), len(
        status), len(valores), len(origens))
    for i in range(total_linhas):
        tabela_reservas.append({
            "data": datas[i] if i < len(datas) else "",
            "cliente": clientes[i] if i < len(clientes) else "",
            "status": status[i] if i < len(status) else "",
            "valor": valores[i] if i < len(valores) else 0,
            "origem": origens[i] if i < len(origens) else ""
        })

    return {
        "total_reservas": total_reservas,
        "total_confirmadas": total_confirmadas,
        "total_canceladas": total_canceladas,
        "receita_total": receita_total,
        "receita_cancelada": receita_cancelada,
        "origens": origem_labels,
        "distribuicao_origem": origem_data,
        "tabela_reservas": tabela_reservas,
        "campos_detectados": {k: v for k, v in campos.items() if v}
    }
