"""Caso de uso de login — verifica credenciales y EMITE el JWT con claims.

Mantiene la respuesta rica del monolito (patient_id/doctor_id/medical_record_id/
receptionist/subscription_status) para no cambiar el contrato del frontend. La
diferencia con el monolito: en vez de 4 repos + 2 lookups de otras features, usa
un único puerto de lectura (`IAuthReadPort`) sobre la DB compartida.

El token incluye `subscription_status` como claim para que los demás servicios
autoricen (require_active_subscription) sin volver a la DB.
"""
from salud_prenatal_shared_core.security import verify_password, create_access_token

from app.auth.domain.ports import IAuthReadPort


class AuthenticateUserUseCase:
    def __init__(self, auth_read: IAuthReadPort):
        self.auth_read = auth_read

    def execute(self, email: str, password: str) -> dict:
        user = self.auth_read.get_user_by_email(email)
        if not user:
            raise ValueError("Incorrect email or password")
        if not verify_password(password, user.password):
            raise ValueError("Incorrect email or password")
        if not user.is_active:
            raise ValueError("Inactive user")

        role_str = user.role.value if hasattr(user.role, "value") else str(user.role)

        patient_id = None
        doctor_id = None
        medical_record_id = None
        receptionist_info = None
        receptionist_id = None
        subscription_status = None

        if role_str == "paciente":
            patient = self.auth_read.get_patient_by_user_id(user.user_id)
            if patient:
                patient_id = patient.patient_id
                doctor_id = patient.doctor_id
                medical_record_id = self.auth_read.get_medical_record_id(
                    patient.patient_id, patient.doctor_id
                )
        elif role_str == "doctor":
            doctor = self.auth_read.get_doctor_by_user_id(user.user_id)
            if doctor:
                doctor_id = doctor.doctor_id
            subscription_status = self.auth_read.get_subscription_status(user.user_id)
        elif role_str == "recepcionista":
            receptionist = self.auth_read.get_receptionist_by_user_id(user.user_id)
            if receptionist:
                doctor_id = receptionist.doctor_id
                receptionist_id = receptionist.receptionist_id

        access_token = create_access_token(
            data={
                "sub": user.email,
                "user_id": user.user_id,
                "role": role_str,
                "subscription_status": subscription_status,
            }
        )

        # receptionist_info: nombre del primer recepcionista del doctor (si existe).
        if doctor_id:
            receptionists = self.auth_read.get_receptionists_by_doctor_id(doctor_id)
            if receptionists:
                first = receptionists[0]
                first_user = self.auth_read.get_user_by_id(first.user_id)
                if first_user:
                    receptionist_info = {
                        "user_id": first_user.user_id,
                        "name": first_user.name,
                        "last_name": first_user.last_name,
                    }

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.user_id,
            "role": role_str,
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "medical_record_id": medical_record_id,
            "receptionist_id": receptionist_id,
            "receptionist": receptionist_info,
            "subscription_status": subscription_status,
        }
