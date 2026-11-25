# Connexion de n8n au serveur MCP

1. Démarrer le serveur (`python -m app.mcp_server`) et vérifier que
   `http://127.0.0.1:8765/mcp` est accessible depuis **n8n**. Si n8n tourne
   dans Docker, `127.0.0.1` désigne le conteneur n8n : utiliser un réseau
   privé partagé, écouter sur `MCP_HOST=0.0.0.0`, puis définir
   `MCP_ALLOWED_HOSTS=mcp-server:8765` et l'URL
   `http://mcp-server:8765/mcp`. Ne pas exposer le serveur de démonstration
   directement sur Internet.
2. Dans n8n, créer un workflow avec un nœud **AI Agent** et un modèle de chat
   configuré.
3. Ajouter le nœud **MCP Client Tool** comme sous-nœud de l'agent. Choisir le
   transport **Streamable HTTP**, saisir l'URL ci-dessus et découvrir les
   outils `rechercher_manuel` et `rag_multimodal`.
4. Relier la sortie de l'agent à une réponse (Chat Trigger / Respond to Chat).
   Pour une question avec photo, transmettre `question` et la référence
   `image_ref` (par exemple `img_px200_01`) à `rag_multimodal`.

Le nœud MCP Client Tool dépend de la version de n8n installée. Si le transport
Streamable HTTP n'est pas proposé, mettre à jour n8n et le nœud
`@n8n/n8n-nodes-langchain`; ne pas remplacer silencieusement le transport par
SSE ou stdio.
