"""
Views adicionais para o app acadêmico - cadastros e funcionalidades extras.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Count
from datetime import timedelta

from .models import (
    Semestre, Materia, MaterialDidatico, EventoAgenda, 
    Tarefa, AcessoMateria, HorarioAula
)
from .forms import EventoAgendaForm, TarefaForm, MateriaComHorariosForm, HorarioAulaForm, HorarioAulaFormSet


@login_required
def materia_create(request):
    """Criar nova matéria com horários integrados."""
    
    if request.method == 'POST':
        form = MateriaComHorariosForm(request.POST)
        horarios_formset = HorarioAulaFormSet(request.POST)
        
        if form.is_valid() and horarios_formset.is_valid():
            materia = form.save()
            
            # Salvar horários associados
            horarios_formset.instance = materia
            horarios_formset.save()
            
            messages.success(request, f'Matéria "{materia.nome}" criada com sucesso!')
            return redirect('academico:materia_detail', slug=materia.slug)
    else:
        form = MateriaComHorariosForm()
        horarios_formset = HorarioAulaFormSet()
    
    context = {
        'form': form,
        'horarios_formset': horarios_formset,
        'titulo_pagina': 'Nova Matéria',
        'is_create': True
    }
    
    return render(request, 'academico/materia_form_completo.html', context)


@login_required  
def materia_edit(request, slug):
    """Editar matéria existente com horários integrados."""
    
    materia = get_object_or_404(Materia, slug=slug, ativo=True)
    
    if request.method == 'POST':
        form = MateriaComHorariosForm(request.POST, instance=materia)
        horarios_formset = HorarioAulaFormSet(request.POST, instance=materia)
        
        if form.is_valid() and horarios_formset.is_valid():
            materia = form.save()
            horarios_formset.save()
            messages.success(request, f'Matéria "{materia.nome}" atualizada com sucesso!')
            return redirect('academico:materia_detail', slug=materia.slug)
    else:
        form = MateriaComHorariosForm(instance=materia)
        horarios_formset = HorarioAulaFormSet(instance=materia)
    
    context = {
        'form': form,
        'horarios_formset': horarios_formset,
        'materia': materia,
        'titulo_pagina': f'Editar: {materia.nome}',
        'is_create': False
    }
    
    return render(request, 'academico/materia_form_completo.html', context)


def materias_lista(request):
    """Lista todas as matérias com filtros e busca."""
    
    # Base queryset
    materias = Materia.objects.filter(ativo=True).select_related('semestre')
    
    # Filtros
    busca = request.GET.get('busca', '').strip()
    semestre_id = request.GET.get('semestre', '')
    
    if busca:
        materias = materias.filter(
            Q(nome__icontains=busca) | 
            Q(descricao__icontains=busca) |
            Q(semestre__nome__icontains=busca)
        )
    
    if semestre_id:
        materias = materias.filter(semestre_id=semestre_id)
    
    # Ordenação
    ordem = request.GET.get('ordem', 'nome')
    if ordem == 'acessos':
        materias = materias.order_by('-contador_acessos', 'nome')
    elif ordem == 'recente':
        materias = materias.order_by('-criado_em')
    else:  # nome
        materias = materias.order_by('nome')
    
    # Paginação
    paginator = Paginator(materias, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Dados para filtros
    semestres = Semestre.objects.filter(ativo=True).order_by('-ano', '-periodo')
    
    context = {
        'page_obj': page_obj,
        'semestres': semestres,
        'busca': busca,
        'semestre_selecionado': semestre_id,
        'ordem': ordem,
        'titulo_pagina': 'Todas as Matérias'
    }
    
    return render(request, 'academico/materias_lista.html', context)


def agenda_geral(request):
    """Agenda geral com todos os eventos."""
    
    # Filtros
    periodo = request.GET.get('periodo', 'proximos')  # proximos, todos, passados
    tipo = request.GET.get('tipo', '')
    
    # Base queryset
    eventos = EventoAgenda.objects.select_related('semestre', 'materia')
    
    # Aplicar filtros de período
    hoje = timezone.now()
    if periodo == 'proximos':
        eventos = eventos.filter(data_inicio__gte=hoje)
    elif periodo == 'passados':
        eventos = eventos.filter(data_inicio__lt=hoje)
    # Se 'todos', não filtra por data
    
    # Filtro por tipo
    if tipo:
        eventos = eventos.filter(tipo=tipo)
    
    eventos = eventos.order_by('data_inicio')
    
    # Paginação
    paginator = Paginator(eventos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Próximos eventos importantes (para sidebar)
    proximos_importantes = EventoAgenda.objects.filter(
        data_inicio__gte=hoje,
        tipo__in=['PROVA', 'TRABALHO']
    ).order_by('data_inicio')[:5]
    
    # Tipos de evento para filtro
    tipos_evento = EventoAgenda.TIPO_CHOICES
    
    context = {
        'page_obj': page_obj,
        'periodo': periodo,
        'tipo_selecionado': tipo,
        'tipos_evento': tipos_evento,
        'proximos_importantes': proximos_importantes,
        'titulo_pagina': 'Agenda Geral'
    }
    
    return render(request, 'academico/agenda_geral.html', context)


@login_required
def evento_geral_create(request):
    """Criar evento geral (não vinculado a matéria)."""
    
    if request.method == 'POST':
        form = EventoAgendaForm(request.POST)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.escopo = 'GERAL'
            evento.usuario = request.user
            evento.save()
            
            messages.success(request, f'Evento "{evento.titulo}" criado com sucesso!')
            return redirect('academico:agenda_geral')
    else:
        form = EventoAgendaForm()
    
    context = {
        'form': form,
        'titulo_pagina': 'Novo Evento Geral'
    }
    
    return render(request, 'academico/evento_form.html', context)


def todolist_geral(request):
    """Lista geral de todas as tarefas (dashboard)."""
    
    # Filtros
    status = request.GET.get('status', 'pendente')
    semestre_id = request.GET.get('semestre', '')
    materia_id = request.GET.get('materia', '')
    
    # Base queryset
    tarefas = Tarefa.objects.select_related('materia', 'materia__semestre')
    
    # Filtros
    if status == 'pendente':
        tarefas = tarefas.filter(status__in=['PENDENTE', 'EM_ANDAMENTO'])
    elif status == 'concluida':
        tarefas = tarefas.filter(status='CONCLUIDA')
    
    if semestre_id:
        tarefas = tarefas.filter(materia__semestre_id=semestre_id)
    
    if materia_id:
        tarefas = tarefas.filter(materia_id=materia_id)
    
    tarefas = tarefas.order_by('prazo', '-criado_em')
    
    # Estatísticas
    stats = {
        'total': Tarefa.objects.count(),
        'pendentes': Tarefa.objects.filter(status__in=['PENDENTE', 'EM_ANDAMENTO']).count(),
        'concluidas': Tarefa.objects.filter(status='CONCLUIDA').count(),
        'atrasadas': Tarefa.objects.filter(
            status__in=['PENDENTE', 'EM_ANDAMENTO'],
            prazo__lt=timezone.now()
        ).count(),
    }
    
    # Paginação
    paginator = Paginator(tarefas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Dados para filtros
    semestres = Semestre.objects.filter(ativo=True).order_by('-ano', '-periodo')
    materias = Materia.objects.filter(ativo=True).order_by('nome')
    
    context = {
        'page_obj': page_obj,
        'stats': stats,
        'status_selecionado': status,
        'semestre_selecionado': semestre_id,
        'materia_selecionada': materia_id,
        'semestres': semestres,
        'materias': materias,
        'titulo_pagina': 'Lista de Tarefas - Geral'
    }
    
    return render(request, 'academico/todolist_geral.html', context)


def todolist_semestre(request, pk):
    """Lista de tarefas de um semestre específico."""
    
    semestre = get_object_or_404(Semestre, pk=pk, ativo=True)
    
    # Filtros
    status = request.GET.get('status', 'pendente')
    materia_id = request.GET.get('materia', '')
    
    # Base queryset - todas as tarefas das matérias deste semestre
    tarefas = Tarefa.objects.filter(
        materia__semestre=semestre
    ).select_related('materia')
    
    # Filtros
    if status == 'pendente':
        tarefas = tarefas.filter(status__in=['PENDENTE', 'EM_ANDAMENTO'])
    elif status == 'concluida':
        tarefas = tarefas.filter(status='CONCLUIDA')
    
    if materia_id:
        tarefas = tarefas.filter(materia_id=materia_id)
    
    tarefas = tarefas.order_by('prazo', '-criado_em')
    
    # Estatísticas do semestre
    stats = {
        'total': Tarefa.objects.filter(materia__semestre=semestre).count(),
        'pendentes': Tarefa.objects.filter(
            materia__semestre=semestre,
            status__in=['PENDENTE', 'EM_ANDAMENTO']
        ).count(),
        'concluidas': Tarefa.objects.filter(
            materia__semestre=semestre,
            status='CONCLUIDA'
        ).count(),
        'atrasadas': Tarefa.objects.filter(
            materia__semestre=semestre,
            status__in=['PENDENTE', 'EM_ANDAMENTO'],
            prazo__lt=timezone.now()
        ).count(),
    }
    
    # Paginação
    paginator = Paginator(tarefas, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Matérias do semestre para filtro
    materias = semestre.materias.filter(ativo=True).order_by('nome')
    
    context = {
        'semestre': semestre,
        'page_obj': page_obj,
        'stats': stats,
        'status_selecionado': status,
        'materia_selecionada': materia_id,
        'materias': materias,
        'titulo_pagina': f'Tarefas - {semestre.nome}'
    }
    
    return render(request, 'academico/todolist_semestre.html', context)


def materials_lista(request):
    """Lista todos os materiais didáticos."""
    
    # Filtros
    busca = request.GET.get('busca', '').strip()
    tipo = request.GET.get('tipo', '')
    materia_id = request.GET.get('materia', '')
    
    # Base queryset
    materiais = MaterialDidatico.objects.select_related('materia', 'materia__semestre')
    
    # Aplicar filtros
    if busca:
        materiais = materiais.filter(
            Q(titulo__icontains=busca) |
            Q(materia__nome__icontains=busca)
        )
    
    if tipo:
        materiais = materiais.filter(tipo=tipo)
    
    if materia_id:
        materiais = materiais.filter(materia_id=materia_id)
    
    materiais = materiais.order_by('-data_upload')
    
    # Paginação
    paginator = Paginator(materiais, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Dados para filtros
    tipos_material = MaterialDidatico.TIPO_CHOICES
    materias = Materia.objects.filter(ativo=True).order_by('nome')
    
    context = {
        'page_obj': page_obj,
        'busca': busca,
        'tipo_selecionado': tipo,
        'materia_selecionada': materia_id,
        'tipos_material': tipos_material,
        'materias': materias,
        'titulo_pagina': 'Materiais Didáticos'
    }
    
    return render(request, 'academico/materials_lista.html', context)

# ==================== VIEWS DE HORÁRIOS DE AULA ====================

@login_required
def horarios_materia(request, slug):
    """Lista os horários de aula de uma matéria específica."""
    materia = get_object_or_404(Materia, slug=slug, ativo=True)
    
    # Verificar se o usuário tem acesso à matéria
    if materia.semestre.usuario != request.user:
        messages.error(request, 'Você não tem permissão para acessar esta matéria.')
        return redirect('semestres_lista')
    
    horarios = HorarioAula.objects.filter(materia=materia, ativo=True).order_by('dia_semana', 'hora_inicio')
    
    context = {
        'materia': materia,
        'horarios': horarios,
        'titulo_pagina': f'Horários - {materia.nome}'
    }
    
    return render(request, 'academico/horarios_materia.html', context)

@login_required
def horario_create(request, slug):
    """Criar novo horário de aula."""
    materia = get_object_or_404(Materia, slug=slug, ativo=True)
    
    # Verificar se o usuário tem acesso à matéria
    if materia.semestre.usuario != request.user:
        messages.error(request, 'Você não tem permissão para acessar esta matéria.')
        return redirect('semestres_lista')
    
    if request.method == 'POST':
        form = HorarioAulaForm(request.POST)
        if form.is_valid():
            horario = form.save(commit=False)
            horario.materia = materia
            
            # Verificar se já existe horário conflitante
            conflito = HorarioAula.objects.filter(
                materia=materia,
                dia_semana=horario.dia_semana,
                ativo=True
            ).filter(
                Q(hora_inicio__lt=horario.hora_fim, hora_fim__gt=horario.hora_inicio)
            ).exists()
            
            if conflito:
                messages.error(request, 'Já existe um horário conflitante para este dia e horário.')
                return render(request, 'academico/horario_form.html', {
                    'form': form,
                    'materia': materia,
                    'titulo_pagina': 'Novo Horário'
                })
            
            horario.save()
            messages.success(request, f'Horário de {horario.get_dia_semana_display()} criado com sucesso!')
            return redirect('academico:horarios_materia', slug=materia.slug)
    else:
        form = HorarioAulaForm()
    
    context = {
        'form': form,
        'materia': materia,
        'titulo_pagina': 'Novo Horário'
    }
    
    return render(request, 'academico/horario_form.html', context)

@login_required
def horario_edit(request, pk):
    """Editar horário de aula existente."""
    horario = get_object_or_404(HorarioAula, pk=pk)
    
    # Verificar se o usuário tem acesso
    if horario.materia.semestre.usuario != request.user:
        messages.error(request, 'Você não tem permissão para editar este horário.')
        return redirect('semestres_lista')
    
    if request.method == 'POST':
        form = HorarioAulaForm(request.POST, instance=horario)
        if form.is_valid():
            horario_editado = form.save(commit=False)
            
            # Verificar conflitos (excluindo o próprio horário)
            conflito = HorarioAula.objects.filter(
                materia=horario.materia,
                dia_semana=horario_editado.dia_semana,
                ativo=True
            ).exclude(pk=horario.pk).filter(
                Q(hora_inicio__lt=horario_editado.hora_fim, hora_fim__gt=horario_editado.hora_inicio)
            ).exists()
            
            if conflito:
                messages.error(request, 'Já existe um horário conflitante para este dia e horário.')
                return render(request, 'academico/horario_form.html', {
                    'form': form,
                    'horario': horario,
                    'materia': horario.materia,
                    'titulo_pagina': 'Editar Horário'
                })
            
            horario_editado.save()
            messages.success(request, f'Horário de {horario_editado.get_dia_semana_display()} atualizado com sucesso!')
            return redirect('academico:horarios_materia', slug=horario.materia.slug)
    else:
        form = HorarioAulaForm(instance=horario)
    
    context = {
        'form': form,
        'horario': horario,
        'materia': horario.materia,
        'titulo_pagina': 'Editar Horário'
    }
    
    return render(request, 'academico/horario_form.html', context)

@login_required
def horario_delete(request, pk):
    """Excluir horário de aula."""
    horario = get_object_or_404(HorarioAula, pk=pk)
    
    # Verificar se o usuário tem acesso
    if horario.materia.semestre.usuario != request.user:
        messages.error(request, 'Você não tem permissão para excluir este horário.')
        return redirect('semestres_lista')
    
    if request.method == 'POST':
        materia_slug = horario.materia.slug
        dia_semana = horario.get_dia_semana_display()
        horario.delete()
        messages.success(request, f'Horário de {dia_semana} excluído com sucesso!')
        return redirect('academico:horarios_materia', slug=materia_slug)
    
    context = {
        'horario': horario,
        'materia': horario.materia,
        'titulo_pagina': 'Excluir Horário'
    }
    
    return render(request, 'academico/horario_delete.html', context)
