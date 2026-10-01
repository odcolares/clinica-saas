"""Seed idempotente dos prompts iniciais de IA (por schema de tenant).

DATABASE.md: seeds idempotentes e limitadas a dados iniciais necessários.
Os três prompts cobrem os casos de uso da ETAPA 4: classificação de intenção,
extração de dados do cliente e resumo de conversa.
"""

from __future__ import annotations

from django.db import migrations

PROMPTS = (
    {
        "name": "intent_classifier",
        "model_hint": "gpt-4o-mini",
        "content": (
            "Você classifica a intenção de mensagens de clientes de uma clínica.\n"
            "Categorias permitidas: {categories}.\n"
            "Mensagem do cliente:\n---\n{message}\n---\n"
            "Responda apenas com o código da categoria, sem explicações."
        ),
        "parameters": {
            "categories": "agendamento, cancelamento, duvida, orcamento, outro"
        },
    },
    {
        "name": "data_extractor",
        "model_hint": "gpt-4o-mini",
        "content": (
            "Extraia os dados do cliente da mensagem abaixo.\n"
            "Responda SOMENTE com JSON válido contendo as chaves: "
            "nome, telefone, servico, data_preferida "
            "(use null quando a informação não existir).\n"
            "Mensagem:\n---\n{message}\n---"
        ),
        "parameters": {},
    },
    {
        "name": "summarizer",
        "model_hint": "gpt-4o",
        "content": (
            "Resuma a conversa abaixo em no máximo {max_sentences} frases, "
            "em português, destacando o que o cliente quer e o próximo passo.\n"
            "Conversa:\n---\n{conversation}\n---"
        ),
        "parameters": {"max_sentences": 3},
    },
)


def seed_prompts(apps, schema_editor):
    PromptTemplate = apps.get_model("ai", "PromptTemplate")
    for spec in PROMPTS:
        PromptTemplate.objects.update_or_create(
            name=spec["name"],
            defaults={
                "content": spec["content"],
                "model_hint": spec["model_hint"],
                "parameters": spec["parameters"],
                "version": 1,
                "is_active": True,
            },
        )


def unseed_prompts(apps, schema_editor):
    PromptTemplate = apps.get_model("ai", "PromptTemplate")
    PromptTemplate.objects.filter(name__in=[spec["name"] for spec in PROMPTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("ai", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_prompts, unseed_prompts),
    ]
