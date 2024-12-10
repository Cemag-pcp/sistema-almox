document.addEventListener('DOMContentLoaded', () => {
    // Configuração para a tabela de transferências
    const transferenciaConfig = {
        containerId: 'table-transferencia-container',
        tbodyId: 'table-body-transferencia',
        url: 'data-transferencia/', // Substitua pela URL correta
        start: 0,
        length: 10,
        isLoading: false,
        hasMoreItems: true,
        spinnerId: 'spinner-transferencia',
        type: 'transferencia',
        columns: [
            { key: 'chave', label: 'Chave' },
            { key: 'item', label: 'Item' },
            { key: 'qtd', label: 'Quantidade' },
            { key: 'data_solicitacao', label: 'Data Solicitação' },
            { key: 'data_entrega', label: 'Data Entrega' },
            { key: 'dep_destino', label: 'Destino' },
            { key: 'solicitante', label: 'Solicitante' },
            { key: 'erro', label: 'Erro' },
            { key: 'actions', label: 'Ações' },
        ],
    };

    // Configuração para a tabela de estoque
    const requisicaoConfig = {
        containerId: 'table-requisicao-container',
        tbodyId: 'table-body-requisicao',
        url: 'data-requisicao/', // Substitua pela URL correta
        start: 0,
        length: 10,
        isLoading: false,
        hasMoreItems: true,
        spinnerId: 'spinner-requisicao',
        type: 'requisicao',
        columns: [
            { key: 'chave', label: 'Chave' },
            { key: 'item', label: 'Item' },
            { key: 'qtd', label: 'Quantidade' },
            { key: 'data_solicitacao', label: 'Data Solicitação' },
            { key: 'data_entrega', label: 'Data Entrega' },
            { key: 'classe_req', label: 'Classe Requisição' },
            { key: 'solicitante', label: 'Solicitante'},
            { key: 'cc', label: 'CC'},
            { key: 'erro', label: 'Erro' },
            { key: 'actions', label: 'Ações' },

        ],
    };

    // Função para mostrar o spinner
    function showSpinner(spinnerId) {
        const spinner = document.getElementById(spinnerId);
        if (spinner) {
            spinner.style.display = 'block';
        }
    }

    // Função para esconder o spinner
    function hideSpinner(spinnerId) {
        const spinner = document.getElementById(spinnerId);
        if (spinner) {
            spinner.style.display = 'none';
        }
    }

    // Função para buscar itens para uma tabela específica
    function fetchItems(config) {
        if (config.isLoading || !config.hasMoreItems) return;
    
        config.isLoading = true;
        showSpinner(config.spinnerId); // Mostra o spinner durante o carregamento
    
        const params = new URLSearchParams({
            start: config.start,
            length: config.length,
            draw: 1,
        });
    
        fetch(`${config.url}?${params.toString()}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro na requisição');
                }
                return response.json();
            })
            .then(data => {
                const items = data.data;
    
                // Adiciona os itens na tabela correta
                const tableBody = document.getElementById(config.tbodyId);
                items.forEach(item => {
                    const row = document.createElement('tr');
                    row.innerHTML = config.columns
                        .map(col => {
                            if (col.key === 'actions') {
                                return `
                                    <td>
                                        <button 
                                            class="btn btn-primary btn-sm badge"> 
                                            Editar
                                        </button>
                                        <button 
                                            class="btn btn-danger btn-sm badge"> 
                                            Confirmar
                                        </button>
                                    </td>
                                `;
                            }
                            return `<td>${item[col.key] || 'N/A'}</td>`;
                        })
                        .join('');
                    tableBody.appendChild(row);
                });
    
                config.start += config.length;
                if (items.length < config.length) {
                    config.hasMoreItems = false;
                }
            })
            .catch(error => {
                console.error("Erro ao buscar dados:", error);
            })
            .finally(() => {
                config.isLoading = false;
                hideSpinner(config.spinnerId); // Esconde o spinner após o carregamento
            });
    }
    

    // Função para inicializar uma tabela específica
    function initializeTable(config) {
        const container = document.getElementById(config.containerId);

        // Carrega os primeiros itens
        fetchItems(config);

        // Evento de scroll no contêiner específico
        container.addEventListener('scroll', () => {
            if (container.scrollTop + container.clientHeight >= container.scrollHeight - 50) {
                fetchItems(config);
            }
        });
    }

    // Inicializa as tabelas
    initializeTable(transferenciaConfig);
    initializeTable(requisicaoConfig);
});

function editar(chave, type) {
    // Preenche os campos do modal de edição
    document.getElementById('editarChave').value = chave;
    document.getElementById('editarType').value = type;

    // Exibe ou oculta o campo "Classe" com base no tipo
    const classeContainer = document.getElementById('editarClasseContainer');
    if (type === 'transferencia') {
        classeContainer.style.display = 'none';
    } else if (type === 'requisicao') {
        classeContainer.style.display = 'block';
    }

    // Exibe o modal
    const modalEditar = new bootstrap.Modal(document.getElementById('modalEditar'));
    modalEditar.show();
}

function confirmar(chave, type) {
    // Preenche os campos do modal de confirmação
    document.getElementById('confirmarChave').textContent = chave;

    // Exibe o modal
    const modalConfirmar = new bootstrap.Modal(document.getElementById('modalConfirmar'));
    modalConfirmar.show();
}

