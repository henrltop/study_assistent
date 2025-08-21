"""
Middleware customizado para controle de autenticação.
"""

from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings


class AuthRequiredMiddleware:
    """
    Middleware que redireciona usuários não logados para a página de apresentação
    quando tentam acessar áreas que requerem autenticação.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # URLs que não requerem login (públicas)
        self.public_urls = [
            reverse('home'),
            reverse('login'), 
            reverse('registro'),
            '/admin/',  # Django admin tem seu próprio controle
        ]
        # Prefixes de URLs públicas
        self.public_prefixes = [
            '/static/',
            '/media/',
            '/admin/',
        ]

    def __call__(self, request):
        # Verificar se a URL atual é pública
        current_url = request.path_info
        
        # Se usuário está logado, deixar passar
        if request.user.is_authenticated:
            response = self.get_response(request)
            return response
            
        # Se a URL é pública, deixar passar
        if (current_url in self.public_urls or 
            any(current_url.startswith(prefix) for prefix in self.public_prefixes)):
            response = self.get_response(request)
            return response
            
        # Se chegou até aqui, usuário não logado tentando acessar área restrita
        # Redirecionar para home (que mostra a página de apresentação)
        return redirect('home')

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Processa views antes da execução para adicionar informações de contexto.
        """
        return None
