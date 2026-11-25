"""Orchestrateur LangGraph et agents spécialisés du service après-vente."""

from __future__ import annotations

import os
import operator
import re
from typing import Annotated, Literal, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from app.warranty import consulter_garantie

Category = Literal["documentation", "garantie"]


class SupportState(TypedDict, total=False):
    request: str
    image_ref: str | None
    serial_number: str | None
    category: Category | None
    agent: str | None
    answer: str | None
    history: Annotated[list[dict[str, str]], operator.add]


def classify_request(text: str) -> tuple[Category, str | None]:
    """Classe chaque demande dans une seule catégorie."""
    serial_match = re.search(r"\bPX\d{2,}-\d{3,}\b", text, flags=re.IGNORECASE)
    warranty_terms = ("garantie", "couvert", "sous garantie", "numéro de série")
    if serial_match or any(term in text.lower() for term in warranty_terms):
        return "garantie", serial_match.group(0).upper() if serial_match else None
    return "documentation", None


async def call_rag_multimodal(
    question: str, image_ref: str | None
) -> str:
    """Appelle l'outil distant via le transport MCP Streamable HTTP."""
    server_url = os.getenv(
        "MCP_SERVER_URL", "http://127.0.0.1:8765/mcp"
    )
    async with streamablehttp_client(server_url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(
                "rag_multimodal",
                {"question": question, "image_ref": image_ref},
            )
    if result.isError:
        details = "\n".join(
            item.text for item in result.content if hasattr(item, "text")
        )
        raise RuntimeError(f"Échec de l'outil MCP rag_multimodal: {details}")
    return "\n".join(
        item.text for item in result.content if hasattr(item, "text")
    )


async def orchestrator(state: SupportState) -> dict:
    if state.get("answer"):
        return {}
    category, serial_number = classify_request(state.get("request", ""))
    return {
        "category": category,
        "agent": (
            "agent_documentaire"
            if category == "documentation"
            else "agent_garantie"
        ),
        "serial_number": serial_number,
    }


async def agent_documentaire(state: SupportState) -> dict:
    answer = await call_rag_multimodal(
        state.get("request", ""), state.get("image_ref")
    )
    return {
        "answer": answer,
        "history": [{"role": "assistant", "content": answer}],
    }


async def agent_garantie(state: SupportState) -> dict:
    serial_number = state.get("serial_number")
    if not serial_number:
        answer = (
            "Pour vérifier la garantie, indiquez le numéro de série "
            "(ex. PX200-0042)."
        )
    else:
        answer = consulter_garantie(serial_number)
    return {
        "answer": answer,
        "history": [{"role": "assistant", "content": answer}],
    }


def route_from_orchestrator(
    state: SupportState,
) -> Literal["finish", "documentation", "garantie"]:
    if state.get("answer"):
        return "finish"
    return state.get("category", "documentation")


builder = StateGraph(SupportState)
builder.add_node("orchestrator", orchestrator)
builder.add_node("agent_documentaire", agent_documentaire)
builder.add_node("agent_garantie", agent_garantie)
builder.add_edge(START, "orchestrator")
builder.add_conditional_edges(
    "orchestrator",
    route_from_orchestrator,
    {
        "documentation": "agent_documentaire",
        "garantie": "agent_garantie",
        "finish": END,
    },
)
builder.add_edge("agent_documentaire", "orchestrator")
builder.add_edge("agent_garantie", "orchestrator")

graph = builder.compile(checkpointer=MemorySaver())
