# TP Agentic AI — solution exécutable

Les notebooks du dossier parent restent les supports des parties A (LangChain)
et B (concepts LangGraph, agentic RAG et HITL). Ce répertoire complète le TP
avec un serveur MCP Streamable HTTP, l'orchestrateur de synthèse demandé en D,
une interface Streamlit et la procédure n8n de la partie C.

> Les passages du manuel et les entrées du registre sont des données fictives
> de démonstration. La réponse documentaire est sourcée dans ce corpus local,
> mais ne doit pas être présentée comme une consigne du fabricant.

## Correspondance avec l'énoncé

| Partie | Support / fichier | Contenu |
|---|---|---|
| A — LangChain | `../agentic_ai_with_langchain_V3.ipynb` | Agent simple, mémoire, tools, DuckDuckGo, Tavily, PythonREPLTool, dynamic model/prompt, tool error handling, guardrails, human-in-the-loop, RAG comme tool. |
| B — LangGraph | `../demo-langgraph.ipynb` | État, nœuds, arêtes, conditions, boucles, agent avec tools/mémoire, agentic RAG, HITL et systèmes multi-agents. |
| B — Studio / Streamlit | `langgraph.json`, `streamlit_app.py` | Graphe SAV lançable dans LangGraph Studio et interface chat locale. |
| C — MCP / n8n | `app/mcp_server.py`, `n8n/README.md` | Deux tools MCP en Streamable HTTP, test Inspector, client MCP LangGraph et raccordement d'un AI Agent n8n. |
| D — Synthèse | `app/graph.py` | Orchestrateur, routage exclusif et retour des agents spécialisés à l'orchestrateur avant la fin. |

## Installation

Depuis ce répertoire :

```bash
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Le serveur MCP et le chatbot local n'exigent pas de clé LLM : la classification
et l'orchestration sont déterministes pour que les deux cas du sujet soient
reproductibles. Les clés `OPENAI_API_KEY` et `TAVILY_API_KEY` ne sont utiles
que pour les cellules LangChain des notebooks qui les appellent.

Pour le notebook LangGraph, sélectionner le kernel Python voulu dans VS Code,
puis installer les dépendances depuis ce kernel :

```python
%pip install -r tp_solution/requirements.txt
```

Le notebook charge la clé OpenAI avec `load_dotenv(override=True)`. Placer un
fichier `.env` à la racine du workspace avec `OPENAI_API_KEY=...` avant
d'exécuter les cellules qui créent `ChatOpenAI`. Les cellules RAG nécessitent
aussi un dossier `pdfs/` contenant les documents attendus. Sans clé ou sans
PDF, les concepts de graphe déterministes restent exécutables, mais les
exemples LLM/RAG concernés ne peuvent pas être lancés.

## C — Serveur et client MCP

Dans un premier terminal, depuis `tp_solution/` :

```bash
python -m app.mcp_server
```

Le serveur expose `rechercher_manuel` et `rag_multimodal` en Streamable HTTP
sur `http://127.0.0.1:8765/mcp`. Dans un second terminal, lancer l'Inspector :

```bash
npx -y @modelcontextprotocol/inspector
```

Dans l'Inspector, choisir le transport Streamable HTTP et saisir l'URL
`http://127.0.0.1:8765/mcp`, puis essayer les deux tools. Le nœud documentaire
du graphe est le client MCP Python et appelle `rag_multimodal` sur ce même
transport. Pour n8n, suivre [n8n/README.md](./n8n/README.md).

## D — Orchestrateur et deux parcours

Le graphe est explicitement `START → orchestrator → agent spécialisé →
orchestrator → END`. L'orchestrateur classe une demande dans une seule
catégorie; l'agent documentaire utilise le tool MCP distant, tandis que
l'agent garantie appelle la fonction locale `consulter_garantie`, dont le
registre statique est en lecture seule.

Exemple documentation :

```text
Mon imprimante PX-200 affiche un voyant clignotant.
Que signifie le pictogramme sur la photo jointe ?
Référence : img_px200_01
```

Attendu : catégorie `documentation`, agent `agent_documentaire`, éléments de
preuve issus du manuel pédagogique et de la figure indexée.

Exemple garantie :

```text
Est-ce que mon imprimante est encore sous garantie ?
Son numéro de série est PX200-0042.
```

Attendu : catégorie `garantie`, agent `agent_garantie`, entrée PX200-0042 du
registre fictif.

## B — LangGraph Studio et Streamlit

Avec le serveur MCP toujours démarré :

```bash
langgraph dev
```

La configuration `langgraph.json` publie le graphe `sav` pour Studio. Le
graphe utilise un checkpointer mémoire; l'historique est conservé par
`thread_id` tant que le processus tourne.

Pour l'interface :

```bash
streamlit run streamlit_app.py
```

Saisir une question dans la zone de chat. Pour le parcours documentaire,
renseigner aussi `img_px200_01` dans le champ de référence de photo.

## Tests

Depuis `tp_solution/` :

```bash
python -m pytest
```

Les tests vérifient les deux routages attendus, la recherche sourcée de la
figure d'exemple et la lecture du registre de garantie.
