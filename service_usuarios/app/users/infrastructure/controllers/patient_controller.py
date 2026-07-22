from fastapi import HTTPException, status
from app.users.infrastructure.schemas.patient_schema import PatientRegistration
from app.users.application.patient.register_patient_usecase import RegisterPatientUseCase
from app.users.application.patient.get_patients_by_doctor_usecase import GetPatientsByDoctorUseCase
from app.users.application.patient.get_patient_dashboard_usecase import GetPatientDashboardUseCase
from app.users.application.invitation.redeem_invitation_code_usecase import RedeemInvitationCodeUseCase
from app.users.infrastructure.schemas.invitation_code_schema import RedeemCodeRequest
from app.users.infrastructure.schemas.unlink_request_schema import UnlinkRequestCreate

class PatientController:
    def __init__(
        self,
        get_patient_dashboard_use_case,
        register_patient_use_case,
        redeem_invitation_code_use_case,
        create_unlink_request_use_case,
        list_patient_unlink_requests_use_case,
        cancel_unlink_request_use_case,
    ):
        self.get_patient_dashboard_use_case = get_patient_dashboard_use_case
        self.register_patient_use_case = register_patient_use_case
        self.redeem_invitation_code_use_case = redeem_invitation_code_use_case
        self.create_unlink_request_use_case = create_unlink_request_use_case
        self.list_patient_unlink_requests_use_case = list_patient_unlink_requests_use_case
        self.cancel_unlink_request_use_case = cancel_unlink_request_use_case

    def get_patient_dashboard(self, patient_id: int):
        try:
            return self.get_patient_dashboard_use_case.execute(patient_id=patient_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while fetching the dashboard.")

    def register_patient(self, data: PatientRegistration):
        from app.users.application.dtos import PatientRegistrationDTO
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

    def create_unlink_request(self, patient_id: int, data: UnlinkRequestCreate):
        try:
            return self.create_unlink_request_use_case.execute(patient_id=patient_id, reason=data.reason)
        except ValueError as e:
            error_str = str(e)
            if "not found" in error_str:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_str)
            if "already" in error_str:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error_str)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_str)
        except Exception as e:
            print(f"Error creating unlink request: {repr(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating the unlink request.")

    def list_unlink_requests(self, patient_id: int, status_filter=None):
        try:
            return self.list_patient_unlink_requests_use_case.execute(patient_id=patient_id, status=status_filter)
        except Exception as e:
            print(f"Error listing unlink requests: {repr(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while fetching unlink requests.")

    def cancel_unlink_request(self, patient_id: int, request_id: int):
        try:
            return self.cancel_unlink_request_use_case.execute(patient_id=patient_id, request_id=request_id)
        except ValueError as e:
            error_str = str(e)
            if "not found" in error_str:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_str)
            if "already" in error_str:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error_str)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_str)
        except Exception as e:
            print(f"Error cancelling unlink request: {repr(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while cancelling the unlink request.")
