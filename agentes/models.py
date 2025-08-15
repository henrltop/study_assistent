"""
Modelos para o app de agentes.

Por enquanto, este app não possui modelos de banco de dados,
pois os agentes são implementados como serviços em memória.

No futuro, poderemos adicionar modelos para:
- Histórico de conversas
- Configurações de agentes
- Cache de respostas
- Métricas de uso
"""

# from django.db import models

# Modelos futuros:
# class HistoricoConversa(models.Model):
#     usuario = models.ForeignKey(User, on_delete=models.CASCADE)
#     tipo_agente = models.CharField(max_length=20)
#     pergunta = models.TextField()
#     resposta = models.TextField()
#     contexto = models.JSONField(null=True, blank=True)
#     timestamp = models.DateTimeField(auto_now_add=True)

# class ConfiguracaoAgente(models.Model):
#     tipo = models.CharField(max_length=20, unique=True)
#     provedor = models.CharField(max_length=20)  # stub, claude, openai
#     configuracao = models.JSONField(default=dict)
#     ativo = models.BooleanField(default=True)
