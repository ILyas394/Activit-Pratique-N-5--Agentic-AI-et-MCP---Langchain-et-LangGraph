"""Serveur MCP Streamable HTTP pour les outils documentaire du TP."""

import os

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

from app.manual_data import retrieve_manual

load_dotenv()
mcp = FastMCP("support-electromenager")


@mcp.tool()
def rechercher_manuel(question: str) -> str:
    """Recherche les passages pertinents du corpus pédagogique PX-200."""
    return retrieve_manual(question)


@mcp.tool()
def rag_multimodal(question: str, image_ref: str | None = None) -> str:
    """Recherche des passages et figures indexées, puis renvoie les preuves."""
    return retrieve_manual(question, image_ref)


if __name__ == "__main__":
    mcp.settings.host = os.getenv("MCP_HOST", mcp.settings.host)
    mcp.settings.port = int(os.getenv("MCP_PORT", "8765"))
    additional_hosts = os.getenv("MCP_ALLOWED_HOSTS")
    if additional_hosts and mcp.settings.transport_security is not None:
        mcp.settings.transport_security.allowed_hosts.extend(
            host.strip()
            for host in additional_hosts.split(",")
            if host.strip()
        )
    mcp.run(transport="streamable-http")
