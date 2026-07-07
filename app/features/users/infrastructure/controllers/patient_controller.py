from fastapi import HTTPException, status
from app.features.users.infrastructure.schemas.patient_schema import PatientRegistration
from app.features.users.application.patient.register_patient_usecase import RegisterPatientUseCase
from app.features.users.application.patient.get_patients_by_doctor_usecase import GetPatientsByDoctorUseCase
from app.features.users.application.patient.get_patient_dashboard_usecase import GetPatientDashboardUseCase
from app.features.users.application.invitation.redeem_invitation_code_usecase import RedeemInvitationCodeUseCase
from app.features.users.infrastructure.schemas.invitation_code_schema import RedeemCodeRequest

class PatientController:
    def __init__(self, get_patient_dashboard_use_case, register_patient_use_case, redeem_invitation_code_use_case):
        self.get_patient_dashboard_use_case = get_patient_dashboard_use_case
        self.register_patient_use_case = register_patient_use_case
        self.redeem_invitation_code_use_case = redeem_invitation_code_use_case

    def get_patient_dashboard(self, patient_id: int):
        try:
            return self.get_patient_dashboard_use_case.execute(patient_id=patient_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while fetching the dashboard.")

    def register_patient(self, data: PatientRegistration):
        from app.features.users.application.dtos import PatientRegistrationDTO
        try:
            dto = PatientRegistrationDTO(**data.model_dump(exclude_unset=True))
            return self.register_patient_use_case.execute(data=dto)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while registering the patient.")

    def redeem_code(self, patient_id: int, data: RedeemCodeRequest):
        try:
            return self.redeem_invitation_code_use_case.execute(patient_id=patient_id, code=data.code)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while redeeming the code.")
