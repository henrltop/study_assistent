from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """Modelo de usuário personalizado para o sistema."""
    
    email = models.EmailField(_('Email'), unique=True)
    first_name = models.CharField(_('Nome'), max_length=150)
    last_name = models.CharField(_('Sobrenome'), max_length=150)
    data_nascimento = models.DateField(_('Data de Nascimento'), null=True, blank=True)
    bio = models.TextField(_('Biografia'), max_length=500, blank=True)
    avatar = models.ImageField(
        _('Avatar'),
        upload_to='avatars/%Y/%m/',
        null=True,
        blank=True
    )
    
    # Configurações de preferências
    tema_escuro = models.BooleanField(_('Tema Escuro'), default=True)
    notificacoes_email = models.BooleanField(_('Receber Notificações por Email'), default=True)
    fuso_horario = models.CharField(
        _('Fuso Horário'),
        max_length=50,
        default='America/Sao_Paulo'
    )
    
    # Campos de controle
    criado_em = models.DateTimeField(_('Criado em'), auto_now_add=True)
    atualizado_em = models.DateTimeField(_('Atualizado em'), auto_now=True)
    ativo = models.BooleanField(_('Ativo'), default=True)
    
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = _('Usuário')
        verbose_name_plural = _('Usuários')
        ordering = ['first_name', 'last_name']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.username})" if self.get_full_name() else self.username
    
    def get_nome_completo(self):
        """Retorna o nome completo do usuário."""
        return self.get_full_name()
    
    def get_iniciais(self):
        """Retorna as iniciais do usuário."""
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        elif self.first_name:
            return self.first_name[0].upper()
        else:
            return self.username[0].upper()

class PerfilUsuario(models.Model):
    """Informações adicionais do perfil do usuário."""
    
    usuario = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name=_('Usuário')
    )
    
    # Informações acadêmicas
    instituicao = models.CharField(_('Instituição de Ensino'), max_length=200, blank=True)
    curso = models.CharField(_('Curso'), max_length=200, blank=True)
    periodo_atual = models.CharField(_('Período Atual'), max_length=50, blank=True)
    
    # Configurações de estudo
    horas_estudo_dia = models.IntegerField(
        _('Meta de Horas de Estudo por Dia'),
        default=4,
        help_text=_('Quantidade de horas que pretende estudar por dia')
    )
    metodo_estudo_preferido = models.CharField(
        _('Método de Estudo Preferido'),
        max_length=100,
        blank=True,
        help_text=_('Ex: Pomodoro, Flashcards, Mapas Mentais')
    )
    
    # Estatísticas
    total_materias = models.IntegerField(_('Total de Matérias'), default=0)
    total_eventos = models.IntegerField(_('Total de Eventos'), default=0)
    total_tarefas_concluidas = models.IntegerField(_('Total de Tarefas Concluídas'), default=0)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Perfil do Usuário')
        verbose_name_plural = _('Perfis dos Usuários')
    
    def __str__(self):
        return f"Perfil de {self.usuario.get_full_name()}"
    
    def atualizar_estatisticas(self):
        """Atualiza as estatísticas do perfil."""
        from academico.models import Materia, Tarefa
        from calendario.models import EventoCalendario
        
        self.total_materias = Materia.objects.filter(
            semestre__usuario=self.usuario
        ).count()
        
        self.total_eventos = EventoCalendario.objects.filter(
            usuario=self.usuario
        ).count()
        
        self.total_tarefas_concluidas = Tarefa.objects.filter(
            usuario=self.usuario,
            status='CONCLUIDA'
        ).count()
        
        self.save(update_fields=['total_materias', 'total_eventos', 'total_tarefas_concluidas'])

class Semestre(models.Model):
    # ...existing code...
    usuario = models.ForeignKey('CustomUser', on_delete=models.CASCADE, null=True, blank=True)
    # ...existing code...
