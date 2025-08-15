// JavaScript para o Assistente de Estudos

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips do Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Inicializar popovers do Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-focus no primeiro input de forms modais
    var modals = document.querySelectorAll('.modal');
    modals.forEach(function(modal) {
        modal.addEventListener('shown.bs.modal', function () {
            var firstInput = modal.querySelector('input, textarea, select');
            if (firstInput) {
                firstInput.focus();
            }
        });
    });

    // Confirmação para ações destrutivas
    var deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            var message = this.getAttribute('data-confirm') || 'Tem certeza que deseja continuar?';
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });

    // Animação de fade-in para elementos
    var observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    var observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observar cards para animação
    var cards = document.querySelectorAll('.card');
    cards.forEach(function(card) {
        observer.observe(card);
    });
});

// Função utilitária para requisições AJAX
function makeAjaxRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    };

    const finalOptions = { ...defaultOptions, ...options };

    // Adicionar CSRF token para requisições POST/PUT/DELETE
    if (['POST', 'PUT', 'DELETE'].includes(finalOptions.method)) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            finalOptions.headers['X-CSRFToken'] = csrfToken.value;
        }
    }

    return fetch(url, finalOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('Erro na requisição:', error);
            throw error;
        });
}

// Função para mostrar notificações toast
function showToast(message, type = 'info') {
    const toastContainer = getOrCreateToastContainer();
    
    const toastId = 'toast-' + Date.now();
    const bgClass = {
        'success': 'bg-success',
        'error': 'bg-danger',
        'warning': 'bg-warning',
        'info': 'bg-info'
    }[type] || 'bg-info';
    
    const iconClass = {
        'success': 'bi-check-circle-fill',
        'error': 'bi-exclamation-triangle-fill',
        'warning': 'bi-exclamation-circle-fill',
        'info': 'bi-info-circle-fill'
    }[type] || 'bi-info-circle-fill';
    
    const toastHtml = `
        <div class="toast" id="${toastId}" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header ${bgClass} text-white">
                <i class="bi ${iconClass} me-2"></i>
                <strong class="me-auto">Assistente de Estudos</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 5000
    });
    
    // Remover o elemento após ser escondido
    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
    
    toast.show();
}

function getOrCreateToastContainer() {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1055';
        document.body.appendChild(container);
    }
    return container;
}

// Função para formatar datas
function formatDate(dateString, includeTime = false) {
    const date = new Date(dateString);
    const options = {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        timeZone: 'America/Sao_Paulo'
    };
    
    if (includeTime) {
        options.hour = '2-digit';
        options.minute = '2-digit';
    }
    
    return date.toLocaleDateString('pt-BR', options);
}

// Função para calcular tempo relativo
function timeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    const intervals = {
        ano: 31536000,
        mês: 2592000,
        semana: 604800,
        dia: 86400,
        hora: 3600,
        minuto: 60
    };
    
    for (let [unit, seconds] of Object.entries(intervals)) {
        const interval = Math.floor(diffInSeconds / seconds);
        if (interval >= 1) {
            return `há ${interval} ${unit}${interval > 1 && unit !== 'mês' ? 's' : ''}`;
        }
    }
    
    return 'agora mesmo';
}

// Função para validar arquivos antes do upload
function validateFile(file, maxSizeMB = 50, allowedTypes = ['.pdf', '.txt', '.doc', '.docx', '.md']) {
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    const fileName = file.name.toLowerCase();
    
    // Verificar tamanho
    if (file.size > maxSizeBytes) {
        return `Arquivo muito grande. Tamanho máximo: ${maxSizeMB}MB`;
    }
    
    // Verificar tipo
    const hasValidExtension = allowedTypes.some(type => fileName.endsWith(type));
    if (!hasValidExtension) {
        return `Tipo de arquivo não permitido. Use: ${allowedTypes.join(', ')}`;
    }
    
    return null; // Arquivo válido
}

// Função para preview de arquivos
function setupFilePreview(inputElement, previewElement) {
    inputElement.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (!file) {
            previewElement.innerHTML = '';
            return;
        }
        
        const validationError = validateFile(file);
        if (validationError) {
            showToast(validationError, 'error');
            e.target.value = '';
            previewElement.innerHTML = '';
            return;
        }
        
        const fileSize = (file.size / 1024 / 1024).toFixed(2);
        const fileExtension = file.name.split('.').pop().toUpperCase();
        
        previewElement.innerHTML = `
            <div class="alert alert-info">
                <i class="bi bi-file-earmark-text me-2"></i>
                <strong>${file.name}</strong><br>
                <small>Tamanho: ${fileSize} MB | Tipo: ${fileExtension}</small>
            </div>
        `;
    });
}

// Debounce para busca
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Função para busca em tempo real
function setupLiveSearch(inputElement, searchCallback, delay = 300) {
    const debouncedSearch = debounce(searchCallback, delay);
    
    inputElement.addEventListener('input', function(e) {
        const query = e.target.value.trim();
        if (query.length >= 2 || query.length === 0) {
            debouncedSearch(query);
        }
    });
}

// Utilitário para copiar texto
function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Texto copiado!', 'success');
        });
    } else {
        // Fallback para navegadores mais antigos
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            showToast('Texto copiado!', 'success');
        } catch (err) {
            showToast('Erro ao copiar texto', 'error');
        }
        document.body.removeChild(textArea);
    }
}

// Exportar funções para uso global
window.AssistenteEstudos = {
    makeAjaxRequest,
    showToast,
    formatDate,
    timeAgo,
    validateFile,
    setupFilePreview,
    setupLiveSearch,
    copyToClipboard,
    debounce
};
