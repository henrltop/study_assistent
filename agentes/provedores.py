"""
Módulo de agentes para simulação de IA no Assistente de Estudos.

Este módulo contém as classes base e implementações stub para os agentes
que futuramente serão integrados com APIs reais (OpenAI, Claude, etc.).

Arquitetura:
- BaseAgente: Interface base para todos os agentes
- AgenteStub: Implementação mockada para desenvolvimento
- Factory: Para instanciar agentes baseado em configuração
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from django.utils import timezone
from datetime import timedelta
import random


class BaseAgente(ABC):
    """Interface base para todos os agentes de IA."""
    
    @abstractmethod
    def responder(self, pergunta: str, contexto: Dict[str, Any] = None) -> str:
        """
        Responde uma pergunta baseada no contexto fornecido.
        
        Args:
            pergunta: A pergunta do usuário
            contexto: Contexto específico (semestre_id, materia_id, etc.)
            
        Returns:
            Resposta do agente
        """
        pass
    
    @abstractmethod
    def get_tipo(self) -> str:
        """Retorna o tipo do agente."""
        pass


class AgenteStub(BaseAgente):
    """Implementação stub/mockada dos agentes para desenvolvimento."""
    
    def __init__(self, tipo_agente: str):
        self.tipo_agente = tipo_agente
        
        # Respostas pré-definidas por tipo
        self.respostas_padrao = {
            'home': [
                "Olá! Sou seu assistente de estudos. Em breve terei funcionalidades completas de chat!",
                "Bem-vindo ao seu assistente de estudos! Por enquanto, use as funcionalidades da agenda e matérias.",
                "Oi! Estou em desenvolvimento, mas já posso ajudar navegando pelo sistema."
            ],
            'semestre': [
                "Sobre este semestre, posso ajudar com informações das matérias e agenda.",
                "Este semestre tem várias atividades interessantes! Quer saber mais sobre alguma matéria específica?",
                "Posso fornecer informações sobre as matérias e eventos deste semestre."
            ],
            'materia': [
                "Como tutor desta matéria, posso ajudar com os materiais disponíveis e cronograma.",
                "Tenho acesso aos materiais didáticos desta matéria. Em que posso ajudar?",
                "Posso explicar conceitos baseados nos materiais que você enviou."
            ]
        }
    
    def responder(self, pergunta: str, contexto: Dict[str, Any] = None) -> str:
        """Gera uma resposta mockada baseada no tipo e contexto."""
        
        resposta_base = random.choice(self.respostas_padrao.get(self.tipo_agente, [
            "Sou um assistente em desenvolvimento. Em breve terei mais funcionalidades!"
        ]))
        
        # Adicionar informações específicas do contexto
        if contexto:
            resposta_contexto = self._gerar_resposta_contextual(pergunta, contexto)
            if resposta_contexto:
                resposta_base += f"\n\n{resposta_contexto}"
        
        # Adicionar timestamp da simulação
        timestamp = timezone.now().strftime("%d/%m/%Y às %H:%M")
        resposta_base += f"\n\n---\n🤖 *Simulação de IA ({self.tipo_agente}) - {timestamp}*"
        
        return resposta_base
    
    def _gerar_resposta_contextual(self, pergunta: str, contexto: Dict[str, Any]) -> str:
        """Gera resposta específica baseada no contexto."""
        
        if self.tipo_agente == 'semestre' and 'semestre' in contexto:
            return self._resposta_semestre(pergunta, contexto['semestre'])
            
        elif self.tipo_agente == 'materia' and 'materia' in contexto:
            return self._resposta_materia(pergunta, contexto['materia'])
            
        return ""
    
    def _resposta_semestre(self, pergunta: str, semestre) -> str:
        """Gera resposta específica para contexto de semestre."""
        from academico.models import EventoAgenda
        
        respostas = []
        
        # Informações sobre matérias do semestre
        materias = semestre.materias.filter(ativo=True)
        if materias.exists():
            materias_nomes = ", ".join([m.nome for m in materias[:3]])
            respostas.append(f"**Matérias deste semestre:** {materias_nomes}")
            
            if materias.count() > 3:
                respostas.append(f"(e mais {materias.count() - 3} matérias)")
        
        # Próximos eventos do semestre
        proximos_eventos = EventoAgenda.objects.filter(
            semestre=semestre,
            data_inicio__gte=timezone.now()
        ).order_by('data_inicio')[:3]
        
        if proximos_eventos:
            eventos_texto = []
            for evento in proximos_eventos:
                data_str = evento.data_inicio.strftime("%d/%m")
                eventos_texto.append(f"• {evento.titulo} ({data_str})")
            
            respostas.append("**Próximos eventos:**")
            respostas.extend(eventos_texto)
        
        return "\n".join(respostas) if respostas else "Não há informações específicas disponíveis no momento."
    
    def _resposta_materia(self, pergunta: str, materia) -> str:
        """Gera resposta específica para contexto de matéria."""
        from academico.models import EventoAgenda, Tarefa
        
        respostas = []
        
        # Informações sobre materiais
        materiais = materia.materiais.all()[:5]
        if materiais:
            respostas.append("**Materiais disponíveis:**")
            for material in materiais:
                respostas.append(f"• {material.titulo} ({material.tipo})")
        
        # Próximas tarefas
        tarefas_pendentes = materia.tarefas.filter(
            status__in=['PENDENTE', 'EM_ANDAMENTO']
        ).order_by('prazo')[:3]
        
        if tarefas_pendentes:
            respostas.append("\n**Tarefas pendentes:**")
            for tarefa in tarefas_pendentes:
                prazo_str = tarefa.prazo.strftime("%d/%m") if tarefa.prazo else "Sem prazo"
                respostas.append(f"• {tarefa.titulo} ({prazo_str})")
        
        # Próximos eventos da matéria
        proximos_eventos = EventoAgenda.objects.filter(
            materia=materia,
            data_inicio__gte=timezone.now()
        ).order_by('data_inicio')[:2]
        
        if proximos_eventos:
            respostas.append("\n**Próximos eventos:**")
            for evento in proximos_eventos:
                data_str = evento.data_inicio.strftime("%d/%m às %H:%M")
                respostas.append(f"• {evento.titulo} ({data_str})")
        
        if not respostas:
            return "Esta matéria ainda não tem materiais ou atividades cadastradas."
        
        return "\n".join(respostas)
    
    def get_tipo(self) -> str:
        """Retorna o tipo do agente."""
        return self.tipo_agente


class AgenteClaude(BaseAgente):
    """Implementação futura para integração com Claude AI."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        # TODO: Implementar integração real com Claude
    
    def responder(self, pergunta: str, contexto: Dict[str, Any] = None) -> str:
        # TODO: Implementar chamada real para a API do Claude
        return "Integração com Claude AI será implementada em breve."
    
    def get_tipo(self) -> str:
        return "claude"


class AgenteOpenAI(BaseAgente):
    """Implementação futura para integração com OpenAI."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        # TODO: Implementar integração real com OpenAI
    
    def responder(self, pergunta: str, contexto: Dict[str, Any] = None) -> str:
        # TODO: Implementar chamada real para a API da OpenAI
        return "Integração com OpenAI será implementada em breve."
    
    def get_tipo(self) -> str:
        return "openai"


class AgenteFactory:
    """Factory para criar instâncias de agentes."""
    
    @staticmethod
    def criar_agente_home() -> BaseAgente:
        """Cria agente para a home."""
        return AgenteStub('home')
    
    @staticmethod
    def criar_agente_semestre() -> BaseAgente:
        """Cria agente para contexto de semestre."""
        return AgenteStub('semestre')
    
    @staticmethod
    def criar_agente_materia() -> BaseAgente:
        """Cria agente tutor para contexto de matéria."""
        return AgenteStub('materia')
    
    @staticmethod
    def criar_agente_personalizado(tipo: str, configuracao: Dict[str, Any] = None) -> BaseAgente:
        """
        Cria agente personalizado baseado na configuração.
        
        No futuro, esta função verificará as configurações do .env
        para decidir qual implementação usar (stub, claude, openai).
        """
        # TODO: Implementar lógica para escolher entre diferentes provedores
        # baseado na configuração do ambiente
        
        if tipo in ['home', 'semestre', 'materia']:
            return AgenteStub(tipo)
        
        return AgenteStub('generico')
