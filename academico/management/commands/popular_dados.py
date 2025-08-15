"""
Management command para popular o banco com dados de exemplo.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import random

from academico.models import (
    Semestre, Materia, MaterialDidatico, EventoAgenda, Tarefa
)


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de exemplo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Limpa os dados existentes antes de criar novos',
        )

    def handle(self, *args, **options):
        if options['limpar']:
            self.stdout.write('Limpando dados existentes...')
            EventoAgenda.objects.all().delete()
            Tarefa.objects.all().delete() 
            MaterialDidatico.objects.all().delete()
            Materia.objects.all().delete()
            Semestre.objects.all().delete()

        self.stdout.write('Criando dados de exemplo...')

        # Criar semestres
        semestres = self._criar_semestres()
        self.stdout.write(f'✓ {len(semestres)} semestres criados')

        # Criar matérias
        materias = self._criar_materias(semestres)
        self.stdout.write(f'✓ {len(materias)} matérias criadas')

        # Criar eventos
        eventos = self._criar_eventos(semestres, materias)
        self.stdout.write(f'✓ {len(eventos)} eventos criados')

        # Criar tarefas
        tarefas = self._criar_tarefas(materias)
        self.stdout.write(f'✓ {len(tarefas)} tarefas criadas')

        self.stdout.write(
            self.style.SUCCESS('Dados de exemplo criados com sucesso!')
        )

    def _criar_semestres(self):
        semestres_data = [
            {
                'nome': '2025/1',
                'ano': 2025,
                'periodo': '1',
                'data_inicio': datetime(2025, 2, 15).date(),
                'data_fim': datetime(2025, 6, 30).date(),
            },
            {
                'nome': '2025/2',
                'ano': 2025,
                'periodo': '2',
                'data_inicio': datetime(2025, 8, 1).date(),
                'data_fim': datetime(2025, 12, 15).date(),
            }
        ]

        semestres = []
        for data in semestres_data:
            semestre, created = Semestre.objects.get_or_create(
                ano=data['ano'],
                periodo=data['periodo'],
                defaults=data
            )
            semestres.append(semestre)

        return semestres

    def _criar_materias(self, semestres):
        materias_data = [
            # Semestre 2025/1
            {
                'nome': 'Algoritmos e Estruturas de Dados',
                'slug': 'algoritmos-estruturas-dados',
                'descricao': 'Estudo de algoritmos fundamentais e estruturas de dados básicas.',
                'semestre': semestres[0]
            },
            {
                'nome': 'Programação Orientada a Objetos',
                'slug': 'programacao-orientada-objetos',
                'descricao': 'Conceitos e práticas de programação orientada a objetos.',
                'semestre': semestres[0]
            },
            {
                'nome': 'Banco de Dados I',
                'slug': 'banco-dados-1',
                'descricao': 'Fundamentos de sistemas de gerenciamento de banco de dados.',
                'semestre': semestres[0]
            },
            
            # Semestre 2025/2
            {
                'nome': 'Desenvolvimento Web',
                'slug': 'desenvolvimento-web',
                'descricao': 'Criação de aplicações web modernas com HTML, CSS, JavaScript e frameworks.',
                'semestre': semestres[1]
            },
            {
                'nome': 'Engenharia de Software',
                'slug': 'engenharia-software',
                'descricao': 'Métodos e técnicas para desenvolvimento de software de qualidade.',
                'semestre': semestres[1]
            },
            {
                'nome': 'Redes de Computadores',
                'slug': 'redes-computadores',
                'descricao': 'Fundamentos de redes de computadores e protocolos de comunicação.',
                'semestre': semestres[1]
            }
        ]

        materias = []
        for data in materias_data:
            materia, created = Materia.objects.get_or_create(
                slug=data['slug'],
                defaults=data
            )
            # Simular alguns acessos
            materia.contador_acessos = random.randint(5, 50)
            materia.save()
            materias.append(materia)

        return materias

    def _criar_eventos(self, semestres, materias):
        eventos = []
        agora = timezone.now()

        # Eventos gerais
        eventos_gerais = [
            {
                'titulo': 'Início do Semestre 2025/2',
                'descricao': 'Início das aulas do segundo semestre de 2025',
                'escopo': 'GERAL',
                'tipo': 'OUTRO',
                'data_inicio': agora + timedelta(days=2),
            },
            {
                'titulo': 'Semana de Provas - Primeira Etapa',
                'descricao': 'Primeira etapa de avaliações do semestre',
                'escopo': 'GERAL',
                'tipo': 'PROVA',
                'data_inicio': agora + timedelta(days=45),
            }
        ]

        for data in eventos_gerais:
            evento = EventoAgenda.objects.create(**data)
            eventos.append(evento)

        # Eventos por semestre
        for semestre in semestres:
            eventos_semestre = [
                {
                    'titulo': f'Reunião de Planejamento - {semestre.nome}',
                    'descricao': 'Planejamento das atividades do semestre',
                    'escopo': 'SEMESTRE',
                    'tipo': 'OUTRO',
                    'semestre': semestre,
                    'data_inicio': agora + timedelta(days=random.randint(7, 30)),
                }
            ]
            
            for data in eventos_semestre:
                evento = EventoAgenda.objects.create(**data)
                eventos.append(evento)

        # Eventos por matéria
        for materia in materias:
            num_eventos = random.randint(2, 5)
            for i in range(num_eventos):
                tipos = ['AULA', 'PROVA', 'TRABALHO', 'ATIVIDADE']
                evento = EventoAgenda.objects.create(
                    titulo=f'{random.choice(tipos).title()} - {materia.nome}',
                    descricao=f'Atividade da matéria {materia.nome}',
                    escopo='MATERIA',
                    tipo=random.choice(tipos),
                    materia=materia,
                    data_inicio=agora + timedelta(days=random.randint(1, 60))
                )
                eventos.append(evento)

        return eventos

    def _criar_tarefas(self, materias):
        tarefas = []
        agora = timezone.now()

        status_opcoes = ['PENDENTE', 'EM_ANDAMENTO', 'CONCLUIDA']
        tipos_tarefa = [
            ('Exercício', 'Resolver lista de exercícios'),
            ('Projeto', 'Desenvolver projeto prático'),
            ('Pesquisa', 'Pesquisar sobre o tema e elaborar relatório'),
            ('Leitura', 'Ler material complementar'),
            ('Apresentação', 'Preparar apresentação sobre o tema')
        ]

        for materia in materias:
            num_tarefas = random.randint(3, 8)
            for i in range(num_tarefas):
                titulo_base, descricao_base = random.choice(tipos_tarefa)
                
                tarefa = Tarefa.objects.create(
                    materia=materia,
                    titulo=f'{titulo_base} - {materia.nome.split()[0]}',
                    descricao=f'{descricao_base} relacionado à matéria {materia.nome}.',
                    status=random.choice(status_opcoes),
                    prazo=agora + timedelta(days=random.randint(1, 30)) if random.choice([True, False]) else None
                )
                tarefas.append(tarefa)

        return tarefas
