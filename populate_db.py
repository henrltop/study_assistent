#!/usr/bin/env python
"""
Script para popular o banco de dados com dados de exemplo.
Execute com: python populate_db.py
"""

import os
import django
from django.utils import timezone
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assistente_estudo.settings')
django.setup()

from academico.models import Semestre, Materia, MaterialDidatico, EventoAgenda, Tarefa

def criar_dados_exemplo():
    """Criar dados de exemplo para testar o sistema."""
    
    print("🚀 Criando dados de exemplo...")
    
    # 1. Criar semestres
    semestre1, created = Semestre.objects.get_or_create(
        ano=2025,
        periodo='1',
        defaults={
            'nome': 'Semestre 2025.1',
            'data_inicio': datetime(2025, 2, 15).date(),
            'data_fim': datetime(2025, 7, 15).date(),
            'ativo': True
        }
    )
    
    semestre2, created = Semestre.objects.get_or_create(
        ano=2024,
        periodo='2',
        defaults={
            'nome': 'Semestre 2024.2',
            'data_inicio': datetime(2024, 8, 1).date(),
            'data_fim': datetime(2024, 12, 15).date(),
            'ativo': True
        }
    )
    
    print(f"✅ Semestres criados: {semestre1.nome}, {semestre2.nome}")
    
    # 2. Criar matérias
    materias_data = [
        {
            'nome': 'Algoritmos e Estruturas de Dados',
            'descricao': 'Estudo de algoritmos fundamentais e estruturas de dados.',
            'semestre': semestre1
        },
        {
            'nome': 'Engenharia de Software',
            'descricao': 'Metodologias e práticas para desenvolvimento de software.',
            'semestre': semestre1
        },
        {
            'nome': 'Banco de Dados',
            'descricao': 'Modelagem, projeto e implementação de bancos de dados.',
            'semestre': semestre1
        },
        {
            'nome': 'Inteligência Artificial',
            'descricao': 'Fundamentos e aplicações de IA.',
            'semestre': semestre2
        },
        {
            'nome': 'Redes de Computadores',
            'descricao': 'Protocolos e arquiteturas de redes.',
            'semestre': semestre2
        }
    ]
    
    materias = []
    for data in materias_data:
        materia, created = Materia.objects.get_or_create(
            nome=data['nome'],
            semestre=data['semestre'],
            defaults={
                'descricao': data['descricao'],
                'slug': data['nome'].lower().replace(' ', '-').replace('ç', 'c').replace('ã', 'a'),
            }
        )
        materias.append(materia)
    
    print(f"✅ Matérias criadas: {len(materias)} matérias")
    
    # 3. Criar eventos
    eventos_data = [
        {
            'titulo': 'Prova de Algoritmos - P1',
            'descricao': 'Primeira prova de Algoritmos e Estruturas de Dados',
            'tipo': 'PROVA',
            'escopo': 'MATERIA',
            'materia': materias[0],
            'data_inicio': timezone.make_aware(datetime(2025, 3, 15, 14, 0)),
            'data_fim': timezone.make_aware(datetime(2025, 3, 15, 16, 0)),
        },
        {
            'titulo': 'Trabalho de Engenharia de Software',
            'descricao': 'Entrega do projeto de análise e design',
            'tipo': 'TRABALHO',
            'escopo': 'MATERIA',
            'materia': materias[1],
            'data_inicio': timezone.make_aware(datetime(2025, 4, 20, 23, 59)),
        },
        {
            'titulo': 'Aula sobre Normalização BD',
            'descricao': 'Aula sobre formas normais e normalização',
            'tipo': 'AULA',
            'escopo': 'MATERIA',
            'materia': materias[2],
            'data_inicio': timezone.make_aware(datetime(2025, 3, 10, 10, 0)),
            'data_fim': timezone.make_aware(datetime(2025, 3, 10, 12, 0)),
        },
        {
            'titulo': 'Seminário de IA',
            'descricao': 'Seminário sobre Machine Learning',
            'tipo': 'ATIVIDADE',
            'escopo': 'MATERIA',
            'materia': materias[3],
            'data_inicio': timezone.make_aware(datetime(2025, 5, 5, 16, 0)),
        },
        {
            'titulo': 'Reunião Geral do Curso',
            'descricao': 'Reunião com coordenação do curso',
            'tipo': 'OUTRO',
            'escopo': 'GERAL',
            'data_inicio': timezone.make_aware(datetime(2025, 3, 1, 19, 0)),
        }
    ]
    
    eventos = []
    for data in eventos_data:
        evento, created = EventoAgenda.objects.get_or_create(
            titulo=data['titulo'],
            defaults=data
        )
        eventos.append(evento)
    
    print(f"✅ Eventos criados: {len(eventos)} eventos")
    
    # 4. Criar tarefas
    tarefas_data = [
        {
            'titulo': 'Implementar algoritmo de ordenação',
            'descricao': 'Implementar QuickSort e MergeSort em Python',
            'materia': materias[0],
            'status': 'PENDENTE',
            'prazo': timezone.make_aware(datetime(2025, 3, 12, 23, 59)),
        },
        {
            'titulo': 'Estudar para prova de Algoritmos',
            'descricao': 'Revisar complexidade de algoritmos e árvores',
            'materia': materias[0],
            'status': 'EM_ANDAMENTO',
            'prazo': timezone.make_aware(datetime(2025, 3, 14, 23, 59)),
        },
        {
            'titulo': 'Diagrama de Casos de Uso',
            'descricao': 'Criar diagramas UML para o projeto',
            'materia': materias[1],
            'status': 'PENDENTE',
            'prazo': timezone.make_aware(datetime(2025, 4, 15, 23, 59)),
        },
        {
            'titulo': 'Modelar banco de dados',
            'descricao': 'Criar modelo ER para sistema de biblioteca',
            'materia': materias[2],
            'status': 'CONCLUIDA',
            'prazo': timezone.make_aware(datetime(2025, 2, 28, 23, 59)),
        },
        {
            'titulo': 'Pesquisar sobre Redes Neurais',
            'descricao': 'Estudar fundamentos de deep learning',
            'materia': materias[3],
            'status': 'PENDENTE',
            'prazo': timezone.make_aware(datetime(2025, 4, 30, 23, 59)),
        },
        {
            'titulo': 'Configurar laboratório de redes',
            'descricao': 'Instalar e configurar simulador de redes',
            'materia': materias[4],
            'status': 'EM_ANDAMENTO',
        }
    ]
    
    tarefas = []
    for data in tarefas_data:
        tarefa, created = Tarefa.objects.get_or_create(
            titulo=data['titulo'],
            materia=data['materia'],
            defaults=data
        )
        tarefas.append(tarefa)
    
    print(f"✅ Tarefas criadas: {len(tarefas)} tarefas")
    
    # Incrementar contadores de acesso das matérias
    for materia in materias:
        import random
        materia.contador_acessos = random.randint(5, 50)
        materia.save()
    
    print("\n🎉 Dados de exemplo criados com sucesso!")
    print(f"📊 Resumo:")
    print(f"   • {Semestre.objects.count()} semestres")
    print(f"   • {Materia.objects.count()} matérias")
    print(f"   • {EventoAgenda.objects.count()} eventos")
    print(f"   • {Tarefa.objects.count()} tarefas")
    print(f"\n🌐 Acesse: http://127.0.0.1:8000")

if __name__ == '__main__':
    criar_dados_exemplo()
