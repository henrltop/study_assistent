"""
Serviços para gerenciar agentes no sistema.

Este módulo fornece uma interface de alto nível para interagir com os agentes,
abstraindo a complexidade da escolha e configuração dos diferentes tipos.
"""

from typing import Dict, Any, Optional
from .provedores import AgenteFactory, BaseAgente


class ServicoAgente:
    """Serviço principal para interação com agentes."""
    
    def __init__(self):
        self._agentes_cache = {}
    
    def responder_home(self, pergunta: str) -> str:
        """
        Resposta do agente da home (chat geral - ainda não conversacional).
        
        Args:
            pergunta: Pergunta do usuário
            
        Returns:
            Resposta do agente
        """
        agente = self._get_agente('home')
        return agente.responder(pergunta)
    
    def responder_semestre(self, pergunta: str, semestre_id: int) -> str:
        """
        Resposta do agente de semestre.
        
        Args:
            pergunta: Pergunta do usuário
            semestre_id: ID do semestre para contexto
            
        Returns:
            Resposta contextualizada do agente
        """
        from academico.models import Semestre
        
        try:
            semestre = Semestre.objects.get(id=semestre_id)
            agente = self._get_agente('semestre')
            
            contexto = {
                'semestre': semestre,
                'semestre_id': semestre_id
            }
            
            return agente.responder(pergunta, contexto)
            
        except Semestre.DoesNotExist:
            return "Erro: Semestre não encontrado."
    
    def responder_materia(self, pergunta: str, materia_slug: str) -> str:
        """
        Resposta do agente tutor de matéria.
        
        Args:
            pergunta: Pergunta do usuário
            materia_slug: Slug da matéria para contexto
            
        Returns:
            Resposta contextualizada do tutor
        """
        from academico.models import Materia
        
        try:
            materia = Materia.objects.get(slug=materia_slug)
            agente = self._get_agente('materia')
            
            contexto = {
                'materia': materia,
                'materia_slug': materia_slug
            }
            
            return agente.responder(pergunta, contexto)
            
        except Materia.DoesNotExist:
            return "Erro: Matéria não encontrada."
    
    def _get_agente(self, tipo: str) -> BaseAgente:
        """
        Obtém uma instância de agente, usando cache quando possível.
        
        Args:
            tipo: Tipo do agente (home, semestre, materia)
            
        Returns:
            Instância do agente
        """
        if tipo not in self._agentes_cache:
            self._agentes_cache[tipo] = self._criar_agente(tipo)
        
        return self._agentes_cache[tipo]
    
    def _criar_agente(self, tipo: str) -> BaseAgente:
        """
        Cria uma nova instância de agente.
        
        Args:
            tipo: Tipo do agente
            
        Returns:
            Nova instância do agente
        """
        if tipo == 'home':
            return AgenteFactory.criar_agente_home()
        elif tipo == 'semestre':
            return AgenteFactory.criar_agente_semestre()
        elif tipo == 'materia':
            return AgenteFactory.criar_agente_materia()
        else:
            return AgenteFactory.criar_agente_personalizado(tipo)
    
    def limpar_cache(self):
        """Limpa o cache de agentes (útil para testes)."""
        self._agentes_cache.clear()


# Instância global do serviço (singleton)
servico_agente = ServicoAgente()
