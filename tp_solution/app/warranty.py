"""Consultation locale en lecture seule du registre de démonstration."""

from datetime import date

WARRANTY_REGISTRY: dict[str, dict[str, str]] = {
    "PX200-0042": {
        "product": "Imprimante PX-200 (donnée fictive de démonstration)",
        "expiry_date": "2027-05-01",
    },
    "PX200-0007": {
        "product": "Imprimante PX-200 (donnée fictive de démonstration)",
        "expiry_date": "2024-01-15",
    },
}


def consulter_garantie(serial_number: str) -> str:
    """Lit le registre sans le modifier et renvoie un résultat explicite."""
    serial = serial_number.strip().upper()
    record = WARRANTY_REGISTRY.get(serial)
    if record is None:
        return f"Aucun appareil trouvé pour le numéro de série {serial!r}."

    expiry_date = date.fromisoformat(record["expiry_date"])
    status = "valide" if date.today() <= expiry_date else "expirée"
    return (
        f"Garantie {status} pour {record['product']}. "
        f"Date de fin enregistrée : {expiry_date.isoformat()}. "
        f"Numéro de série : {serial}."
    )
