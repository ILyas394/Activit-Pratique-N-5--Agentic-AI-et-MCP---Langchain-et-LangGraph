import asyncio

from app.graph import classify_request
from app.graph import graph
from app.manual_data import retrieve_manual
from app.warranty import consulter_garantie


def test_documentation_example_routes_to_documentation():
    category, serial = classify_request(
        "Mon imprimante PX-200 affiche un voyant clignotant."
    )
    assert category == "documentation"
    assert serial is None


def test_warranty_example_routes_to_warranty():
    category, serial = classify_request(
        "Est-ce que mon imprimante est encore sous garantie ? "
        "Son numéro de série est PX200-0042."
    )
    assert category == "garantie"
    assert serial == "PX200-0042"


def test_multimodal_retrieval_returns_figure_and_sources():
    evidence = retrieve_manual(
        "voyant clignotant pictogramme imprimante", "img_px200_01"
    )
    assert "img_px200_01" in evidence
    assert "Source :" in evidence
    assert "incident papier" in evidence


def test_warranty_registry_known_and_unknown_serials():
    assert "PX200-0042" in consulter_garantie("PX200-0042")
    assert "Aucun appareil trouvé" in consulter_garantie("UNKNOWN-0000")


def test_graph_routes_to_the_warranty_agent_and_returns_to_orchestrator():
    result = asyncio.run(
        graph.ainvoke(
            {
                "request": "Garantie du numéro de série PX200-0042 ?",
                "answer": None,
                "history": [
                    {
                        "role": "user",
                        "content": "Garantie du numéro de série PX200-0042 ?",
                    }
                ],
            },
            config={"configurable": {"thread_id": "warranty-test"}},
        )
    )
    assert result["category"] == "garantie"
    assert result["agent"] == "agent_garantie"
    assert "PX200-0042" in result["answer"]
