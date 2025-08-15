from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.db.models import Q
from django.http import JsonResponse
from datetime import datetime, timedelta, date
import calendar
import json
from .models import EventoCalendario, RecorrenciaEvento
from .forms import EventoCalendarioForm, RecorrenciaEventoForm, FiltroEventosForm
from academico.models import HorarioAula

def gerar_eventos_horarios(user, first_day, last_day):
    """Gera eventos virtuais baseados nos horários de aula das matérias"""
    eventos_horarios = []
    
    # Buscar todos os horários de aula ativos (as matérias são globais no sistema)
    horarios = HorarioAula.objects.filter(ativo=True).select_related('materia')
    
    # Para cada horário, gerar eventos para o período solicitado
    current_date = first_day
    while current_date <= last_day:
        # Mapear dia da semana (0=Segunda, 6=Domingo) para Python (0=Segunda, 6=Domingo)
        weekday = current_date.weekday()
        
        for horario in horarios:
            # Verificar se o horário corresponde ao dia da semana atual
            if horario.dia_semana == weekday:
                # Criar um objeto evento virtual
                evento_virtual = {
                    'id': f'horario_{horario.id}_{current_date}',
                    'titulo': f'{horario.materia.nome}',
                    'descricao': f'Aula regular - {horario.local}' if horario.local else 'Aula regular',
                    'data_inicio': timezone.make_aware(
                        datetime.combine(current_date, horario.hora_inicio)
                    ),
                    'data_fim': timezone.make_aware(
                        datetime.combine(current_date, horario.hora_fim)
                    ),
                    'tipo': 'AULA',
                    'cor': '#28a745',  # Verde para aulas regulares
                    'local': horario.local or '',
                    'observacoes': horario.observacoes or '',
                    'materia': horario.materia,
                    'is_horario_fixo': True,  # Flag para identificar como horário fixo
                }
                eventos_horarios.append(evento_virtual)
        
        current_date += timedelta(days=1)
    
    return eventos_horarios

@login_required
def calendario_home(request):
    """Página principal do calendário com visualização mensal e semanal"""
    today = timezone.now().date()
    current_view = request.GET.get('view', 'monthly')  # 'monthly' ou 'weekly'
    
    # Determinar o mês/ano a ser exibido
    try:
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
    except (ValueError, TypeError):
        year, month = today.year, today.month
    
    # Criar calendário
    cal = calendar.Calendar(firstweekday=6)  # Domingo como primeiro dia
    month_days = cal.monthdayscalendar(year, month)
    
    # Buscar eventos do mês atual
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    
    # Para visualização semanal, calcular semana atual
    week_dates = []
    eventos_semana_por_hora = {}
    horas_semana = list(range(7, 23))  # 7h às 22h
    
    if current_view == 'weekly':
        # Encontrar primeira semana do mês que contém dias válidos
        primeira_semana = month_days[0]
        for i, dia in enumerate(primeira_semana):
            if dia > 0:  # Primeiro dia válido encontrado
                # Calcular data da primeira semana
                inicio_semana = date(year, month, dia) - timedelta(days=i)
                for j in range(7):
                    week_dates.append(inicio_semana + timedelta(days=j))
                break
        
        # Se não encontrou, usar primeira semana com todos os dias do mês
        if not week_dates:
            for semana in month_days:
                if all(dia > 0 for dia in semana):
                    for i, dia in enumerate(semana):
                        week_dates.append(date(year, month, dia))
                    break
        
        # Inicializar estrutura de eventos por hora e dia da semana
        for hora in horas_semana:
            eventos_semana_por_hora[hora] = {}
            for dia_index in range(7):
                eventos_semana_por_hora[hora][dia_index] = []
    
    # Buscar eventos normais
    eventos = EventoCalendario.objects.filter(
        usuario=request.user,
        data_inicio__date__gte=first_day,
        data_inicio__date__lte=last_day
    ).order_by('data_inicio')
    
    # Gerar eventos dos horários de aula
    eventos_horarios = gerar_eventos_horarios(request.user, first_day, last_day)
    
    # Combinar eventos normais e horários
    todos_eventos = list(eventos) + eventos_horarios
    
    # Organizar eventos por dia (visualização mensal)
    eventos_por_dia = {}
    for evento in todos_eventos:
        if hasattr(evento, 'data_inicio'):
            # Evento normal do banco
            dia = evento.data_inicio.date().day
            data_evento = evento.data_inicio.date()
        else:
            # Evento virtual do horário
            dia = evento['data_inicio'].date().day
            data_evento = evento['data_inicio'].date()
            
        if dia not in eventos_por_dia:
            eventos_por_dia[dia] = []
        eventos_por_dia[dia].append(evento)
        
        # Para visualização semanal, organizar por hora e dia da semana
        if current_view == 'weekly' and data_evento in week_dates:
            dia_semana_index = week_dates.index(data_evento)
            
            if hasattr(evento, 'data_inicio'):
                hora_evento = evento.data_inicio.hour
            else:
                hora_evento = evento['data_inicio'].hour
            
            if hora_evento in horas_semana:
                eventos_semana_por_hora[hora_evento][dia_semana_index].append(evento)
    
    # Navegação de meses
    if month == 1:
        prev_month, prev_year = 12, year - 1
        prev_month_name = calendar.month_name[12]
    else:
        prev_month, prev_year = month - 1, year
        prev_month_name = calendar.month_name[prev_month]
    
    if month == 12:
        next_month, next_year = 1, year + 1
        next_month_name = calendar.month_name[1]
    else:
        next_month, next_year = month + 1, year
        next_month_name = calendar.month_name[next_month]
    
    # Estatísticas rápidas
    eventos_hoje = EventoCalendario.objects.filter(
        usuario=request.user,
        data_inicio__date=today
    ).count()
    
    proximos_eventos = EventoCalendario.objects.filter(
        usuario=request.user,
        data_inicio__gte=timezone.now()
    )[:3]
    
    context = {
        'month_days': month_days,
        'eventos_por_dia': eventos_por_dia,
        'current_month': month,
        'current_year': year,
        'month_name': calendar.month_name[month],
        'prev_month': prev_month,
        'prev_year': prev_year,
        'prev_month_name': prev_month_name,
        'next_month': next_month,
        'next_year': next_year,
        'next_month_name': next_month_name,
        'today': today,
        'eventos_hoje': eventos_hoje,
        'proximos_eventos': proximos_eventos,
        'weekdays': ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'],
        'current_view': current_view,
        'week_dates': week_dates,
        'eventos_semana_por_hora': eventos_semana_por_hora,
        'horas_semana': horas_semana,
    }
    
    return render(request, 'calendario/calendario_home.html', context)

@login_required
def evento_criar(request):
    """Criar um novo evento"""
    if request.method == 'POST':
        form = EventoCalendarioForm(request.POST, user=request.user)
        recorrencia_form = RecorrenciaEventoForm(request.POST)
        
        if form.is_valid():
            evento = form.save(commit=False)
            evento.usuario = request.user
            evento.save()
            
            # Processar recorrência se fornecida
            if request.POST.get('tem_recorrencia') == 'on' and recorrencia_form.is_valid():
                recorrencia = recorrencia_form.save(commit=False)
                recorrencia.evento = evento
                recorrencia.save()
                
                messages.success(request, f'Evento "{evento.titulo}" criado com recorrência!')
            else:
                messages.success(request, f'Evento "{evento.titulo}" criado com sucesso!')
            
            return redirect('calendario:calendario_home')
    else:
        # Pré-preencher data se fornecida na URL
        initial_data = {}
        if request.GET.get('date'):
            try:
                date_str = request.GET.get('date')
                initial_date = datetime.strptime(date_str, '%Y-%m-%d')
                # Definir hora padrão como 9:00 para início e 10:00 para fim
                data_inicio = initial_date.replace(hour=9, minute=0)
                data_fim = initial_date.replace(hour=10, minute=0)
                
                # Converter para timezone aware se necessário
                if timezone.is_naive(data_inicio):
                    data_inicio = timezone.make_aware(data_inicio)
                    data_fim = timezone.make_aware(data_fim)
                
                # Converter para o formato esperado pelo campo datetime-local
                initial_data['data_inicio'] = data_inicio.strftime('%Y-%m-%dT%H:%M')
                initial_data['data_fim'] = data_fim.strftime('%Y-%m-%dT%H:%M')
            except ValueError:
                pass
        
        form = EventoCalendarioForm(initial=initial_data, user=request.user)
        recorrencia_form = RecorrenciaEventoForm()
    
    context = {
        'form': form,
        'recorrencia_form': recorrencia_form,
        'titulo_pagina': 'Criar Evento'
    }
    
    return render(request, 'calendario/evento_form.html', context)

@login_required
def evento_editar(request, evento_id):
    """Editar um evento existente"""
    evento = get_object_or_404(EventoCalendario, id=evento_id, usuario=request.user)
    
    if request.method == 'POST':
        form = EventoCalendarioForm(request.POST, instance=evento, user=request.user)
        
        if form.is_valid():
            evento = form.save()
            messages.success(request, f'Evento "{evento.titulo}" atualizado com sucesso!')
            return redirect('calendario:evento_detalhe', evento_id=evento.id)
    else:
        form = EventoCalendarioForm(instance=evento, user=request.user)
    
    context = {
        'form': form,
        'evento': evento,
        'titulo_pagina': 'Editar Evento'
    }
    
    return render(request, 'calendario/evento_form.html', context)

@login_required
def evento_detalhe(request, evento_id):
    """Visualizar detalhes de um evento"""
    evento = get_object_or_404(EventoCalendario, id=evento_id, usuario=request.user)
    
    context = {
        'evento': evento,
    }
    
    return render(request, 'calendario/evento_detalhe.html', context)

@login_required
def evento_excluir(request, evento_id):
    """Excluir um evento"""
    evento = get_object_or_404(EventoCalendario, id=evento_id, usuario=request.user)
    
    if request.method == 'POST':
        titulo = evento.titulo
        evento.delete()
        messages.success(request, f'Evento "{titulo}" excluído com sucesso!')
        return redirect('calendario:calendario_home')
    
    context = {
        'evento': evento,
    }
    
    return render(request, 'calendario/evento_confirmar_exclusao.html', context)

@login_required
def eventos_lista(request):
    """Lista de eventos com filtros"""
    form = FiltroEventosForm(request.GET, user=request.user)
    
    # Filtros base
    eventos = EventoCalendario.objects.filter(usuario=request.user)
    
    if form.is_valid():
        # Filtro por período
        periodo = form.cleaned_data.get('periodo')
        data_inicio = form.cleaned_data.get('data_inicio')
        data_fim = form.cleaned_data.get('data_fim')
        
        if periodo == 'hoje':
            hoje = timezone.now().date()
            eventos = eventos.filter(data_inicio__date=hoje)
        elif periodo == 'semana':
            hoje = timezone.now().date()
            inicio_semana = hoje - timedelta(days=hoje.weekday())
            fim_semana = inicio_semana + timedelta(days=6)
            eventos = eventos.filter(
                data_inicio__date__gte=inicio_semana,
                data_inicio__date__lte=fim_semana
            )
        elif periodo == 'mes':
            hoje = timezone.now().date()
            primeiro_dia = hoje.replace(day=1)
            if hoje.month == 12:
                ultimo_dia = hoje.replace(year=hoje.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                ultimo_dia = hoje.replace(month=hoje.month + 1, day=1) - timedelta(days=1)
            eventos = eventos.filter(
                data_inicio__date__gte=primeiro_dia,
                data_inicio__date__lte=ultimo_dia
            )
        elif periodo == 'personalizado' and data_inicio and data_fim:
            eventos = eventos.filter(
                data_inicio__date__gte=data_inicio,
                data_inicio__date__lte=data_fim
            )
        
        # Filtro por tipo de evento
        tipos_evento = form.cleaned_data.get('tipo_evento')
        if tipos_evento:
            eventos = eventos.filter(tipo_evento__in=tipos_evento)
        
        # Filtro por matéria
        materia = form.cleaned_data.get('materia')
        if materia:
            eventos = eventos.filter(materia=materia)
    
    eventos = eventos.order_by('data_inicio')
    
    context = {
        'eventos': eventos,
        'form': form,
        'total_eventos': eventos.count(),
    }
    
    return render(request, 'calendario/eventos_lista.html', context)

@login_required
def eventos_json(request):
    """API JSON para eventos do calendário (para integração com plugins JS)"""
    start = request.GET.get('start')
    end = request.GET.get('end')
    
    try:
        start_date = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(end.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return JsonResponse({'error': 'Datas inválidas'}, status=400)
    
    eventos = EventoCalendario.objects.filter(
        usuario=request.user,
        data_inicio__gte=start_date,
        data_inicio__lt=end_date
    )
    
    eventos_json = []
    for evento in eventos:
        eventos_json.append({
            'id': evento.id,
            'title': evento.titulo,
            'start': evento.data_inicio.isoformat(),
            'end': evento.data_fim.isoformat(),
            'description': evento.descricao,
            'color': evento.get_cor_evento(),
            'tipo': evento.get_tipo_evento_display(),
            'materia': evento.materia.nome if evento.materia else None,
            'url': reverse('calendario:evento_detalhe', args=[evento.id])
        })
    
    return JsonResponse(eventos_json, safe=False)

@login_required
def dashboard_calendario(request):
    """Dashboard com resumo e estatísticas do calendário"""
    hoje = timezone.now().date()
    agora = timezone.now()
    
    # Eventos de hoje
    eventos_hoje = EventoCalendario.objects.filter(
        usuario=request.user,
        data_inicio__date=hoje
    ).order_by('data_inicio')
    
    # Próximos eventos (próximos 7 dias)
    proxima_semana = hoje + timedelta(days=7)
    proximos_eventos = EventoCalendario.objects.filter(
        usuario=request.user,
        data_inicio__date__gt=hoje,
        data_inicio__date__lte=proxima_semana
    ).order_by('data_inicio')[:5]
    
    # Estatísticas do mês atual
    primeiro_dia_mes = hoje.replace(day=1)
    if hoje.month == 12:
        ultimo_dia_mes = hoje.replace(year=hoje.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        ultimo_dia_mes = hoje.replace(month=hoje.month + 1, day=1) - timedelta(days=1)
    
    eventos_mes = EventoCalendario.objects.filter(
        usuario=request.user,
        data_inicio__date__gte=primeiro_dia_mes,
        data_inicio__date__lte=ultimo_dia_mes
    )
    
    # Estatísticas por tipo
    stats_por_tipo = {}
    for tipo, nome in EventoCalendario.TipoEvento.choices:
        stats_por_tipo[nome] = eventos_mes.filter(tipo_evento=tipo).count()
    
    context = {
        'eventos_hoje': eventos_hoje,
        'proximos_eventos': proximos_eventos,
        'total_eventos_mes': eventos_mes.count(),
        'stats_por_tipo': stats_por_tipo,
        'mes_atual': calendar.month_name[hoje.month],
        'ano_atual': hoje.year,
    }
    
    return render(request, 'calendario/dashboard.html', context)
