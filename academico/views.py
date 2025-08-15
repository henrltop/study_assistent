"""
Views para o app acadêmico - páginas específicas de matérias, materiais, etc.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404, HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.files.storage import default_storage
from django.conf import settings
from datetime import timedelta
import os
import mimetypes

from .models import (
    Materia, MaterialDidatico, EventoAgenda, 
    Tarefa, AcessoMateria
)
from .forms import (
    MaterialDidaticoForm, EventoAgendaForm, TarefaForm
)
from agentes.servicos import servico_agente


def materia_detail(request, slug):
    """Detalhes de uma matéria específica."""
    
    materia = get_object_or_404(Materia, slug=slug, ativo=True)
    
    # Incrementar contador de acesso
    materia.incrementar_acesso()
    
    # Registrar acesso para estatísticas
    AcessoMateria.objects.create(
        materia=materia,
        usuario=request.user if request.user.is_authenticated else None,
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    # Materiais didáticos
    materiais = materia.materiais.all().order_by('-data_upload')
    
    # Próximos eventos da matéria
    eventos_proximos = EventoAgenda.objects.filter(
        materia=materia,
        data_inicio__gte=timezone.now()
    ).order_by('data_inicio')[:5]
    
    # Tarefas pendentes
    tarefas_pendentes = materia.tarefas.filter(
        status__in=['PENDENTE', 'EM_ANDAMENTO']
    ).order_by('prazo', '-criado_em')
    
    # Tarefas concluídas (últimas 5)
    tarefas_concluidas = materia.tarefas.filter(
        status='CONCLUIDA'
    ).order_by('-atualizado_em')[:5]
    
    context = {
        'materia': materia,
        'materiais': materiais,
        'eventos_proximos': eventos_proximos,
        'tarefas_pendentes': tarefas_pendentes,
        'tarefas_concluidas': tarefas_concluidas,
        'titulo_pagina': f'Matéria: {materia.nome}'
    }
    
    return render(request, 'academico/materia_detail.html', context)


@require_POST
def materia_tutor(request, slug):
    """Endpoint para o tutor (agente) da matéria."""
    
    materia = get_object_or_404(Materia, slug=slug, ativo=True)
    pergunta = request.POST.get('pergunta', '').strip()
    
    if not pergunta:
        messages.error(request, 'Por favor, digite uma pergunta.')
        return redirect('materia_detail', slug=slug)
    
    try:
        resposta = servico_agente.responder_materia(pergunta, materia.slug)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'resposta': resposta,
                'sucesso': True
            })
        else:
            messages.success(request, f"Tutor da Matéria: {resposta}")
            
    except Exception as e:
        erro_msg = "Erro ao processar sua pergunta. Tente novamente."
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'erro': erro_msg,
                'sucesso': False
            })
        else:
            messages.error(request, erro_msg)
    
    return redirect('materia_detail', slug=slug)


@login_required
def material_upload(request, slug):
    """Upload de material didático para a matéria."""
    
    materia = get_object_or_404(Materia, slug=slug, ativo=True)
    
    if request.method == 'POST':
        form = MaterialDidaticoForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.materia = materia
            material.usuario = request.user
            
            # Determinar tipo baseado na extensão
            if material.arquivo:
                ext = os.path.splitext(material.arquivo.name)[1].lower()
                if ext == '.pdf':
                    material.tipo = 'PDF'
                elif ext in ['.txt', '.md']:
                    material.tipo = 'TXT'
                elif ext in ['.doc', '.docx']:
                    material.tipo = 'DOCX'
            
            material.save()
            messages.success(request, f'Material "{material.titulo}" enviado com sucesso!')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'sucesso': True,
                    'mensagem': f'Material "{material.titulo}" enviado com sucesso!'
                })
            
            return redirect('materia_detail', slug=slug)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'sucesso': False,
                    'erros': form.errors
                })
    else:
        form = MaterialDidaticoForm()
    
    context = {
        'form': form,
        'materia': materia,
        'titulo_pagina': f'Enviar Material - {materia.nome}'
    }
    
    return render(request, 'academico/material_upload.html', context)


def material_download(request, pk):
    """Download de material didático."""
    
    material = get_object_or_404(MaterialDidatico, pk=pk)
    
    if not material.arquivo:
        raise Http404("Arquivo não encontrado")
    
    # Verificar se o arquivo existe
    if not default_storage.exists(material.arquivo.name):
        messages.error(request, 'Arquivo não encontrado no servidor.')
        return redirect('materia_detail', slug=material.materia.slug)
    
    # Preparar resposta com o arquivo
    file_path = material.arquivo.path
    mime_type, _ = mimetypes.guess_type(file_path)
    
    try:
        with open(file_path, 'rb') as arquivo:
            response = HttpResponse(arquivo.read(), content_type=mime_type or 'application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(material.arquivo.name)}"'
            return response
    except FileNotFoundError:
        messages.error(request, 'Arquivo não encontrado.')
        return redirect('materia_detail', slug=material.materia.slug)


@login_required
def evento_create(request, slug):
    """Criar evento para a matéria."""
    
    materia = get_object_or_404(Materia, slug=slug, ativo=True)
    
    if request.method == 'POST':
        form = EventoAgendaForm(request.POST)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.escopo = 'MATERIA'
            evento.materia = materia
            evento.usuario = request.user
            evento.save()
            
            messages.success(request, f'Evento "{evento.titulo}" criado com sucesso!')
            return redirect('materia_detail', slug=slug)
    else:
        form = EventoAgendaForm()
    
    context = {
        'form': form,
        'materia': materia,
        'titulo_pagina': f'Novo Evento - {materia.nome}'
    }
    
    return render(request, 'academico/evento_form.html', context)


@login_required
def evento_edit(request, pk):
    """Editar evento."""
    
    evento = get_object_or_404(EventoAgenda, pk=pk)
    
    # Verificar permissões
    if not request.user.is_staff and evento.usuario != request.user:
        messages.error(request, 'Você não tem permissão para editar este evento.')
        return redirect('materia_detail', slug=evento.materia.slug if evento.materia else 'home')
    
    if request.method == 'POST':
        form = EventoAgendaForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            messages.success(request, f'Evento "{evento.titulo}" atualizado com sucesso!')
            
            if evento.materia:
                return redirect('materia_detail', slug=evento.materia.slug)
            else:
                return redirect('agenda_geral')
    else:
        form = EventoAgendaForm(instance=evento)
    
    context = {
        'form': form,
        'evento': evento,
        'titulo_pagina': f'Editar Evento: {evento.titulo}'
    }
    
    return render(request, 'academico/evento_form.html', context)


@login_required
def tarefa_create(request, slug):
    """Criar tarefa para a matéria."""
    
    materia = get_object_or_404(Materia, slug=slug, ativo=True)
    
    if request.method == 'POST':
        form = TarefaForm(request.POST, materia=materia)
        if form.is_valid():
            tarefa = form.save(commit=False)
            tarefa.materia = materia
            tarefa.usuario = request.user
            tarefa.save()
            
            messages.success(request, f'Tarefa "{tarefa.titulo}" criada com sucesso!')
            return redirect('academico:materia_detail', slug=slug)
    else:
        form = TarefaForm(materia=materia)
    
    context = {
        'form': form,
        'materia': materia,
        'titulo_pagina': f'Nova Tarefa - {materia.nome}'
    }
    
    return render(request, 'academico/tarefa_form.html', context)


@login_required
def tarefa_edit(request, pk):
    """Editar tarefa."""
    
    tarefa = get_object_or_404(Tarefa, pk=pk)
    
    # Verificar permissões
    if not request.user.is_staff and tarefa.usuario != request.user:
        messages.error(request, 'Você não tem permissão para editar esta tarefa.')
        return redirect('academico:materia_detail', slug=tarefa.materia.slug)
    
    if request.method == 'POST':
        form = TarefaForm(request.POST, instance=tarefa, materia=tarefa.materia)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tarefa "{tarefa.titulo}" atualizada com sucesso!')
            return redirect('academico:materia_detail', slug=tarefa.materia.slug)
    else:
        form = TarefaForm(instance=tarefa, materia=tarefa.materia)
    
    context = {
        'form': form,
        'tarefa': tarefa,
        'titulo_pagina': f'Editar Tarefa: {tarefa.titulo}'
    }
    
    return render(request, 'academico/tarefa_form.html', context)


@login_required
@require_POST
def tarefa_toggle_status(request, pk):
    """Toggle do status da tarefa (pendente <-> concluída)."""
    
    tarefa = get_object_or_404(Tarefa, pk=pk)
    
    # Verificar permissões
    if not request.user.is_staff and tarefa.usuario != request.user:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'sucesso': False, 'erro': 'Sem permissão'})
        
        messages.error(request, 'Você não tem permissão para alterar esta tarefa.')
        return redirect('materia_detail', slug=tarefa.materia.slug)
    
    # Toggle do status
    if tarefa.status == 'CONCLUIDA':
        tarefa.status = 'PENDENTE'
        mensagem = f'Tarefa "{tarefa.titulo}" marcada como pendente.'
    else:
        tarefa.status = 'CONCLUIDA'
        mensagem = f'Tarefa "{tarefa.titulo}" marcada como concluída.'
    
    tarefa.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'sucesso': True,
            'novo_status': tarefa.get_status_display(),
            'status_code': tarefa.status,
            'mensagem': mensagem
        })
    
    messages.success(request, mensagem)
    return redirect('materia_detail', slug=tarefa.materia.slug)
