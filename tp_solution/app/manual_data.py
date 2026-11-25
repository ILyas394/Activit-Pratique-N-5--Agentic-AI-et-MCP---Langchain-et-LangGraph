"""Petit corpus fictif pour les démonstrations du TP.

Ces extraits ne sont pas le manuel réel d'un produit commercial.
Remplacer ce corpus par les manuels et figures validés du distributeur.
"""

MANUAL_PASSAGES = [
    {
        "id": "px200-troubleshooting-3.2",
        "source": "Manuel pédagogique PX-200, Dépannage, §3.2, p. 47",
        "text": (
            "Dans ce corpus de démonstration, le voyant orange clignotant "
            "associé au pictogramme de feuille indique un incident papier. "
            "Vérifier le bac et le chemin papier. Mettre l'imprimante hors "
            "tension avant de retirer délicatement une feuille visible; "
            "ne pas forcer les rouleaux."
        ),
    },
    {
        "id": "px200-troubleshooting-3.3",
        "source": "Manuel pédagogique PX-200, Dépannage, §3.3, p. 48",
        "text": (
            "Si le voyant persiste après vérification du papier, retirer "
            "puis réinsérer le bac, remettre l'imprimante sous tension et "
            "contacter le support si le signal reste affiché."
        ),
    },
]

FIGURES = {
    "img_px200_01": {
        "id": "fig-px200-paper-warning",
        "source": "Manuel pédagogique PX-200, figure 12, p. 47",
        "description": (
            "Pictogramme de feuille près d'un voyant orange clignotant; "
            "figure d'exemple indexée sous la référence img_px200_01."
        ),
    },
}


def retrieve_manual(question: str, image_ref: str | None = None) -> str:
    """Retourne des passages et, si elle existe, la figure correspondante."""
    terms = {
        word.strip(".,?!:;()[]{}\"'").lower()
        for word in question.split()
        if len(word.strip(".,?!:;()[]{}\"'")) > 2
    }

    def score(passage: dict[str, str]) -> int:
        words = set(passage["text"].lower().split())
        return sum(term in words for term in terms)

    passages = sorted(MANUAL_PASSAGES, key=score, reverse=True)[:2]
    evidence = [
        f"- {item['text']} [Source : {item['source']}]"
        for item in passages
        if score(item) > 0
    ]
    if image_ref:
        figure = FIGURES.get(image_ref)
        if figure:
            evidence.append(
                f"- Figure {figure['id']} : {figure['description']} "
                f"[Source : {figure['source']}]"
            )
        else:
            evidence.append(
                f"- Aucune figure indexée sous la référence {image_ref!r}."
            )

    if not evidence:
        return (
            "Aucun passage pertinent n'a été trouvé dans le corpus pédagogique. "
            "Ne déduisez pas de diagnostic sans source."
        )
    return "\n".join(evidence)
