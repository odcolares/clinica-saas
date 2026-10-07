"""Testes de features dos serviços AI (Etapa 4).

Cobrem ``intent``, ``extraction``, ``rag``, ``summarizer`` e ``auto_reply``
com o cliente OpenAI mockado (``AsyncMock``) — sem chave real e sem rede.
Verificam também a auditoria em ``LLMInteraction`` (toda chamada gera
linha) e o isolamento por tenant.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from django.db import connection

from apps.ai import auto_reply, extraction, intent, rag, summarizer
from apps.ai.intent import IntentOutput
from apps.ai.models import LLMInteraction
from apps.omnichannel.models import Conversation, ConversationMessage

pytestmark = pytest.mark.django_db

PASSWORD = "SenhaForte123"


# --- Helpers de mock -------------------------------------------------------


def _usage(prompt: int = 10, completion: int = 5) -> MagicMock:
    usage = MagicMock()
    usage.prompt_tokens = prompt
    usage.completion_tokens = completion
    return usage


def _parse_client(intent_value: str, confidence: float) -> MagicMock:
    """Cliente cujo ``chat.completions.parse`` devolve Structured Output."""
    parsed = IntentOutput(intent=intent_value, confidence=confidence)
    message = MagicMock()
    message.parsed = parsed
    response = MagicMock()
    response.choices = [MagicMock(message=message)]
    response.usage = _usage()

    client = MagicMock()
    client.chat.completions.parse = AsyncMock(return_value=response)
    return client


def _chat_client(content: str, tool_arguments: str | None = None) -> MagicMock:
    """Cliente cujo ``chat.completions.create`` devolve texto ou tool_call."""
    message = MagicMock()
    message.content = content
    if tool_arguments is None:
        message.tool_calls = []
    else:
        function = MagicMock()
        function.arguments = tool_arguments
        message.tool_calls = [MagicMock(function=function)]

    response = MagicMock()
    response.choices = [MagicMock(message=message)]
    response.usage = _usage()

    client = MagicMock()
    client.chat.completions.create = AsyncMock(return_value=response)
    return client


@pytest.fixture
def patch_client(monkeypatch):
    """Permite trocar o cliente devolvido por ``apps.ai.client.get_client``."""

    def _install(client: Any) -> Any:
        monkeypatch.setattr("apps.ai.client.get_client", lambda: client)
        return client

    return _install


def _conversation(**kwargs) -> Conversation:
    defaults: dict[str, Any] = {
        "channel": Conversation.Channel.TELEGRAM,
        "external_chat_id": "999",
    }
    defaults.update(kwargs)
    return Conversation.objects.create(**defaults)


# --- intent ----------------------------------------------------------------


def test_classify_intent_devolve_intencao_e_confianca(tenant, patch_client):
    connection.set_tenant(tenant)
    patch_client(_parse_client("booking", 0.92))
    result = intent.classify_intent("quero agendar uma consulta")
    assert result == {"intent": "booking", "confidence": 0.92}


def test_classify_intent_normaliza_intencao_invalida(tenant, patch_client):
    connection.set_tenant(tenant)
    patch_client(_parse_client("handoff", 0.0))
    result = intent.classify_intent("mensagem ambígua")
    assert result["intent"] in intent.INTENT_NAMES
    assert 0.0 <= result["confidence"] <= 1.0


def test_classify_intent_grava_auditoria(tenant, patch_client):
    connection.set_tenant(tenant)
    patch_client(_parse_client("query", 0.8))
    intent.classify_intent("qual o horário?")
    row = LLMInteraction.objects.get()
    assert row.model == "gpt-4o-mini"
    assert row.prompt_tokens == 10
    assert row.completion_tokens == 5
    assert row.total_tokens == 15
    assert row.tenant_id == tenant.pk


def test_classify_intent_indisponivel_escala_para_humano(tenant):
    connection.set_tenant(tenant)

    def _boom():
        raise RuntimeError("OPENAI_API_KEY não configurada")

    import apps.ai.client as client_module

    original = client_module.get_client
    client_module.get_client = _boom
    try:
        result = intent.classify_intent("oi")
    finally:
        client_module.get_client = original
    assert result == {"intent": "handoff", "confidence": 0.0}


# --- extraction ------------------------------------------------------------


def test_extract_client_data_devolve_campos(tenant, patch_client):
    connection.set_tenant(tenant)
    patch_client(
        _chat_client(
            "",
            tool_arguments=(
                '{"nome":"João","telefone":"11999998888","servico":"limpeza"}'
            ),
        )
    )
    result = extraction.extract_client_data("meu nome é João")
    assert result == {
        "nome": "João",
        "telefone": "11999998888",
        "servico": "limpeza",
    }


def test_extract_client_data_sem_dados_devolve_none(tenant, patch_client):
    connection.set_tenant(tenant)
    patch_client(_chat_client("", tool_arguments=None))
    result = extraction.extract_client_data("oi")
    assert result == {"nome": None, "telefone": None, "servico": None}


def test_extract_client_data_grava_auditoria(tenant, patch_client):
    connection.set_tenant(tenant)
    patch_client(_chat_client("", tool_arguments='{"nome":"Ana"}'))
    extraction.extract_client_data("sou a Ana")
    assert LLMInteraction.objects.count() == 1


# --- rag -------------------------------------------------------------------


def test_rag_sem_mensagens_retorna_vazio(tenant):
    connection.set_tenant(tenant)
    assert rag.search_faq("horário de funcionamento") == []


def test_rag_encontra_resposta_do_atendente(tenant):
    connection.set_tenant(tenant)
    ConversationMessage.objects.create(
        conversation=_conversation(external_chat_id="111"),
        direction=ConversationMessage.Direction.OUTBOUND,
        sender_kind=ConversationMessage.SenderKind.AGENT,
        body="Horário de atendimento: seg a sex, 08h às 18h.",
        normalized_body="horário de atendimento: seg a sex, 08h às 18h.",
    )
    results = rag.search_faq("horário")
    assert len(results) == 1
    assert results[0]["snippet"] == "Horário de atendimento: seg a sex, 08h às 18h."


def test_rag_ignora_mensagem_do_cliente(tenant):
    connection.set_tenant(tenant)
    ConversationMessage.objects.create(
        conversation=_conversation(external_chat_id="222"),
        direction=ConversationMessage.Direction.INBOUND,
        sender_kind=ConversationMessage.SenderKind.CUSTOMER,
        body="Qual o horário?",
        normalized_body="qual o horário?",
    )
    assert rag.search_faq("horário") == []


def test_rag_isola_entre_tenants(tenant, tenant_factory):
    connection.set_tenant(tenant)
    ConversationMessage.objects.create(
        conversation=_conversation(external_chat_id="333"),
        direction=ConversationMessage.Direction.OUTBOUND,
        sender_kind=ConversationMessage.SenderKind.AGENT,
        body="Resposta do tenant A",
        normalized_body="resposta do tenant a",
    )
    assert len(rag.search_faq("resposta")) == 1

    outro = tenant_factory("ai_feat_iso")
    connection.set_tenant(outro)
    assert rag.search_faq("resposta") == []


def test_embedding_stub_e_deterministico():
    assert rag.embedding_stub("horário") == rag.embedding_stub("horário")
    assert len(rag.embedding_stub("horário")) == rag.EMBEDDING_DIM
    assert rag.embedding_stub("a") != rag.embedding_stub("b")


# --- summarizer ------------------------------------------------------------


def test_summarize_conversa_vazia_retorna_vazio(tenant):
    connection.set_tenant(tenant)
    assert summarizer.summarize_conversation([]) == ""


def test_summarize_conversa_em_ptbr(tenant, patch_client):
    connection.set_tenant(tenant)
    patch_client(
        _chat_client("Cliente quer agendar limpeza. Próximo passo: confirmar horário.")
    )
    messages = [
        ConversationMessage(
            direction=ConversationMessage.Direction.INBOUND,
            sender_kind=ConversationMessage.SenderKind.CUSTOMER,
            body="Quero agendar",
        ),
        ConversationMessage(
            direction=ConversationMessage.Direction.OUTBOUND,
            sender_kind=ConversationMessage.SenderKind.AGENT,
            body="Qual horário?",
        ),
    ]
    result = summarizer.summarize_conversation(messages)
    assert "Cliente quer agendar" in result


def test_summarize_formata_historico_com_autores():
    messages = [
        ConversationMessage(
            direction=ConversationMessage.Direction.INBOUND,
            sender_kind=ConversationMessage.SenderKind.CUSTOMER,
            body="Quero agendar",
        ),
        ConversationMessage(
            direction=ConversationMessage.Direction.OUTBOUND,
            sender_kind=ConversationMessage.SenderKind.AGENT,
            body="Qual horário?",
        ),
    ]
    formatted = summarizer.format_conversation(messages)
    assert "Cliente: Quero agendar" in formatted
    assert "Atendente: Qual horário?" in formatted


# --- auto_reply ------------------------------------------------------------


def test_auto_reply_usa_faq_quando_existe(tenant, patch_client):
    connection.set_tenant(tenant)
    ConversationMessage.objects.create(
        conversation=_conversation(external_chat_id="444"),
        direction=ConversationMessage.Direction.OUTBOUND,
        sender_kind=ConversationMessage.SenderKind.AGENT,
        body="Horário de atendimento: segunda a sexta, 8h às 18h.",
        normalized_body="horário de atendimento: segunda a sexta, 8h às 18h.",
    )
    patch_client(_chat_client("Atendemos de segunda a sexta, das 8h às 18h."))
    result = auto_reply.auto_reply("qual o horário de atendimento?")
    assert result["source"] == "faq"
    assert "segunda" in result["answer"]


def test_auto_reply_sem_faq_marca_fallback(tenant, patch_client):
    connection.set_tenant(tenant)
    patch_client(_chat_client("Não encontrei essa informação."))
    result = auto_reply.auto_reply("vocês fazem unha de gel?")
    assert result["source"] == "fallback"
    assert result["answer"]


def test_auto_reply_indisponivel_nao_vaza_erro(tenant):
    connection.set_tenant(tenant)

    def _boom():
        raise RuntimeError("OPENAI_API_KEY não configurada")

    import apps.ai.client as client_module

    original = client_module.get_client
    client_module.get_client = _boom
    try:
        result = auto_reply.auto_reply("oi")
    finally:
        client_module.get_client = original
    assert result["source"] == "fallback"
    assert result["answer"] == auto_reply.FALLBACK_ANSWER


# --- Endpoints DRF (JWT + tenant) ------------------------------------------


def _signup(client, slug: str):
    return client.post(
        "/api/v1/tenants/signup/",
        {
            "tenant_name": f"Clínica {slug}",
            "tenant_slug": slug,
            "admin_username": "admin",
            "admin_email": "admin@example.com",
            "admin_password": PASSWORD,
        },
        format="json",
    )


def _schema(slug: str) -> str:
    return slug.replace("-", "_")


def _auth(client, access: str) -> None:
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")


def _set_tenant(slug: str):
    connection.set_schema_to_public()
    from apps.tenants.models import Tenant

    tenant_obj = Tenant.objects.using("default").get(schema_name=_schema(slug))
    connection.set_tenant(tenant_obj)
    return tenant_obj


def test_endpoint_classify_200_e_grava_auditoria(patch_client):
    from rest_framework.test import APIClient

    client = APIClient()
    access = _signup(client, "ai-ep-clsf").data["access"]
    _auth(client, access)
    patch_client(_parse_client("booking", 0.9))

    resp = client.post(
        "/api/v1/ai/classify/",
        {"text": "quero agendar uma consulta"},
        format="json",
    )
    assert resp.status_code == 200, resp.content
    assert resp.data == {"intent": "booking", "confidence": 0.9}

    _set_tenant("ai-ep-clsf")
    row = LLMInteraction.objects.get()
    assert row.tenant_id is not None
    assert row.model == "gpt-4o-mini"


def test_endpoint_extract_200_com_conversation_id(patch_client):
    from rest_framework.test import APIClient

    client = APIClient()
    access = _signup(client, "ai-ep-extr").data["access"]

    _set_tenant("ai-ep-extr")
    conversation = Conversation.objects.create(
        channel=Conversation.Channel.TELEGRAM, external_chat_id="555"
    )
    ConversationMessage.objects.create(
        conversation=conversation,
        direction=ConversationMessage.Direction.INBOUND,
        sender_kind=ConversationMessage.SenderKind.CUSTOMER,
        body="Meu nome é Maria, telefone 11988887777",
    )
    conversation_id = conversation.pk
    connection.set_schema_to_public()

    _auth(client, access)
    patch_client(
        _chat_client(
            "",
            tool_arguments=('{"nome":"Maria","telefone":"11988887777","servico":null}'),
        )
    )
    resp = client.post(
        "/api/v1/ai/extract/",
        {"conversation_id": conversation_id},
        format="json",
    )
    assert resp.status_code == 200, resp.content
    assert resp.data["nome"] == "Maria"
    assert resp.data["telefone"] == "11988887777"
    assert resp.data["servico"] is None


def test_endpoint_summarize_200(patch_client):
    from rest_framework.test import APIClient

    client = APIClient()
    access = _signup(client, "ai-ep-sum").data["access"]

    _set_tenant("ai-ep-sum")
    conversation = Conversation.objects.create(
        channel=Conversation.Channel.TELEGRAM, external_chat_id="666"
    )
    ConversationMessage.objects.create(
        conversation=conversation,
        direction=ConversationMessage.Direction.INBOUND,
        sender_kind=ConversationMessage.SenderKind.CUSTOMER,
        body="Quero remarcar",
    )
    conversation_id = conversation.pk
    connection.set_schema_to_public()

    _auth(client, access)
    patch_client(_chat_client("Cliente quer remarcar o horário."))
    resp = client.post(
        "/api/v1/ai/summarize/",
        {"conversation_id": conversation_id},
        format="json",
    )
    assert resp.status_code == 200, resp.content
    assert "remarcar" in resp.data["summary"]


def test_endpoint_auto_reply_200(patch_client):
    from rest_framework.test import APIClient

    client = APIClient()
    access = _signup(client, "ai-ep-rep").data["access"]
    _auth(client, access)
    patch_client(_chat_client("Claro! Posso ajudar."))

    resp = client.post(
        "/api/v1/ai/auto-reply/",
        {"text": "vocês atendem sábado?"},
        format="json",
    )
    assert resp.status_code == 200, resp.content
    assert resp.data["answer"] == "Claro! Posso ajudar."
    assert resp.data["source"] in ("faq", "fallback")


def test_endpoint_sem_jwt_retorna_401():
    from rest_framework.test import APIClient

    client = APIClient()
    resp = client.post("/api/v1/ai/classify/", {"text": "oi"}, format="json")
    assert resp.status_code == 401


def test_endpoint_conversation_de_outro_tenant_404(patch_client):
    """conversation_id de outro tenant → 404 (não vaza existência)."""
    from rest_framework.test import APIClient

    client = APIClient()
    _signup(client, "ai-ep-iso-a")
    access_b = _signup(client, "ai-ep-iso-b").data["access"]

    _set_tenant("ai-ep-iso-a")
    conversation = Conversation.objects.create(
        channel=Conversation.Channel.TELEGRAM, external_chat_id="777"
    )
    ConversationMessage.objects.create(
        conversation=conversation,
        direction=ConversationMessage.Direction.INBOUND,
        sender_kind=ConversationMessage.SenderKind.CUSTOMER,
        body="segredo do tenant A",
    )
    foreign_id = conversation.pk
    connection.set_schema_to_public()

    _auth(client, access_b)
    patch_client(_chat_client("não deveria chegar aqui"))
    resp = client.post(
        "/api/v1/ai/summarize/",
        {"conversation_id": foreign_id},
        format="json",
    )
    assert resp.status_code == 404
    _set_tenant("ai-ep-iso-b")
    assert LLMInteraction.objects.count() == 0
