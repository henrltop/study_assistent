"""
Formulários para o app acadêmico.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.text import slugify
from .models import Materia, MaterialDidatico, EventoAgenda, Tarefa, Semestre, HorarioAula, HorarioAula
import os


class MaterialDidaticoForm(forms.ModelForm):
    """Formulário para upload de materiais didáticos."""
    
    class Meta:
        model = MaterialDidatico
        fields = ['titulo', 'arquivo', 'tipo']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o título do material'
            }),
            'arquivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.txt,.doc,.docx,.md'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'titulo': 'Título do Material',
            'arquivo': 'Arquivo',
            'tipo': 'Tipo de Arquivo'
        }
        help_texts = {
            'arquivo': 'Formatos aceitos: PDF, TXT, DOC, DOCX, MD (máximo 50MB)',
            'tipo': 'O tipo será detectado automaticamente se não informado'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].required = False  # Será determinado automaticamente
    
    def clean_arquivo(self):
        arquivo = self.cleaned_data.get('arquivo')
        
        if not arquivo:
            raise ValidationError('É necessário selecionar um arquivo.')
        
        # Verificar tamanho do arquivo
        max_size = 50 * 1024 * 1024  # 50MB
        if arquivo.size > max_size:
            raise ValidationError('O arquivo é muito grande. Tamanho máximo: 50MB.')
        
        # Verificar extensão
        extensoes_permitidas = ['.pdf', '.txt', '.doc', '.docx', '.md']
        nome_arquivo = arquivo.name.lower()
        
        if not any(nome_arquivo.endswith(ext) for ext in extensoes_permitidas):
            raise ValidationError('Formato de arquivo não permitido. Use: PDF, TXT, DOC, DOCX ou MD.')
        
        return arquivo
    
    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')
        
        if not titulo or not titulo.strip():
            raise ValidationError('O título é obrigatório.')
        
        return titulo.strip()


class EventoAgendaForm(forms.ModelForm):
    """Formulário para criação/edição de eventos da agenda."""
    
    class Meta:
        model = EventoAgenda
        fields = ['titulo', 'descricao', 'tipo', 'data_inicio', 'data_fim']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o título do evento'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição do evento (opcional)'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'data_inicio': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'data_fim': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }
        labels = {
            'titulo': 'Título do Evento',
            'descricao': 'Descrição',
            'tipo': 'Tipo de Evento',
            'data_inicio': 'Data e Hora de Início',
            'data_fim': 'Data e Hora de Término (opcional)'
        }
        help_texts = {
            'data_fim': 'Se não informada, será considerado um evento pontual',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_fim'].required = False
        self.fields['descricao'].required = False
    
    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')
        
        if not titulo or not titulo.strip():
            raise ValidationError('O título é obrigatório.')
        
        return titulo.strip()
    
    def clean_data_inicio(self):
        data_inicio = self.cleaned_data.get('data_inicio')
        
        if not data_inicio:
            raise ValidationError('A data de início é obrigatória.')
        
        # Verificar se não é no passado (para eventos novos)
        if not self.instance.pk and data_inicio < timezone.now():
            raise ValidationError('A data de início não pode ser no passado.')
        
        return data_inicio
    
    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        
        if data_inicio and data_fim:
            if data_fim <= data_inicio:
                raise ValidationError('A data de término deve ser posterior à data de início.')
        
        return cleaned_data


class TarefaForm(forms.ModelForm):
    """Formulário para criação/edição de tarefas."""
    
    # Campo adicional para sugerir datas das aulas
    data_sugerida = forms.ChoiceField(
        label='Data Sugerida',
        choices=[],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_data_sugerida'
        }),
        help_text='Próximas datas de aula desta matéria'
    )
    
    class Meta:
        model = Tarefa
        fields = ['titulo', 'descricao', 'status', 'prazo']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o título da tarefa'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descrição da tarefa (opcional)'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'prazo': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'id': 'id_prazo_manual'
            }),
        }
        labels = {
            'titulo': 'Título da Tarefa',
            'descricao': 'Descrição',
            'status': 'Status',
            'prazo': 'Prazo Personalizado (opcional)'
        }
        help_texts = {
            'prazo': 'Use este campo para datas personalizadas fora dos dias de aula',
        }
    
    def __init__(self, *args, materia=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['descricao'].required = False
        self.fields['prazo'].required = False
        
        # Gerar opções de datas das aulas
        if materia:
            from datetime import datetime
            proximas_datas = materia.get_proximas_aulas(limite=10)
            
            choices = [('', 'Selecione uma data de aula')]
            for data in proximas_datas:
                dia_nome = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'][data.weekday()]
                data_formatada = data.strftime('%Y-%m-%d')
                data_display = f"{dia_nome}, {data.strftime('%d/%m/%Y')}"
                choices.append((data_formatada, data_display))
            
            choices.append(('personalizado', '📅 Data personalizada'))
            self.fields['data_sugerida'].choices = choices
    
    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')
        
        if not titulo or not titulo.strip():
            raise ValidationError('O título é obrigatório.')
        
        return titulo.strip()
    
    def clean(self):
        cleaned_data = super().clean()
        data_sugerida = cleaned_data.get('data_sugerida')
        prazo = cleaned_data.get('prazo')
        
        # Se selecionou uma data sugerida que não é personalizada
        if data_sugerida and data_sugerida != 'personalizado' and data_sugerida != '':
            from datetime import datetime
            try:
                # Converter para datetime (assumir 23:59 do dia)
                data_obj = datetime.strptime(data_sugerida, '%Y-%m-%d')
                data_obj = data_obj.replace(hour=23, minute=59)
                cleaned_data['prazo'] = timezone.make_aware(data_obj)
            except ValueError:
                pass
        
        # Validar prazo se foi informado
        prazo_final = cleaned_data.get('prazo')
        if prazo_final and prazo_final < timezone.now() - timezone.timedelta(hours=1):
            raise ValidationError('O prazo não pode ser no passado.')
        
        return cleaned_data


class MateriaForm(forms.ModelForm):
    """Formulário para cadastro/edição de matérias."""
    
    class Meta:
        model = Materia
        fields = ['semestre', 'nome', 'descricao']
        widgets = {
            'semestre': forms.Select(attrs={
                'class': 'form-select'
            }),
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome da matéria'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descrição da matéria (opcional)'
            }),
        }
        labels = {
            'semestre': 'Semestre',
            'nome': 'Nome da Matéria',
            'descricao': 'Descrição'
        }
        help_texts = {
            'nome': 'Nome único da matéria/disciplina',
            'descricao': 'Breve descrição sobre a matéria',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar apenas semestres ativos
        self.fields['semestre'].queryset = Semestre.objects.filter(ativo=True)
        self.fields['descricao'].required = False
    
    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        
        if not nome or not nome.strip():
            raise ValidationError('O nome da matéria é obrigatório.')
        
        nome = nome.strip()
        
        # Verificar se já existe uma matéria com este nome no mesmo semestre
        semestre = self.cleaned_data.get('semestre')
        if semestre:
            existing = Materia.objects.filter(
                semestre=semestre,
                nome__iexact=nome
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing.exists():
                raise ValidationError('Já existe uma matéria com este nome neste semestre.')
        
        return nome
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Gerar slug único se não existe
        if not instance.slug:
            base_slug = slugify(instance.nome)
            slug = base_slug
            counter = 1
            
            while Materia.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            instance.slug = slug
        
        if commit:
            instance.save()
        
        return instance


class HorarioAulaForm(forms.ModelForm):
    """Formulário para horários de aula das matérias."""
    
    class Meta:
        model = HorarioAula
        fields = ['dia_semana', 'hora_inicio', 'hora_fim', 'local', 'observacoes']
        widgets = {
            'dia_semana': forms.Select(attrs={
                'class': 'form-select'
            }),
            'hora_inicio': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'hora_fim': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'local': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Sala 201, Lab. de Informática'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Informações adicionais sobre a aula...'
            }),
        }
        labels = {
            'dia_semana': 'Dia da Semana',
            'hora_inicio': 'Horário de Início',
            'hora_fim': 'Horário de Término',
            'local': 'Local/Sala',
            'observacoes': 'Observações'
        }
    
    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fim = cleaned_data.get('hora_fim')
        
        if hora_inicio and hora_fim:
            if hora_fim <= hora_inicio:
                raise ValidationError('O horário de término deve ser posterior ao horário de início.')
            
            # Verificar se não é uma aula muito longa (mais de 8 horas)
            from datetime import datetime, timedelta
            inicio = datetime.combine(datetime.today(), hora_inicio)
            fim = datetime.combine(datetime.today(), hora_fim)
            duracao = fim - inicio
            
            if duracao > timedelta(hours=8):
                raise ValidationError('A aula não pode durar mais de 8 horas.')
        
        return cleaned_data


# FormSet para gerenciar múltiplos horários de uma vez
HorarioAulaFormSet = forms.inlineformset_factory(
    Materia, 
    HorarioAula,
    form=HorarioAulaForm,
    extra=2,  # Começar com 2 horários vazios
    can_delete=True,
    min_num=0,
    validate_min=False
)

class MateriaComHorariosForm(forms.ModelForm):
    """Formulário para matéria com horários integrados."""
    
    class Meta:
        model = Materia
        fields = ['semestre', 'nome', 'descricao']
        widgets = {
            'semestre': forms.Select(attrs={
                'class': 'form-select'
            }),
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome da matéria'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descrição da matéria (opcional)'
            }),
        }
        labels = {
            'semestre': 'Semestre',
            'nome': 'Nome da Matéria',
            'descricao': 'Descrição'
        }
        help_texts = {
            'nome': 'Nome único da matéria/disciplina',
            'descricao': 'Breve descrição sobre a matéria',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar apenas semestres ativos
        self.fields['semestre'].queryset = Semestre.objects.filter(ativo=True)
        self.fields['descricao'].required = False
    
    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        
        if not nome or not nome.strip():
            raise ValidationError('O nome da matéria é obrigatório.')
        
        nome = nome.strip()
        
        # Verificar se já existe uma matéria com este nome no mesmo semestre
        semestre = self.cleaned_data.get('semestre')
        if semestre:
            existing = Materia.objects.filter(
                semestre=semestre,
                nome__iexact=nome
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing.exists():
                raise ValidationError('Já existe uma matéria com este nome neste semestre.')
        
        return nome
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Gerar slug único se não existe
        if not instance.slug:
            base_slug = slugify(instance.nome)
            slug = base_slug
            counter = 1
            
            while Materia.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            instance.slug = slug
        
        if commit:
            instance.save()
        
        return instance
