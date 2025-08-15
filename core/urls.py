"""
URLs para o app core - páginas principais.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Página inicial
    path('', views.home, name='home'),
    
    # Chat da home (placeholder)
    path('chat/', views.chat_home, name='chat_home'),
    
    # Semestres
    path('semestres/', views.semestres_lista, name='semestres_lista'),
    path('semestres/<int:pk>/', views.semestre_detail, name='semestre_detail'),
    path('semestres/<int:pk>/agente/', views.semestre_agente, name='semestre_agente'),
    
    # Busca global
    path('buscar/', views.buscar, name='buscar'),
    
    # Evento form placeholder
    path('evento/form/', views.evento_form, name='evento_form'),
]
