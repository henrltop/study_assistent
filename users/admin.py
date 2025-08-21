from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, PerfilUsuario


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin customizado para o modelo CustomUser."""
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Informações Pessoais'), {
            'fields': ('first_name', 'last_name', 'email', 'data_nascimento', 'bio', 'avatar')
        }),
        (_('Permissões'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Configurações'), {
            'fields': ('tema_escuro', 'notificacoes_email', 'fuso_horario')
        }),
        (_('Datas Importantes'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'ativo', 'criado_em')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'ativo', 'tema_escuro')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('first_name', 'last_name')


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    """Admin para o modelo PerfilUsuario."""
    
    list_display = ('usuario', 'instituicao', 'curso', 'horas_estudo_dia', 'total_materias')
    list_filter = ('horas_estudo_dia', 'metodo_estudo_preferido')
    search_fields = ('usuario__username', 'usuario__email', 'instituicao', 'curso')
    readonly_fields = ('total_materias', 'total_eventos', 'total_tarefas_concluidas', 'criado_em', 'atualizado_em')
    
    fieldsets = (
        (_('Informações Acadêmicas'), {
            'fields': ('usuario', 'instituicao', 'curso', 'periodo_atual')
        }),
        (_('Configurações de Estudo'), {
            'fields': ('horas_estudo_dia', 'metodo_estudo_preferido')
        }),
        (_('Estatísticas'), {
            'fields': ('total_materias', 'total_eventos', 'total_tarefas_concluidas'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
