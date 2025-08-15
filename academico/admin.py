from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Semestre, Materia, MaterialDidatico, 
    EventoAgenda, Tarefa, AcessoMateria, HorarioAula
)


@admin.register(Semestre)
class SemestreAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ano', 'get_periodo_display', 'data_inicio', 'data_fim', 'ativo']
    list_filter = ['ano', 'periodo', 'ativo']
    search_fields = ['nome']
    ordering = ['-ano', '-periodo']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'ano', 'periodo')
        }),
        ('Datas', {
            'fields': ('data_inicio', 'data_fim')
        }),
        ('Status', {
            'fields': ('ativo',)
        }),
    )


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'semestre', 'contador_acessos', 'ativo', 'criado_em']
    list_filter = ['semestre', 'ativo', 'criado_em']
    search_fields = ['nome', 'descricao']
    prepopulated_fields = {'slug': ('nome',)}
    ordering = ['nome']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'slug', 'semestre', 'descricao')
        }),
        ('Estatísticas', {
            'fields': ('contador_acessos',)
        }),
        ('Status', {
            'fields': ('ativo',)
        }),
    )
    
    readonly_fields = ['contador_acessos', 'criado_em']


@admin.register(MaterialDidatico)
class MaterialDidaticoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'materia', 'tipo', 'get_tamanho', 'data_upload', 'usuario']
    list_filter = ['tipo', 'materia__semestre', 'data_upload']
    search_fields = ['titulo', 'materia__nome']
    ordering = ['-data_upload']
    
    def get_tamanho(self, obj):
        return obj.get_tamanho_arquivo()
    get_tamanho.short_description = 'Tamanho'
    
    fieldsets = (
        ('Material', {
            'fields': ('titulo', 'materia', 'arquivo', 'tipo')
        }),
        ('Informações', {
            'fields': ('usuario',)
        }),
    )
    
    readonly_fields = ['data_upload']


@admin.register(EventoAgenda)
class EventoAgendaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'escopo', 'tipo', 'data_inicio', 'get_contexto', 'eh_futuro']
    list_filter = ['escopo', 'tipo', 'data_inicio', 'semestre']
    search_fields = ['titulo', 'descricao']
    date_hierarchy = 'data_inicio'
    ordering = ['data_inicio']
    
    def get_contexto(self, obj):
        if obj.escopo == 'SEMESTRE' and obj.semestre:
            return obj.semestre.nome
        elif obj.escopo == 'MATERIA' and obj.materia:
            return obj.materia.nome
        return 'Geral'
    get_contexto.short_description = 'Contexto'
    
    def eh_futuro(self, obj):
        if obj.eh_futuro:
            return format_html('<span style="color: green;">✓ Futuro</span>')
        return format_html('<span style="color: red;">✗ Passado</span>')
    eh_futuro.short_description = 'Status'
    
    fieldsets = (
        ('Evento', {
            'fields': ('titulo', 'descricao', 'tipo')
        }),
        ('Data e Hora', {
            'fields': ('data_inicio', 'data_fim')
        }),
        ('Escopo', {
            'fields': ('escopo', 'semestre', 'materia')
        }),
        ('Criação', {
            'fields': ('usuario',)
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Adicionar JavaScript para mostrar/esconder campos baseado no escopo
        return form


@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'materia', 'status', 'prazo', 'get_status_prazo', 'criado_em']
    list_filter = ['status', 'materia__semestre', 'prazo', 'criado_em']
    search_fields = ['titulo', 'descricao', 'materia__nome']
    date_hierarchy = 'prazo'
    ordering = ['prazo', '-criado_em']
    
    actions = ['marcar_como_concluida', 'marcar_como_pendente']
    
    def get_status_prazo(self, obj):
        if obj.status == 'CONCLUIDA':
            return format_html('<span style="color: green;">✓ Concluída</span>')
        elif obj.esta_atrasada:
            return format_html('<span style="color: red;">⚠ Atrasada</span>')
        elif obj.dias_para_prazo is not None and obj.dias_para_prazo <= 3:
            return format_html('<span style="color: orange;">⏰ Urgente</span>')
        return format_html('<span style="color: blue;">📋 Normal</span>')
    get_status_prazo.short_description = 'Status do Prazo'
    
    def marcar_como_concluida(self, request, queryset):
        updated = queryset.update(status='CONCLUIDA')
        self.message_user(request, f'{updated} tarefa(s) marcada(s) como concluída(s).')
    marcar_como_concluida.short_description = "Marcar como concluída"
    
    def marcar_como_pendente(self, request, queryset):
        updated = queryset.update(status='PENDENTE')
        self.message_user(request, f'{updated} tarefa(s) marcada(s) como pendente(s).')
    marcar_como_pendente.short_description = "Marcar como pendente"
    
    fieldsets = (
        ('Tarefa', {
            'fields': ('titulo', 'descricao', 'materia')
        }),
        ('Status e Prazo', {
            'fields': ('status', 'prazo')
        }),
        ('Criação', {
            'fields': ('usuario',)
        }),
    )
    
    readonly_fields = ['criado_em', 'atualizado_em']


@admin.register(AcessoMateria)
class AcessoMateriaAdmin(admin.ModelAdmin):
    list_display = ['materia', 'usuario', 'data_hora', 'ip_address']
    list_filter = ['materia__semestre', 'data_hora']
    search_fields = ['materia__nome', 'usuario__username']
    date_hierarchy = 'data_hora'
    ordering = ['-data_hora']
    
    readonly_fields = ['materia', 'usuario', 'data_hora', 'ip_address']
    
    def has_add_permission(self, request):
        return False  # Não permitir adicionar manualmente
    
    def has_change_permission(self, request, obj=None):
        return False  # Não permitir editar


@admin.register(HorarioAula)
class HorarioAulaAdmin(admin.ModelAdmin):
    list_display = ['materia', 'get_dia_semana_display', 'hora_inicio', 'hora_fim', 'get_duracao', 'local', 'ativo']
    list_filter = ['dia_semana', 'ativo', 'materia__semestre']
    search_fields = ['materia__nome', 'local']
    ordering = ['materia', 'dia_semana', 'hora_inicio']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('materia', 'dia_semana')
        }),
        ('Horários', {
            'fields': ('hora_inicio', 'hora_fim')
        }),
        ('Local e Observações', {
            'fields': ('local', 'observacoes')
        }),
        ('Status', {
            'fields': ('ativo',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('materia')
    
    def save_model(self, request, obj, form, change):
        # Validar se hora_fim é maior que hora_inicio
        if obj.hora_fim <= obj.hora_inicio:
            from django.core.exceptions import ValidationError
            raise ValidationError('A hora de término deve ser posterior à hora de início.')
        super().save_model(request, obj, form, change)
