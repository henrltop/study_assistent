from django.urls import path
from . import views

app_name = 'calendario'

urlpatterns = [
    # Página principal do calendário
    path('', views.calendario_home, name='calendario_home'),
    
    # Dashboard
    path('dashboard/', views.dashboard_calendario, name='dashboard'),
    
    # CRUD de eventos
    path('evento/criar/', views.evento_criar, name='evento_criar'),
    path('evento/<int:evento_id>/', views.evento_detalhe, name='evento_detalhe'),
    path('evento/<int:evento_id>/editar/', views.evento_editar, name='evento_editar'),
    path('evento/<int:evento_id>/excluir/', views.evento_excluir, name='evento_excluir'),
    
    # Lista de eventos com filtros
    path('eventos/', views.eventos_lista, name='eventos_lista'),
    
    # API JSON para integração
    path('api/eventos/', views.eventos_json, name='eventos_json'),
]
