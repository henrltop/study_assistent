"""
URLs para o app academico - funcionalidades específicas de matérias.
"""

from django.urls import path
from . import views

app_name = 'academico'

urlpatterns = [
    # Matéria específica
    path('materias/<slug:slug>/', views.materia_detail, name='materia_detail'),
    path('materias/<slug:slug>/tutor/', views.materia_tutor, name='materia_tutor'),
    
    # Upload e download de materiais
    path('materias/<slug:slug>/material/upload/', views.material_upload, name='material_upload'),
    path('materiais/<int:pk>/download/', views.material_download, name='material_download'),
    
    # Eventos da matéria
    path('materias/<slug:slug>/evento/novo/', views.evento_create, name='evento_create'),
    path('eventos/<int:pk>/editar/', views.evento_edit, name='evento_edit'),
    
    # Tarefas da matéria
    path('materias/<slug:slug>/tarefa/nova/', views.tarefa_create, name='tarefa_create'),
    path('tarefas/<int:pk>/editar/', views.tarefa_edit, name='tarefa_edit'),
    path('tarefas/<int:pk>/toggle/', views.tarefa_toggle_status, name='tarefa_toggle_status'),
]
