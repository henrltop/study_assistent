from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
import os

User = get_user_model()

class Semestre(models.Model):
    """Modelo para representar semestres acadêmicos."""
    
    PERIODO_CHOICES = [
        ('1', '1º Semestre'),
        ('2', '2º Semestre'),
        ('VERAO', 'Verão'),
        ('INVERNO', 'Inverno'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='semestres', verbose_name='Usuário')
    nome = models.CharField('Nome', max_length=100)
    ano = models.IntegerField('Ano')
    periodo = models.CharField('Período', max_length=10, choices=PERIODO_CHOICES)
    data_inicio = models.DateField('Data de Início')
    data_fim = models.DateField('Data de Término')
    ativo = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Semestre'
        verbose_name_plural = 'Semestres'
        ordering = ['-ano', '-periodo']
        unique_together = ['usuario', 'ano', 'periodo']
    
    def __str__(self):
        return f"{self.nome} - {self.ano}/{self.get_periodo_display()}"
    
    def get_absolute_url(self):
        return reverse('semestre_detail', kwargs={'pk': self.pk})


class Materia(models.Model):
    """Modelo para representar matérias/disciplinas."""
    
    semestre = models.ForeignKey(Semestre, on_delete=models.CASCADE, related_name='materias', verbose_name='Semestre')
    nome = models.CharField('Nome', max_length=200)
    descricao = models.TextField('Descrição', blank=True)
    slug = models.SlugField('Slug', unique=True, max_length=200)
    contador_acessos = models.PositiveIntegerField('Contador de Acessos', default=0)
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Matéria'
        verbose_name_plural = 'Matérias'
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} ({self.semestre})"
    
    def get_absolute_url(self):
        return reverse('materia_detail', kwargs={'slug': self.slug})
    
    def incrementar_acesso(self):
        """Incrementa o contador de acessos da matéria."""
        self.contador_acessos += 1
        self.save(update_fields=['contador_acessos'])
    
    def get_dias_aula(self):
        """Retorna os dias da semana que tem aula desta matéria."""
        return self.horarios_aula.filter(ativo=True).values_list('dia_semana', flat=True).distinct().order_by('dia_semana')
    
    def get_proximas_aulas(self, limite=5):
        """Retorna as próximas datas de aula desta matéria."""
        from datetime import date, timedelta
        
        dias_aula = list(self.get_dias_aula())
        if not dias_aula:
            return []
        
        proximas_datas = []
        data_atual = date.today()
        
        # Procurar as próximas datas por até 60 dias
        for i in range(60):
            data_teste = data_atual + timedelta(days=i)
            if data_teste.weekday() in dias_aula:
                proximas_datas.append(data_teste)
                if len(proximas_datas) >= limite:
                    break
        
        return proximas_datas


class MaterialDidatico(models.Model):
    """Modelo para armazenar materiais didáticos da matéria."""
    
    TIPO_CHOICES = [
        ('PDF', 'PDF'),
        ('TXT', 'Texto'),
        ('DOCX', 'Word'),
    ]
    
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='materiais', verbose_name='Matéria')
    titulo = models.CharField('Título', max_length=200)
    arquivo = models.FileField('Arquivo', upload_to='materiais/%Y/%m/')
    tipo = models.CharField('Tipo', max_length=10, choices=TIPO_CHOICES)
    data_upload = models.DateTimeField('Data do Upload', auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Usuário')
    
    class Meta:
        verbose_name = 'Material Didático'
        verbose_name_plural = 'Materiais Didáticos'
        ordering = ['-data_upload']
    
    def __str__(self):
        return f"{self.titulo} ({self.materia})"
    
    def get_tamanho_arquivo(self):
        """Retorna o tamanho do arquivo em formato legível."""
        if self.arquivo:
            size = self.arquivo.size
            if size < 1024:
                return f"{size} bytes"
            elif size < 1024*1024:
                return f"{size/1024:.1f} KB"
            else:
                return f"{size/(1024*1024):.1f} MB"
        return "0 bytes"
    
    def get_extensao(self):
        """Retorna a extensão do arquivo."""
        if self.arquivo:
            return os.path.splitext(self.arquivo.name)[1].lower()
        return ''


class EventoAgenda(models.Model):
    """Modelo para eventos da agenda (geral, por semestre ou por matéria)."""
    
    ESCOPO_CHOICES = [
        ('GERAL', 'Geral'),
        ('SEMESTRE', 'Semestre'),
        ('MATERIA', 'Matéria'),
    ]
    
    TIPO_CHOICES = [
        ('AULA', 'Aula'),
        ('PROVA', 'Prova'),
        ('TRABALHO', 'Trabalho'),
        ('ATIVIDADE', 'Atividade'),
        ('OUTRO', 'Outro'),
    ]
    
    titulo = models.CharField('Título', max_length=200)
    descricao = models.TextField('Descrição', blank=True)
    escopo = models.CharField('Escopo', max_length=10, choices=ESCOPO_CHOICES)
    data_inicio = models.DateTimeField('Data e Hora de Início')
    data_fim = models.DateTimeField('Data e Hora de Término', null=True, blank=True)
    tipo = models.CharField('Tipo', max_length=10, choices=TIPO_CHOICES, default='OUTRO')
    
    # Relacionamentos opcionais baseados no escopo
    semestre = models.ForeignKey(Semestre, on_delete=models.CASCADE, null=True, blank=True, 
                               related_name='eventos', verbose_name='Semestre')
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, null=True, blank=True,
                              related_name='eventos', verbose_name='Matéria')
    
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuário')
    
    class Meta:
        verbose_name = 'Evento da Agenda'
        verbose_name_plural = 'Eventos da Agenda'
        ordering = ['data_inicio']
    
    def __str__(self):
        return f"{self.titulo} - {self.data_inicio.strftime('%d/%m/%Y %H:%M')}"
    
    def clean(self):
        """Validações customizadas do modelo."""
        from django.core.exceptions import ValidationError
        
        if self.escopo == 'SEMESTRE' and not self.semestre:
            raise ValidationError('Eventos de semestre devem ter um semestre associado.')
        
        if self.escopo == 'MATERIA' and not self.materia:
            raise ValidationError('Eventos de matéria devem ter uma matéria associada.')
        
        if self.data_fim and self.data_fim <= self.data_inicio:
            raise ValidationError('A data de término deve ser posterior à data de início.')
    
    @property
    def eh_hoje(self):
        """Verifica se o evento é hoje."""
        hoje = timezone.now().date()
        return self.data_inicio.date() == hoje
    
    @property
    def eh_futuro(self):
        """Verifica se o evento é futuro."""
        return self.data_inicio > timezone.now()


class Tarefa(models.Model):
    """Modelo para tarefas/to-do das matérias."""
    
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('CONCLUIDA', 'Concluída'),
    ]
    
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='tarefas', verbose_name='Matéria')
    titulo = models.CharField('Título', max_length=200)
    descricao = models.TextField('Descrição', blank=True)
    status = models.CharField('Status', max_length=15, choices=STATUS_CHOICES, default='PENDENTE')
    prazo = models.DateTimeField('Prazo', null=True, blank=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuário')
    
    class Meta:
        verbose_name = 'Tarefa'
        verbose_name_plural = 'Tarefas'
        ordering = ['prazo', '-criado_em']
    
    def __str__(self):
        return f"{self.titulo} ({self.materia}) - {self.get_status_display()}"
    
    @property
    def esta_atrasada(self):
        """Verifica se a tarefa está atrasada."""
        if self.prazo and self.status != 'CONCLUIDA':
            return self.prazo < timezone.now()
        return False
    
    @property
    def dias_para_prazo(self):
        """Calcula quantos dias faltam para o prazo."""
        if self.prazo:
            delta = self.prazo.date() - timezone.now().date()
            return delta.days
        return None


class AcessoMateria(models.Model):
    """Modelo para registrar acessos às matérias (para ranking)."""
    
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='acessos', verbose_name='Matéria')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuário')
    data_hora = models.DateTimeField('Data e Hora', auto_now_add=True)
    ip_address = models.GenericIPAddressField('Endereço IP', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Acesso à Matéria'
        verbose_name_plural = 'Acessos às Matérias'
        ordering = ['-data_hora']
    
    def __str__(self):
        return f"{self.materia} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"


class HorarioAula(models.Model):
    """Modelo para representar horários fixos de aula das matérias"""
    
    DIAS_SEMANA = [
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    
    materia = models.ForeignKey(
        Materia,
        on_delete=models.CASCADE,
        related_name='horarios_aula',
        verbose_name='Matéria'
    )
    dia_semana = models.IntegerField(
        'Dia da Semana',
        choices=DIAS_SEMANA
    )
    hora_inicio = models.TimeField('Horário de Início')
    hora_fim = models.TimeField('Horário de Término')
    local = models.CharField(
        'Local/Sala',
        max_length=100,
        blank=True,
        help_text='Sala, laboratório ou local da aula'
    )
    observacoes = models.TextField(
        'Observações',
        blank=True,
        help_text='Informações adicionais sobre a aula'
    )
    ativo = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Horário de Aula'
        verbose_name_plural = 'Horários de Aula'
        ordering = ['materia', 'dia_semana', 'hora_inicio']
        unique_together = ['materia', 'dia_semana', 'hora_inicio']
    
    def __str__(self):
        return f"{self.materia.nome} - {self.get_dia_semana_display()} {self.hora_inicio.strftime('%H:%M')}"
    
    def get_duracao(self):
        """Calcula a duração da aula"""
        from datetime import datetime, timedelta
        inicio = datetime.combine(datetime.today(), self.hora_inicio)
        fim = datetime.combine(datetime.today(), self.hora_fim)
        duracao = fim - inicio
        
        horas = int(duracao.total_seconds() // 3600)
        minutos = int((duracao.total_seconds() % 3600) // 60)
        
        if horas > 0 and minutos > 0:
            return f"{horas}h{minutos}min"
        elif horas > 0:
            return f"{horas}h"
        else:
            return f"{minutos}min"
    
    def get_cor_calendar(self):
        """Retorna uma cor para o calendário baseada na matéria"""
        # Usa a cor da matéria se existir, senão uma cor baseada no hash do nome
        import hashlib
        hash_object = hashlib.md5(self.materia.nome.encode())
        hex_dig = hash_object.hexdigest()
        # Converte parte do hash em uma cor
        r = int(hex_dig[0:2], 16)
        g = int(hex_dig[2:4], 16)
        b = int(hex_dig[4:6], 16)
        return f"#{r:02x}{g:02x}{b:02x}"
