document.addEventListener('DOMContentLoaded', function () {
    // --- Sidebar Mobile (hamburger)
    const sidebarToggle = document.getElementById('sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function () {
            document.querySelector('.sidebar').classList.toggle('sidebar-open');
        });
    }
    const sidebarClose = document.getElementById('sidebar-close');
    if (sidebarClose) {
        sidebarClose.addEventListener('click', function () {
            document.querySelector('.sidebar').classList.remove('sidebar-open');
        });
    }

    // --- Referências dos painéis
    const painelDashboard = document.getElementById('pagina-dashboard');
    const painelArquivos = document.getElementById('pagina-arquivos');
    const painelRelatorios = document.getElementById('pagina-relatorios');
    const painelAgenteDeIA = document.getElementById('pagina-agente');
    const painelConfiguracoes = document.getElementById('pagina-configuracoes');
    const painelAjuda = document.getElementById('pagina-ajuda');
    const painelNotificacoes = document.getElementById('pagina-notificacoes');

    // --- Função para mostrar painéis e esconder os outros
    function mostrarPainel(painel) {
    // Lista de todos os painéis
    if (painelDashboard) painelDashboard.style.display = painel === 'dashboard' ? 'block' : 'none';
    if (painelArquivos) painelArquivos.style.display = painel === 'arquivos' ? 'block' : 'none';
    if (painelRelatorios) painelRelatorios.style.display = painel === 'relatorios' ? 'block' : 'none';
    if (painelAgenteDeIA) painelAgenteDeIA.style.display = painel === 'agente de ia' ? 'block' : 'none';
    if (painelConfiguracoes) painelConfiguracoes.style.display = painel === 'configuracoes' ? 'block' : 'none';
    if (painelAjuda) painelAjuda.style.display = painel === 'ajuda' ? 'block' : 'none';
    if (painelNotificacoes) painelNotificacoes.style.display = painel === 'notificacoes' ? 'block' : 'none';

    // Esconde comparativo (tabela e gráficos) ao sair da aba de relatórios
    const comparativoPreview = document.getElementById('comparativo-preview');
    const graficosDiv = document.getElementById('comparativo-graficos');

    if (painel !== 'relatorios') {
        if (comparativoPreview) comparativoPreview.style.display = 'none';
        if (graficosDiv) graficosDiv.innerHTML = ''; // Limpa gráficos
        const tabelaComparativo = document.getElementById('tabela-comparativo');
        if (tabelaComparativo) tabelaComparativo.innerHTML = ''; // Limpa tabela
    }
    // Opcional: ao entrar na aba de relatórios, pode ocultar por padrão até o usuário clicar comparar
    if (painel === 'relatorios' && comparativoPreview) {
        comparativoPreview.style.display = 'none';
    }


     if (painel !== 'agente de ia') {
        const chatHistory = document.getElementById('chat-history');
        if (chatHistory) {
            while (chatHistory.firstChild) {
                chatHistory.removeChild(chatHistory.firstChild);
            }
            // Mensagem inicial (opcional)
            const msgDiv = document.createElement('div');
            msgDiv.className = 'flex flex-col gap-1';
            const bubble = document.createElement('div');
            bubble.className = 'message-bubble ai-message';
            bubble.textContent = 'Olá! Sou o assistente de IA do Hórus. Posso te ajudar com análises de dados, criação de relatórios e responder perguntas sobre suas métricas. Como posso te ajudar hoje?';
            msgDiv.appendChild(bubble);
            chatHistory.appendChild(msgDiv);
        }
    }
}


    // --- Sidebar: troca active e painel ao clicar
    document.getElementById('btn-dashboard').addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelectorAll('.sidebar-item').forEach(i => i.classList.remove('active'));
        this.classList.add('active');
        mostrarPainel('dashboard');
    });

    document.getElementById('btn-arquivos').addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelectorAll('.sidebar-item').forEach(i => i.classList.remove('active'));
        this.classList.add('active');
        mostrarPainel('arquivos');
        carregarArquivos();
    });

    document.getElementById('btn-relatorios').addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelectorAll('.sidebar-item').forEach(i => i.classList.remove('active'));
        this.classList.add('active');
        mostrarPainel('relatorios');
         carregarRelatoriosDisponiveis();
    });

    document.getElementById('btn-agente').addEventListener('click', function (e) {
    e.preventDefault();
    document.querySelectorAll('.sidebar-item').forEach(i => i.classList.remove('active'));
    this.classList.add('active');
    mostrarPainel('agente de ia');
});


    // --- Carregar arquivos enviados (para aba Arquivos)
    // arquivos.js

document.addEventListener('DOMContentLoaded', function() {
    carregarArquivos();

    // Search
    document.querySelector('.search-input').addEventListener('input', function() {
        const query = this.value.toLowerCase();
        document.querySelectorAll('.file-row').forEach(row => {
            const fileName = row.querySelector('.file-name').textContent.toLowerCase();
            row.style.display = fileName.includes(query) ? '' : 'none';
        });
    });

    // Upload
    document.querySelector('.upload-btn').addEventListener('click', function() {
        // Aqui chama o seu modal/input de upload
        alert("Funcionalidade de upload aqui");
    });
});

function carregarArquivos() {
    fetch('/uploads')
    .then(resp => resp.json())
    .then(data => {
        const tbody = document.getElementById('tabela-arquivos');
        if (!tbody) return;
        tbody.innerHTML = '';
        (data.files || []).forEach(file => {
            const tr = document.createElement('tr');
            tr.className = 'file-row';
            tr.innerHTML = `
                <td class="px-4 py-3">
                    <div class="flex items-center">
                        <i class="fas fa-file-excel text-green-600 mr-3"></i>
                        <span class="file-name">${file.name}</span>
                    </div>
                </td>
                <td class="px-4 py-3 text-sm text-gray-500">${file.uploaded_at || '-'}</td>
                <td class="px-4 py-3">
                    <div class="flex space-x-2">
                        <button class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm" onclick="baixarArquivo('${file.name}')">
                            <i class="fas fa-download mr-1"></i>Baixar
                        </button>
                        <button class="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm" onclick="carregarArquivoNoDashboard('${file.name}')">
                            <i class="fas fa-chart-line mr-1"></i>Dashboard
                        </button>
                        <button class="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm" onclick="excluirArquivo('${file.name}', this)">
                            <i class="fas fa-trash mr-1"></i>Excluir
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
    })
    .catch(err => console.error('Erro ao carregar arquivos:', err));
}

function baixarArquivo(nome) {
    window.location.href = `/download/${nome}`; // Ajuste a rota para seu backend!
}

function usarNoDashboard(nome) {
    alert("Funcionalidade de dashboard aqui para: " + nome);
}

    // --- Funções globais para botões Baixar, Dashboard e Excluir
    window.baixarArquivo = function(nomeArquivo) {
        window.open(`/api/download-arquivo/${encodeURIComponent(nomeArquivo)}`);
    };
    
    window.carregarArquivoNoDashboard = function(nomeArquivo) {
        fetch(`/api/usefile/${encodeURIComponent(nomeArquivo)}`)
            .then(res => res.json())
            .then(data => {
                atualizarCards(data);
                atualizarGraficos(data);
                atualizarTabela(data);
                mostrarPainel('dashboard');
                // Troca destaque do menu para o Dashboard
                document.querySelectorAll('.sidebar-item').forEach(i => i.classList.remove('active'));
                document.getElementById('btn-dashboard').classList.add('active');
            });
    };
    
    window.excluirArquivo = function(nome, btn) {
        if(confirm(`Deseja excluir o arquivo "${nome}"?`)) {
            fetch(`/uploads/${encodeURIComponent(nome)}`, { method: 'DELETE' })
            .then(resp => resp.json())
            .then(data => {
                if(data.success){
                    btn.closest('tr').remove();
                    alert(`Arquivo "${nome}" excluído com sucesso!`);
                } else {
                    alert("Erro ao excluir: " + (data.error || 'Erro desconhecido'));
                }
            })
            .catch(err => {
                console.error('Erro ao excluir arquivo:', err);
                alert('Erro ao excluir arquivo. Tente novamente.');
            });
        }
    };

    // --- GRÁFICOS (Chart.js)
    let revenueChart, distributionChart;
    function criarGraficos() {
        const revenueCtx = document.getElementById('revenueChart').getContext('2d');
        revenueChart = new Chart(revenueCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Receita',
                        data: [],
                        borderColor: '#4f46e5',
                        backgroundColor: 'rgba(79, 70, 229, 0.1)',
                        tension: 0.3,
                        fill: true
                    },
                    {
                        label: 'Meta',
                        data: [],
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderDash: [5, 5],
                        tension: 0.3,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top' },
                    tooltip: { mode: 'index', intersect: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function (value) {
                                return 'R$ ' + value.toLocaleString('pt-BR');
                            }
                        }
                    }
                }
            }
        });

        const distributionCtx = document.getElementById('distributionChart').getContext('2d');
        distributionChart = new Chart(distributionCtx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        '#4f46e5', '#10b981', '#f59e0b', '#ec4899', '#6366f1'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'right' },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return context.label + ': ' + context.raw + '%';
                            }
                        }
                    }
                },
                cutout: '70%'
            }
        });
    }

    // --- Atualiza os cards de KPIs
    function atualizarCards(data) {
        document.getElementById('valor-receita').textContent = 'R$ ' + (data.receita_total || 0).toLocaleString('pt-BR');
        document.getElementById('valor-despesa').textContent = 'R$ ' + (data.despesa_total || 0).toLocaleString('pt-BR');
        document.getElementById('valor-saldo').textContent = 'R$ ' + (data.saldo || 0).toLocaleString('pt-BR');
        document.getElementById('valor-lucro').textContent = 'R$ ' + (data.lucro_total || 0).toLocaleString('pt-BR');
    }

    // --- Atualiza os gráficos com os arrays do backend
    function atualizarGraficos(data) {
        revenueChart.data.labels = data.meses || [];
        revenueChart.data.datasets[0].data = data.receita_por_mes || [];
        revenueChart.data.datasets[1].data = data.meta_vendas || [];
        revenueChart.update();

        distributionChart.data.labels = data.meses ? data.meses.slice(0, data.distribuicao_vendas.length) : [];
        distributionChart.data.datasets[0].data = data.distribuicao_vendas || [];
        distributionChart.update();
    }

    // --- Atualiza tabela de dados do dashboard
    function atualizarTabela(data) {
        const tbody = document.getElementById('tabela-dados');
        tbody.innerHTML = '';
        (data.dados_tabela || []).forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${row.mes || ''}</td>
                <td>R$ ${(row.vendas || 0).toLocaleString('pt-BR')}</td>
                <td>R$ ${(row.meta_vendas || 0).toLocaleString('pt-BR')}</td>
                <td>R$ ${(row.despesas || 0).toLocaleString('pt-BR')}</td>
                <td>R$ ${(row.lucro_mensal || 0).toLocaleString('pt-BR')}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    // --- Carrega dashboard salvo ao abrir a página
    function carregarDashboard() {
        fetch('/api/dashboard')
            .then(res => res.json())
            .then(data => {
                atualizarCards(data);
                atualizarGraficos(data);
                atualizarTabela(data);
            });
    }

    // --- Upload dinâmico (envio e processamento)
    const mainUpload = document.getElementById('main-upload');
    if (mainUpload) {
        mainUpload.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (!file) return;
            const formData = new FormData();
            formData.append('file', file);
            fetch('/upload/financial', {
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                atualizarCards(data);
                atualizarGraficos(data);
                atualizarTabela(data);
                alert(`Arquivo "${file.name}" processado! Dashboard atualizado.`);
                carregarArquivos(); // Atualiza lista de arquivos após upload
            })
            .catch(err => alert("Erro ao processar arquivo!"));
        });
    }

    // --- Botão para buscar dados da API
    const btnFetchApi = document.getElementById('btn-fetch-api');
    if (btnFetchApi) {
        btnFetchApi.addEventListener('click', function() {
            const periodStart = document.getElementById('period-start').value;
            const periodEnd = document.getElementById('period-end').value;
            
            if (!periodStart || !periodEnd) {
                alert('Por favor, selecione as datas de início e fim.');
                return;
            }
            
            btnFetchApi.disabled = true;
            btnFetchApi.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Buscando...';
            
            fetch('/api/fetch-reservas', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    period_one: periodStart,
                    period_two: periodEnd,
                    per_page: 200
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert(`Sucesso! ${data.total_reservas} reservas processadas.\n\nArquivo salvo: ${data.filename}\n\nOs dados estão disponíveis na aba Arquivos e para o agente de IA.`);
                    // Recarrega a lista de arquivos se estivermos na aba arquivos
                    if (document.getElementById('pagina-arquivos').style.display !== 'none') {
                        carregarArquivos();
                    }
                } else {
                    alert('Erro: ' + (data.error || 'Erro desconhecido'));
                }
            })
            .catch(err => {
                console.error('Erro:', err);
                alert('Erro ao buscar dados da API.');
            })
            .finally(() => {
                btnFetchApi.disabled = false;
                btnFetchApi.innerHTML = '<i class="fas fa-download mr-2"></i>Buscar Reservas';
            });
        });
    }

    // --- Inicialização (primeiro load)
    criarGraficos();
    carregarDashboard();
    mostrarPainel('dashboard');
    // Sidebar marca o dashboard como ativo ao carregar
    document.querySelectorAll('.sidebar-item').forEach(i => i.classList.remove('active'));
    document.getElementById('btn-dashboard').classList.add('active');

    // Mostra aba de relatórios
document.getElementById('btn-relatorios').addEventListener('click', function(e) {
    e.preventDefault();
    mostrarPainel('relatorios');
    carregarRelatoriosDisponiveis();
});

// Carrega arquivos existentes
function carregarRelatoriosDisponiveis() {
    fetch('/api/lista-arquivos')
        .then(res => res.json())
        .then(files => {
            const lista = document.getElementById('lista-relatorios');
            lista.innerHTML = '';
            files.forEach(file => {
                const div = document.createElement('div');
                div.innerHTML = `
                    <label>
                        <input type="checkbox" class="relatorio-checkbox" value="${file.nome}">
                        ${file.nome} <span class="text-xs text-gray-400">(${file.data_upload})</span>
                    </label>
                `;
                lista.appendChild(div);
            });
            // Limitar para no máximo 6 selecionados
            const checkboxes = document.querySelectorAll('.relatorio-checkbox');
            checkboxes.forEach(cb => {
                cb.addEventListener('change', function() {
                    const checked = document.querySelectorAll('.relatorio-checkbox:checked');
                    if (checked.length > 6) {
                        this.checked = false;
                        alert("Máximo de 6 relatórios!");
                    }
                });
            });
        });
}

// Envia seleção ao backend
document.getElementById('btn-comparar-relatorios').addEventListener('click', function() {
    const selecionados = Array.from(document.querySelectorAll('.relatorio-checkbox:checked')).map(cb => cb.value);
    console.log('Arquivos selecionados:', selecionados);
    
    if (selecionados.length < 2) {
        alert("Selecione pelo menos 2 arquivos.");
        return;
    }
    
    fetch('/api/comparar-relatorios', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({arquivos: selecionados})
    })
    .then(res => {
        console.log('Status da resposta:', res.status);
        return res.json();
    })
    .then(dados => {
        console.log('Dados recebidos:', dados);
        if (dados.error) {
            alert('Erro: ' + dados.error);
        } else {
            exibirComparativo(dados);
        }
    })
    .catch(err => {
        console.error('Erro na requisição:', err);
        alert('Erro ao comparar relatórios. Verifique o console.');
    });
});

// Função para mostrar o resultado
function exibirComparativo(obj) {
    console.log('Exibindo comparativo:', obj);
    const arquivos = obj.arquivos;
    const metricas = obj.colunas_metricas;
    const dados = obj.dados;

    // Gera explicação da comparação
    const explicacao = gerarExplicacaoComparativo(arquivos, metricas, dados);
    const explicacaoDiv = document.getElementById('explicacao-comparativo');
    if (explicacaoDiv) {
        explicacaoDiv.innerHTML = explicacao;
    }

    document.getElementById('comparativo-preview').style.display = 'block';
    document.getElementById('btn-exportar-excel').style.display = '';
    document.getElementById('btn-exportar-pdf').style.display = '';
    console.log('Comparativo exibido com sucesso');

    // Chama renderização dos gráficos
    renderizarGraficosComparativo(arquivos, metricas, dados);
}

// Função para gerar explicação da comparação
function gerarExplicacaoComparativo(arquivos, metricas, dados) {
    const numArquivos = arquivos.length;
    const numMeses = dados.length;
    const arquivosNomes = arquivos.map(arq => arq.split('.')[0]).join(', ');
    
    let explicacao = `
        <div class="space-y-4">
            <p class="text-base">
                <strong>Comparação entre ${numArquivos} arquivos:</strong> ${arquivosNomes}
            </p>
            <p class="text-sm">
                Esta análise compara <strong>${metricas.join(', ')}</strong> ao longo de <strong>${numMeses} períodos</strong>, 
                mostrando a evolução temporal e as diferenças entre os arquivos selecionados.
            </p>
            <div class="bg-blue-50 p-4 rounded-lg">
                <h4 class="font-semibold text-blue-800 mb-2">📈 O que você verá nos gráficos:</h4>
                <ul class="text-sm text-blue-700 space-y-1">
                    <li>• <strong>Gráficos de linha:</strong> Evolução de cada métrica por arquivo ao longo do tempo</li>
                    <li>• <strong>Gráficos de barras:</strong> Diferenças absolutas e percentuais entre os valores</li>
                    <li>• <strong>Cores diferentes:</strong> Cada arquivo tem sua cor única para facilitar a identificação</li>
                </ul>
            </div>
        </div>
    `;
    
    return explicacao;
}

// Função para montar gráficos
function renderizarGraficosComparativo(arquivos, metricas, dados) {
    const graficosDiv = document.getElementById('comparativo-graficos');
    graficosDiv.innerHTML = "";

    metricas.forEach(met => {
        // Dados para gráfico de linha (valores de cada arquivo)
        const labels = dados.map(row => row['Mês']);
        const datasets = arquivos.map(arq => ({
            label: `${met} (${arq.split('.')[0]})`,
            data: dados.map(row => Number(row[`${met}_${arq}`]) || 0),
            fill: false,
            borderWidth: 2,
            borderColor: randomColor(arq),
            backgroundColor: randomColor(arq, 0.2)
        }));

        // Gráfico de linhas por métrica
        const canvasId = `grafico_${met}`;
        graficosDiv.innerHTML += `
            <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
                <h4 class="text-lg font-semibold text-gray-800 mb-2">${met} - Evolução Temporal</h4>
                <p class="text-sm text-gray-600 mb-4">Compare como a ${met.toLowerCase()} evoluiu ao longo do tempo em cada arquivo selecionado.</p>
                <canvas id="${canvasId}" height="100"></canvas>
            </div>
        `;

        setTimeout(() => {
            new Chart(document.getElementById(canvasId).getContext('2d'), {
                type: 'line',
                data: { labels: labels, datasets: datasets },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'top' }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { callback: val => 'R$ ' + val.toLocaleString('pt-BR') }
                        }
                    }
                }
            });
        }, 100);

        // Gráfico de barras para diferença
        const diffCanvasId = `grafico_${met}_dif`;
        const diffs = dados.map(row => Number(row[`${met}_dif`]) || 0);
        const percs = dados.map(row => Number(row[`${met}_perc`]) || 0);

        graficosDiv.innerHTML += `
            <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
                <h4 class="text-lg font-semibold text-gray-800 mb-2">${met} - Análise de Diferenças</h4>
                <p class="text-sm text-gray-600 mb-4">Veja a diferença absoluta (em R$) e percentual entre o maior e menor valor de ${met.toLowerCase()} em cada período.</p>
                <canvas id="${diffCanvasId}" height="100"></canvas>
            </div>
        `;

        setTimeout(() => {
            new Chart(document.getElementById(diffCanvasId).getContext('2d'), {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Diferença (R$)',
                            data: diffs,
                            backgroundColor: 'rgba(255,99,132,0.5)',
                            borderColor: 'rgba(255,99,132,1)',
                            borderWidth: 1,
                            yAxisID: 'y'
                        },
                        {
                            label: 'Variação (%)',
                            data: percs,
                            type: 'line',
                            borderColor: 'rgba(54,162,235,1)',
                            backgroundColor: 'rgba(54,162,235,0.2)',
                            fill: false,
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'top' }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: { display: true, text: 'Diferença (R$)' }
                        },
                        y1: {
                            beginAtZero: true,
                            position: 'right',
                            title: { display: true, text: 'Variação (%)' },
                            grid: { drawOnChartArea: false }
                        }
                    }
                }
            });
        }, 200);
    });
}

// Função simples para gerar cor única por arquivo
function randomColor(str, alpha=1) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    const r = (hash >> 0) & 0xFF;
    const g = (hash >> 8) & 0xFF;
    const b = (hash >> 16) & 0xFF;
    return alpha === 1
        ? `rgb(${r},${g},${b})`
        : `rgba(${r},${g},${b},${alpha})`;
}


// Elementos do chat IA
const btnPerguntarIa = document.getElementById('btn-perguntar-ia');
const perguntaIa = document.getElementById('pergunta-ia');
const chatHistory = document.getElementById('chat-history');
const btnLimpar = document.getElementById('btn-limpar');

// Habilita/Desabilita o botão de enviar conforme texto digitado
if (perguntaIa && btnPerguntarIa) {
    perguntaIa.addEventListener('input', function () {
        btnPerguntarIa.disabled = this.value.trim() === '';
    });
}

// Sugerir perguntas rápidas (chips)
window.insertSuggestion = function(element) {
    if (perguntaIa && btnPerguntarIa) {
        perguntaIa.value = element.textContent.trim();
        perguntaIa.focus();
        btnPerguntarIa.disabled = false;
    }
};

// Adiciona mensagem ao chat (usuário/IA)
function addMessage(text, isUser) {
    if (!chatHistory) return;
    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex flex-col gap-1';
    const bubble = document.createElement('div');
    bubble.className = isUser ? 'message-bubble user-message' : 'message-bubble ai-message';
    bubble.textContent = text;
    messageDiv.appendChild(bubble);
    chatHistory.appendChild(messageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Indicador de "digitando"
function showTypingIndicator() {
    if (!chatHistory) return null;
    const typingDiv = document.createElement('div');
    typingDiv.className = 'flex flex-col gap-1';
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble ai-message flex items-center';
    const dots = document.createElement('div');
    dots.className = 'flex';
    dots.innerHTML = `
        <span class="typing-indicator"></span>
        <span class="typing-indicator"></span>
        <span class="typing-indicator"></span>
    `;
    bubble.appendChild(dots);
    typingDiv.appendChild(bubble);
    chatHistory.appendChild(typingDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    return typingDiv;
}

function removeTypingIndicator(indicator) {
    if (indicator && indicator.parentNode) {
        indicator.parentNode.removeChild(indicator);
    }
}

// Função para perguntar para o agente IA
async function perguntarAgenteIA(pergunta) {
    const resp = await fetch("https://perceptive-essence-production.up.railway.app/ask", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ pergunta: pergunta })
    });
    if (!resp.ok) {
        const data = await resp.json().catch(() => ({}));
        throw new Error(data.detail || "Erro ao conectar com o agente de IA.");
    }
    const data = await resp.json();
    return data.resposta;
}

// Envio pelo botão/enviar
if (btnPerguntarIa && perguntaIa && chatHistory) {
    btnPerguntarIa.addEventListener('click', async function () {
        const question = perguntaIa.value.trim();
        if (!question) return;
        addMessage(question, true); // balão do usuário
        perguntaIa.value = '';
        btnPerguntarIa.disabled = true;
        const typingIndicator = showTypingIndicator();
        try {
            const resposta = await perguntarAgenteIA(question);
            removeTypingIndicator(typingIndicator);
            addMessage(resposta, false); // balão do bot
        } catch (err) {
            removeTypingIndicator(typingIndicator);
            addMessage("Erro ao obter resposta da IA: " + (err.message || err), false);
        } finally {
            btnPerguntarIa.disabled = false;
        }
    });

    // Envia ao pressionar Enter (sem Shift)
    perguntaIa.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!btnPerguntarIa.disabled) {
                btnPerguntarIa.click();
            }
        }
    });
}

// Limpar histórico de chat IA (mensagem inicial)
function resetarChatIA() {
    if (chatHistory) {
        while (chatHistory.firstChild) {
            chatHistory.removeChild(chatHistory.firstChild);
        }
        // Mensagem inicial
        const msgDiv = document.createElement('div');
        msgDiv.className = 'flex flex-col gap-1';
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble ai-message';
        bubble.textContent = 'Olá! Sou o assistente de IA do Hórus. Posso te ajudar com análises de dados, criação de relatórios e responder perguntas sobre suas métricas. Como posso te ajudar hoje?';
        msgDiv.appendChild(bubble);
        chatHistory.appendChild(msgDiv);
    }
}

// Botão limpar histórico
if (btnLimpar && chatHistory) {
    btnLimpar.addEventListener('click', resetarChatIA);
}

// Resetar chat sempre que entrar na aba de IA:
document.getElementById('btn-agente').addEventListener('click', function (e) {
    e.preventDefault();
    document.querySelectorAll('.sidebar-item').forEach(i => i.classList.remove('active'));
    this.classList.add('active');
    mostrarPainel('agente de ia');
    resetarChatIA();
});




});
