import os

import requests

from app.users.domain.ports import IPatientLinkedNotifier


class PatientLinkedNotifierAdapter(IPatientLinkedNotifier):
    """Transporte HTTP hacia el endpoint interno de service_transaccional, donde
    viven los observers reales (log + push Firebase) para PatientLinkedEvent.
    Best-effort: swallowea fallos de red, igual que MlPredictionServiceAdapter en
    transaccional -- una notificación caída no debe tumbar la vinculación."""

    def notify(self, patient_id: int, doctor_id: int) -> None:
        transaccional_url = os.getenv("TRANSACCIONAL_URL")
        internal_token = os.getenv("INTERNAL_SERVICE_TOKEN")
        if not transaccional_url or not internal_token:
            return

        try:
            requests.post(
                f"{transaccional_url}/api/v1/notifications/internal/patient-linked",
                json={"patient_id": patient_id, "doctor_id": doctor_id},
                headers={"X-Internal-Token": internal_token},
                timeout=2.0,
            )
        except Exception as e:
            print("Transaccional notify Exception:", str(e))
