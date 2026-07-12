from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from .extracted_symptom_entity import ExtractedSymptomEntity


class AggregatedSymptom(BaseModel):
    """Sintoma agregado por concepto clinico (RF-31: recurrencia). Colapsa todas las
    ocurrencias del mismo `code` en una fila con conteo, rango de fechas y zonas
    deduplicadas. Lo consume tanto el aviso del expediente como el historial."""

    code: str
    label: Optional[str] = None
    occurrences: int
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    alarm: bool = False
    zones: List[str] = []

    model_config = ConfigDict(from_attributes=True)


def aggregate_symptoms(symptoms: List[ExtractedSymptomEntity]) -> List[AggregatedSymptom]:
    """Agrupa por `code`, excluye negados, y ordena alarma-primero luego mas-reciente.
    Funcion pura: sin acceso a BD ni efectos secundarios."""
    groups: dict[str, List[ExtractedSymptomEntity]] = {}
    for s in symptoms:
        if s.negated:
            continue
        groups.setdefault(s.code, []).append(s)

    aggregated: List[AggregatedSymptom] = []
    for code, items in groups.items():
        dates = [i.created_at for i in items if i.created_at is not None]
        zone_codes: List[str] = []
        for i in items:
            for z in i.zones:
                if z.code not in zone_codes:
                    zone_codes.append(z.code)
        aggregated.append(AggregatedSymptom(
            code=code,
            label=next((i.label for i in items if i.label), None),
            occurrences=len(items),
            first_seen=min(dates) if dates else None,
            last_seen=max(dates) if dates else None,
            alarm=any(i.alarm for i in items),
            zones=zone_codes,
        ))

    # Dos sorts estables: primero por recencia, luego alarma al frente.
    aggregated.sort(key=lambda a: a.last_seen or datetime.min, reverse=True)
    aggregated.sort(key=lambda a: not a.alarm)
    return aggregated
