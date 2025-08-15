"""
Views de autenticação personalizadas.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.views import View
from django.contrib.auth.models import User
from django import forms


class RegistroForm(UserCreationForm):
    """Formulário de registro personalizado."""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu email'
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu nome'
        }),
        label='Nome'
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Digite um nome de usuário'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Digite uma senha'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirme sua senha'
        })
        
        # Customizar labels
        self.fields['username'].label = 'Nome de Usuário'
        self.fields['password1'].label = 'Senha'
        self.fields['password2'].label = 'Confirmar Senha'
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        if commit:
            user.save()
        return user


class RegistroView(View):
    """View para registro de novos usuários."""
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
            
        form = RegistroForm()
        return render(request, 'registration/registro.html', {
            'form': form,
            'titulo_pagina': 'Criar Conta'
        })
    
    def post(self, request):
        if request.user.is_authenticated:
            return redirect('home')
            
        form = RegistroForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada para {username}! Você foi logado automaticamente.')
            
            # Fazer login automático após o registro
            login(request, user)
            return redirect('home')
        
        return render(request, 'registration/registro.html', {
            'form': form,
            'titulo_pagina': 'Criar Conta'
        })
