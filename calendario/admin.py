from django.contrib import admin
from .models import EventoCalendario, RecorrenciaEvento

@admin.register(EventoCalendario)
class EventoCalendarioAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'tipo_evento', 'data_inicio', 'data_fim', 
        'materia', 'usuario', 'criado_em'
    ]
    list_filter = [
        'tipo_evento', 'data_inicio', 'materia__semestre', 
        'lembrete', 'criado_em'
    ]
    search_fields = ['titulo', 'descricao', 'usuario__username']
    date_hierarchy = 'data_inicio'
    ordering = ['-data_inicio']
    readonly_fields = ['criado_em', 'atualizado_em']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'descricao', 'tipo_evento', 'materia')
        }),
        ('Data e Hora', {
            'fields': ('data_inicio', 'data_fim')
        }),
        ('Configurações', {
            'fields': ('cor_personalizada', 'lembrete', 'tempo_lembrete')
        }),
        ('Sistema', {
            'fields': ('usuario', 'criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'usuario', 'materia', 'materia__semestre'
        )

@admin.register(RecorrenciaEvento)
class RecorrenciaEventoAdmin(admin.ModelAdmin):
    list_display = [
        'evento', 'tipo_recorrencia', 'intervalo', 
        'data_fim_recorrencia'
    ]
    list_filter = ['tipo_recorrencia', 'data_fim_recorrencia']
    search_fields = ['evento__titulo']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('evento')
