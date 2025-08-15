"""
URLs para o app academico - funcionalidades específicas de matérias.
"""

from django.urls import path
from . import views, views_extra

app_name = 'academico'

urlpatterns = [
    # Listagens gerais (URLs diretas para compatibilidade)
    path('', views_extra.materias_lista, name='materias_lista'),
    path('agenda/', views_extra.agenda_geral, name='agenda_geral'),
    path('tarefas/', views_extra.todolist_geral, name='todolist_geral'),
    path('materiais/', views_extra.materials_lista, name='materials_lista'),
    
    # CRUD de matérias
    path('nova/', views_extra.materia_create, name='materia_create'),
    path('<slug:slug>/', views.materia_detail, name='materia_detail'),
    path('<slug:slug>/editar/', views_extra.materia_edit, name='materia_edit'),
    path('<slug:slug>/tutor/', views.materia_tutor, name='materia_tutor'),
    
    # Upload e download de materiais
    path('<slug:slug>/material/upload/', views.material_upload, name='material_upload'),
    path('materiais/<int:pk>/download/', views.material_download, name='material_download'),
    
    # Eventos
    path('eventos/novo/', views_extra.evento_geral_create, name='evento_geral_create'),
    path('<slug:slug>/evento/novo/', views.evento_create, name='evento_create'),
    path('eventos/<int:pk>/editar/', views.evento_edit, name='evento_edit'),
    
    # Tarefas da matéria
    path('<slug:slug>/tarefa/nova/', views.tarefa_create, name='tarefa_create'),
    path('tarefas/<int:pk>/editar/', views.tarefa_edit, name='tarefa_edit'),
    path('tarefas/<int:pk>/toggle/', views.tarefa_toggle_status, name='tarefa_toggle_status'),
    
    # Tarefas por semestre
    path('semestres/<int:pk>/tarefas/', views_extra.todolist_semestre, name='todolist_semestre'),
]
