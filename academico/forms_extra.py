"""
Formulários adicionais para o app acadêmico.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.text import slugify
from .models import Materia, Semestre
import os


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


class SemestreForm(forms.ModelForm):
    """Formulário para cadastro/edição de semestres."""
    
    class Meta:
        model = Semestre
        fields = ['nome', 'ano', 'periodo', 'data_inicio', 'data_fim']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Semestre 2025.1'
            }),
            'ano': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2020,
                'max': 2030
            }),
            'periodo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'data_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'data_fim': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        labels = {
            'nome': 'Nome do Semestre',
            'ano': 'Ano',
            'periodo': 'Período',
            'data_inicio': 'Data de Início',
            'data_fim': 'Data de Término'
        }
    
    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        ano = cleaned_data.get('ano')
        periodo = cleaned_data.get('periodo')
        
        if data_inicio and data_fim:
            if data_fim <= data_inicio:
                raise ValidationError('A data de término deve ser posterior à data de início.')
        
        # Verificar se já existe um semestre com mesmo ano e período
        if ano and periodo:
            existing = Semestre.objects.filter(
                ano=ano,
                periodo=periodo
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing.exists():
                raise ValidationError('Já existe um semestre para este ano e período.')
        
        return cleaned_data
