"""
Views para o app core - páginas principais do sistema.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q

from academico.models import (
    Semestre, Materia, EventoAgenda, 
    Tarefa, AcessoMateria
)
from agentes.servicos import servico_agente


def home(request):
    """Página inicial do sistema."""
    
    # Agenda geral - próximos 7 dias
    data_limite = timezone.now() + timedelta(days=7)
    eventos_proximos = EventoAgenda.objects.filter(
        data_inicio__gte=timezone.now(),
        data_inicio__lte=data_limite
    ).order_by('data_inicio')[:10]
    
    # Semestres ativos
    semestres = Semestre.objects.filter(ativo=True).order_by('-ano', '-periodo')[:4]
    
    # Matérias mais acessadas (top 6)
    materias_populares = Materia.objects.filter(
        ativo=True
    ).order_by('-contador_acessos')[:6]
    
    # Estatísticas para os cards
    total_semestres = Semestre.objects.filter(ativo=True).count()
    total_materias = Materia.objects.filter(ativo=True).count()
    total_eventos = EventoAgenda.objects.filter(
        data_inicio__gte=timezone.now()
    ).count()
    
    context = {
        'eventos_proximos': eventos_proximos,
        'semestres': semestres,
        'materias_populares': materias_populares,
        'total_semestres': total_semestres,
        'total_materias': total_materias,
        'total_eventos': total_eventos,
        'titulo_pagina': 'Assistente de Estudos'
    }
    
    return render(request, 'core/home.html', context)


def chat_home(request):
    """Placeholder para o chat da home (em breve)."""
    
    if request.method == 'POST':
        pergunta = request.POST.get('pergunta', '').strip()
        
        if pergunta:
            # Por enquanto, apenas uma resposta informativa
            resposta = servico_agente.responder_home(pergunta)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'resposta': resposta,
                    'sucesso': True
                })
            else:
                messages.info(request, f"Resposta: {resposta}")
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'erro': 'Por favor, digite uma pergunta.',
                    'sucesso': False
                })
            else:
                messages.error(request, 'Por favor, digite uma pergunta.')
    
    return redirect('home')


def semestres_lista(request):
    """Lista todos os semestres, destacando o semestre atual."""
    from django.utils import timezone
    from datetime import date
    
    # Data atual para determinar o semestre corrente
    hoje = date.today()
    
    # Buscar semestre atual (que está em andamento)
    semestre_atual = Semestre.objects.filter(
        ativo=True,
        data_inicio__lte=hoje,
        data_fim__gte=hoje
    ).first()
    
    # Todos os semestres ordenados (mais recente primeiro)
    semestres = Semestre.objects.filter(ativo=True).order_by('-ano', '-periodo')
    
    # Outros semestres (excluindo o atual)
    outros_semestres = semestres.exclude(pk=semestre_atual.pk if semestre_atual else None)
    
    context = {
        'semestre_atual': semestre_atual,
        'outros_semestres': outros_semestres,
        'semestres': semestres,  # Mantém compatibilidade
        'titulo_pagina': 'Semestres'
    }
    
    return render(request, 'core/semestres_lista.html', context)


def semestre_detail(request, pk):
    """Detalhes de um semestre específico."""
    
    semestre = get_object_or_404(Semestre, pk=pk, ativo=True)
    
    # Matérias do semestre
    materias = semestre.materias.filter(ativo=True).order_by('nome')
    
    # Eventos do semestre (próximos 30 dias)
    data_limite = timezone.now() + timedelta(days=30)
    eventos = EventoAgenda.objects.filter(
        Q(escopo='SEMESTRE', semestre=semestre) |
        Q(escopo='MATERIA', materia__semestre=semestre),
        data_inicio__gte=timezone.now(),
        data_inicio__lte=data_limite
    ).order_by('data_inicio')[:10]
    
    context = {
        'semestre': semestre,
        'materias': materias,
        'eventos': eventos,
        'titulo_pagina': f'Semestre: {semestre.nome}'
    }
    
    return render(request, 'core/semestre_detail.html', context)


@require_POST
def semestre_agente(request, pk):
    """Endpoint para o agente do semestre."""
    
    semestre = get_object_or_404(Semestre, pk=pk, ativo=True)
    pergunta = request.POST.get('pergunta', '').strip()
    
    if not pergunta:
        messages.error(request, 'Por favor, digite uma pergunta.')
        return redirect('semestre_detail', pk=pk)
    
    try:
        resposta = servico_agente.responder_semestre(pergunta, semestre.id)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'resposta': resposta,
                'sucesso': True
            })
        else:
            messages.success(request, f"Agente do Semestre: {resposta}")
            
    except Exception as e:
        erro_msg = "Erro ao processar sua pergunta. Tente novamente."
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'erro': erro_msg,
                'sucesso': False
            })
        else:
            messages.error(request, erro_msg)
    
    return redirect('semestre_detail', pk=pk)


def buscar(request):
    """Busca global no sistema - pode ser acessada diretamente."""
    
    query = request.GET.get('q', '').strip()
    
    if not query:
        messages.info(request, 'Digite algo para buscar.')
        return redirect('home')
    
    if len(query) < 2:
        messages.warning(request, 'Digite pelo menos 2 caracteres para buscar.')
        return redirect('home')
    
    # Buscar em matérias
    materias = Materia.objects.filter(
        Q(nome__icontains=query) | Q(descricao__icontains=query),
        ativo=True
    ).select_related('semestre')[:10]
    
    # Buscar em eventos
    eventos = EventoAgenda.objects.filter(
        Q(titulo__icontains=query) | Q(descricao__icontains=query),
        data_inicio__gte=timezone.now()
    ).select_related('semestre', 'materia')[:10]
    
    # Buscar em tarefas
    tarefas = Tarefa.objects.filter(
        Q(titulo__icontains=query) | Q(descricao__icontains=query)
    ).select_related('materia', 'materia__semestre')[:10]
    
    context = {
        'query': query,
        'materias': materias,
        'eventos': eventos,
        'tarefas': tarefas,
        'titulo_pagina': f'Busca: {query}'
    }
    
    return render(request, 'core/buscar.html', context)


def evento_form(request):
    """Formulário para criar/editar eventos (placeholder)."""
    
    if request.method == 'POST':
        messages.info(request, 'Funcionalidade de eventos em desenvolvimento.')
        return redirect('home')
    
    # Por enquanto, redireciona para a home
    messages.info(request, 'Formulário de eventos em desenvolvimento.')
    return redirect('home')
