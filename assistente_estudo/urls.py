"""
URL configuration for assistente_estudo project.

Sistema de Assistente de Estudos - Configuração principal de URLs
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.http import HttpResponseRedirect
from django.contrib.auth import logout
from django.urls import reverse


# Views de autenticação customizadas
from core.views_auth import RegistroView

# Configurar títulos do admin
admin.site.site_header = 'Assistente de Estudos - Administração'
admin.site.site_title = 'Assistente de Estudos'
admin.site.index_title = 'Painel de Administração'

def custom_logout_view(request):
    """
    View personalizada de logout que redireciona diretamente para a home
    sem mostrar uma página de logout intermediária.
    """
    logout(request)
    return HttpResponseRedirect(reverse('home'))


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('academico/', include('academico.urls')),
    path('calendario/', include('calendario.urls')),
    
    # Sistema de autenticação
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('auth/logout/', custom_logout_view, name='auth_logout'),  # Alias para compatibilidade
    path('registro/', RegistroView.as_view(), name='registro'),
    
    # URLs de autenticação padrão do Django (apenas para recuperação de senha)
    # path('auth/', include('django.contrib.auth.urls')),  # Removido para evitar conflito
]

# Servir arquivos de media em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
