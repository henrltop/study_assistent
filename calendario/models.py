from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from academico.models import Materia

class EventoCalendario(models.Model):
    class TipoEvento(models.TextChoices):
        PROVA = 'prova', _('Prova/Exame')
        AULA = 'aula', _('Aula')
        TRABALHO = 'trabalho', _('Trabalho/Projeto')
        ESTUDO = 'estudo', _('Sessão de Estudo')
        REUNIAO = 'reuniao', _('Reunião')
        OUTRO = 'outro', _('Outro')
    
    titulo = models.CharField(_("Título"), max_length=200)
    descricao = models.TextField(_("Descrição"), blank=True)
    data_inicio = models.DateTimeField(_("Data e Hora de Início"))
    data_fim = models.DateTimeField(_("Data e Hora de Término"))
    tipo_evento = models.CharField(
        _("Tipo de Evento"),
        max_length=20,
        choices=TipoEvento.choices,
        default=TipoEvento.OUTRO
    )
    materia = models.ForeignKey(
        Materia, 
        on_delete=models.CASCADE, 
        related_name="eventos_calendario",
        verbose_name=_("Matéria"),
        null=True,
        blank=True
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="eventos_calendario",
        verbose_name=_("Usuário")
    )
    cor_personalizada = models.CharField(
        _("Cor Personalizada"),
        max_length=7,
        blank=True,
        help_text=_("Cor em formato hexadecimal (ex: #FF7A00)")
    )
    lembrete = models.BooleanField(_("Ativar Lembrete"), default=True)
    tempo_lembrete = models.IntegerField(
        _("Tempo do Lembrete (minutos)"),
        default=30,
        help_text=_("Quantos minutos antes do evento enviar o lembrete")
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['data_inicio']
        verbose_name = _("Evento do Calendário")
        verbose_name_plural = _("Eventos do Calendário")
        indexes = [
            models.Index(fields=['data_inicio']),
            models.Index(fields=['usuario', 'data_inicio']),
            models.Index(fields=['tipo_evento']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.data_inicio.strftime('%d/%m/%Y %H:%M')}"
    
    def get_cor_evento(self):
        """Retorna a cor do evento baseada no tipo ou cor personalizada"""
        if self.cor_personalizada:
            return self.cor_personalizada
        
        cores_tipo = {
            'prova': '#DC3545',      # Vermelho
            'aula': '#28A745',       # Verde
            'trabalho': '#FFC107',   # Amarelo
            'estudo': '#007BFF',     # Azul
            'reuniao': '#6F42C1',    # Roxo
            'outro': '#FF7A00',      # Laranja (tema do sistema)
        }
        return cores_tipo.get(self.tipo_evento, '#FF7A00')
    
    def duracao_em_horas(self):
        """Calcula a duração do evento em horas"""
        if self.data_fim and self.data_inicio:
            duracao = self.data_fim - self.data_inicio
            return round(duracao.total_seconds() / 3600, 2)
        return 0

class RecorrenciaEvento(models.Model):
    class TipoRecorrencia(models.TextChoices):
        DIARIA = 'diaria', _('Diária')
        SEMANAL = 'semanal', _('Semanal')
        QUINZENAL = 'quinzenal', _('Quinzenal')
        MENSAL = 'mensal', _('Mensal')
        ANUAL = 'anual', _('Anual')
    
    evento = models.OneToOneField(
        EventoCalendario,
        on_delete=models.CASCADE,
        related_name="recorrencia",
        verbose_name=_("Evento")
    )
    tipo_recorrencia = models.CharField(
        _("Tipo de Recorrência"),
        max_length=20,
        choices=TipoRecorrencia.choices
    )
    data_fim_recorrencia = models.DateField(
        _("Data Final da Recorrência"),
        null=True,
        blank=True,
        help_text=_("Deixe em branco para recorrência infinita")
    )
    intervalo = models.PositiveIntegerField(
        _("Intervalo"),
        default=1,
        help_text=_("A cada quantos períodos repetir (ex: a cada 2 semanas)")
    )
    dias_semana = models.CharField(
        _("Dias da Semana"),
        max_length=20,
        blank=True,
        help_text=_("Para recorrência semanal: 1=Segunda, 2=Terça... (separados por vírgula)")
    )
    
    class Meta:
        verbose_name = _("Recorrência de Evento")
        verbose_name_plural = _("Recorrências de Eventos")
    
    def __str__(self):
        return f"Recorrência {self.get_tipo_recorrencia_display()} - {self.evento.titulo}"
