"""
URLs para o app academico.
"""

from django.urls import path
from . import views, views_extra

app_name = 'academico'

urlpatterns = [
    # Matérias
    path('materias/', views_extra.materias_lista, name='materias_lista'),
    path('materias/nova/', views_extra.materia_create, name='materia_create'),
    path('materias/<slug:slug>/', views.materia_detail, name='materia_detail'),
    path('materias/<slug:slug>/editar/', views_extra.materia_edit, name='materia_edit'),
    path('materias/<slug:slug>/tutor/', views.materia_tutor, name='materia_tutor'),
    
    # Materiais didáticos
    path('materias/<slug:slug>/material/upload/', views.material_upload, name='material_upload'),
    path('materiais/<int:pk>/download/', views.material_download, name='material_download'),
    path('materiais/', views_extra.materials_lista, name='materials_lista'),
    
    # Eventos
    path('agenda/', views_extra.agenda_geral, name='agenda_geral'),
    path('eventos/novo/', views_extra.evento_geral_create, name='evento_geral_create'),
    path('materias/<slug:slug>/evento/novo/', views.evento_create, name='evento_create'),
    path('eventos/<int:pk>/editar/', views.evento_edit, name='evento_edit'),
    
    # Tarefas
    path('tarefas/', views_extra.todolist_geral, name='todolist_geral'),
    path('materias/<slug:slug>/tarefa/nova/', views.tarefa_create, name='tarefa_create'),
    path('tarefas/<int:pk>/editar/', views.tarefa_edit, name='tarefa_edit'),
    path('tarefas/<int:pk>/toggle/', views.tarefa_toggle_status, name='tarefa_toggle_status'),
    path('semestres/<int:pk>/tarefas/', views_extra.todolist_semestre, name='todolist_semestre'),

    # Horários de aula
    path('materias/<slug:slug>/horarios/', views_extra.horarios_materia, name='horarios_materia'),
    path('materias/<slug:slug>/horarios/novo/', views_extra.horario_create, name='horario_create'),
    path('horarios/<int:pk>/editar/', views_extra.horario_edit, name='horario_edit'),
    path('horarios/<int:pk>/excluir/', views_extra.horario_delete, name='horario_delete'),
]