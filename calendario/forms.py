from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import EventoCalendario, RecorrenciaEvento
from academico.models import Materia
import datetime

class EventoCalendarioForm(forms.ModelForm):
    class Meta:
        model = EventoCalendario
        fields = [
            'titulo', 'descricao', 'data_inicio', 'data_fim', 
            'tipo_evento', 'materia', 'cor_personalizada',
            'lembrete', 'tempo_lembrete'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Prova de Matemática'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descreva detalhes do evento...'
            }),
            'data_inicio': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'data_fim': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'tipo_evento': forms.Select(attrs={
                'class': 'form-select'
            }),
            'materia': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cor_personalizada': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'style': 'height: 50px;'
            }),
            'lembrete': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'tempo_lembrete': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '5',
                'max': '1440',
                'step': '5'
            })
        }
        labels = {
            'titulo': _('Título do Evento'),
            'descricao': _('Descrição'),
            'data_inicio': _('Data e Hora de Início'),
            'data_fim': _('Data e Hora de Término'),
            'tipo_evento': _('Tipo de Evento'),
            'materia': _('Matéria (Opcional)'),
            'cor_personalizada': _('Cor Personalizada'),
            'lembrete': _('Ativar Lembrete'),
            'tempo_lembrete': _('Lembrete (minutos antes)')
        }
        help_texts = {
            'cor_personalizada': _('Escolha uma cor personalizada para este evento'),
            'tempo_lembrete': _('Quantos minutos antes do evento você deseja ser lembrado'),
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Como as matérias são globais no sistema, mostrar todas as ativas
        self.fields['materia'].queryset = Materia.objects.filter(
            ativo=True
        ).order_by('nome')
        
        # Adicionar opção vazia para matéria
        self.fields['materia'].empty_label = "Selecione uma matéria (opcional)"
        
        # Definir valores iniciais de data/hora apenas se for um novo evento 
        # e não foram fornecidos valores iniciais
        if not self.instance.pk and not args and not kwargs.get('initial'):
            now = timezone.now()
            rounded_now = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
            self.fields['data_inicio'].initial = rounded_now.strftime('%Y-%m-%dT%H:%M')
            self.fields['data_fim'].initial = (rounded_now + datetime.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M')
    
    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        
        # Validar se a data de término é posterior à data de início
        if data_inicio and data_fim:
            if data_fim <= data_inicio:
                self.add_error('data_fim', _('A data de término deve ser posterior à data de início.'))
            
            # Validar se o evento não é muito longo (máximo 12 horas)
            duracao = data_fim - data_inicio
            if duracao.total_seconds() > 12 * 3600:  # 12 horas em segundos
                self.add_error('data_fim', _('O evento não pode durar mais de 12 horas.'))
        
        # Validar tempo do lembrete
        tempo_lembrete = cleaned_data.get('tempo_lembrete')
        if tempo_lembrete and (tempo_lembrete < 5 or tempo_lembrete > 1440):
            self.add_error('tempo_lembrete', _('O tempo do lembrete deve ser entre 5 minutos e 24 horas (1440 minutos).'))
        
        return cleaned_data

class RecorrenciaEventoForm(forms.ModelForm):
    class Meta:
        model = RecorrenciaEvento
        fields = [
            'tipo_recorrencia', 'data_fim_recorrencia', 
            'intervalo', 'dias_semana'
        ]
        widgets = {
            'tipo_recorrencia': forms.Select(attrs={
                'class': 'form-select'
            }),
            'data_fim_recorrencia': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'intervalo': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '52'
            }),
            'dias_semana': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 1,3,5 (Seg, Qua, Sex)'
            })
        }
        labels = {
            'tipo_recorrencia': _('Tipo de Recorrência'),
            'data_fim_recorrencia': _('Data Final (Opcional)'),
            'intervalo': _('Intervalo'),
            'dias_semana': _('Dias da Semana')
        }
        help_texts = {
            'data_fim_recorrencia': _('Deixe em branco para recorrência sem fim'),
            'intervalo': _('A cada quantos períodos repetir (ex: a cada 2 semanas)'),
            'dias_semana': _('Para recorrência semanal: 1=Seg, 2=Ter, 3=Qua, 4=Qui, 5=Sex, 6=Sáb, 7=Dom')
        }
    
    def clean_dias_semana(self):
        dias_semana = self.cleaned_data.get('dias_semana')
        tipo_recorrencia = self.cleaned_data.get('tipo_recorrencia')
        
        if tipo_recorrencia == 'semanal' and dias_semana:
            # Validar formato dos dias da semana
            try:
                dias = [int(dia.strip()) for dia in dias_semana.split(',')]
                for dia in dias:
                    if dia < 1 or dia > 7:
                        raise ValueError()
                return ','.join(str(dia) for dia in sorted(set(dias)))
            except (ValueError, AttributeError):
                raise forms.ValidationError(
                    _('Formato inválido. Use números de 1 a 7 separados por vírgula (ex: 1,3,5)')
                )
        
        return dias_semana

class FiltroEventosForm(forms.Form):
    """Form para filtrar eventos na visualização do calendário"""
    
    PERIODO_CHOICES = [
        ('hoje', _('Hoje')),
        ('semana', _('Esta Semana')),
        ('mes', _('Este Mês')),
        ('personalizado', _('Período Personalizado'))
    ]
    
    periodo = forms.ChoiceField(
        choices=PERIODO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    tipo_evento = forms.MultipleChoiceField(
        choices=EventoCalendario.TipoEvento.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    materia = forms.ModelChoiceField(
        queryset=Materia.objects.none(),
        required=False,
        empty_label=_("Todas as matérias"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['materia'].queryset = Materia.objects.filter(
                semestre__usuario=user
            ).order_by('nome')
