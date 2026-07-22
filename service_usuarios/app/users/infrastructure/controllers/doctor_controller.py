from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from app.users.infrastructure.schemas.doctor_schema import DoctorRegistration
from app.users.application.doctor.register_doctor_usecase import RegisterDoctorUseCase
from app.users.application.doctor.create_receptionist_usecase import CreateReceptionistUseCase
from app.users.application.doctor.get_receptionists_by_doctor_usecase import GetReceptionistsByDoctorUseCase
from app.users.application.doctor.generate_invitation_code_usecase import GenerateInvitationCodeUseCase
from app.users.application.doctor.get_doctor_by_id_usecase import GetDoctorByIdUseCase
from app.users.application.doctor.get_doctor_dashboard_usecase import GetDoctorDashboardUseCase
from app.users.application.doctor.get_receptionist_by_id_usecase import GetReceptionistByIdUseCase
from app.users.application.doctor.get_receptionist_dashboard_usecase import GetReceptionistDashboardUseCase
from app.users.infrastructure.schemas.receptionist_schema import ReceptionistCreate
from app.users.infrastructure.schemas.patient_schema import PatientSearchResult, PatientDirectoryEntry
from app.users.infrastructure.schemas.unlink_request_schema import ResolveUnlinkRequest

class DoctorController:
    def __init__(
        self,
        create_receptionist_use_case,
        get_receptionists_by_doctor_use_case,
        register_doctor_use_case,
        get_patients_by_doctor_use_case,
        generate_invitation_code_use_case,
        search_patients_by_name_use_case,
        get_doctor_by_id_use_case,
        get_doctor_dashboard_use_case,
        get_receptionist_by_id_use_case,
        get_receptionist_dashboard_use_case,
        search_patient_directory_use_case,
        list_unlink_requests_use_case,
        resolve_unlink_request_use_case,
    ):
        self.create_receptionist_use_case = create_receptionist_use_case
        self.get_receptionists_by_doctor_use_case = get_receptionists_by_doctor_use_case
        self.register_doctor_use_case = register_doctor_use_case
        self.get_patients_by_doctor_use_case = get_patients_by_doctor_use_case
        self.generate_invitation_code_use_case = generate_invitation_code_use_case
        self.search_patients_by_name_use_case = search_patients_by_name_use_case
        self.get_doctor_by_id_use_case = get_doctor_by_id_use_case
        self.get_doctor_dashboard_use_case = get_doctor_dashboard_use_case
        self.get_receptionist_by_id_use_case = get_receptionist_by_id_use_case
        self.get_receptionist_dashboard_use_case = get_receptionist_dashboard_use_case
        self.search_patient_directory_use_case = search_patient_directory_use_case
        self.list_unlink_requests_use_case = list_unlink_requests_use_case
        self.resolve_unlink_request_use_case = resolve_unlink_request_use_case

    def create_receptionist(self, doctor_id: int, data: ReceptionistCreate):
        from app.users.application.dtos import ReceptionistCreateDTO
        try:
            dto = ReceptionistCreateDTO(**data.model_dump(exclude_unset=True))
            return self.create_receptionist_use_case.execute(doctor_id=doctor_id, data=dto)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            print(f"Error creating receptionist: {repr(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating the receptionist.")

    def get_receptionists_by_doctor(self, doctor_id: int):
        try:
            return self.get_receptionists_by_doctor_use_case.execute(doctor_id=doctor_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception as e:
            print(f"Error fetching receptionists: {repr(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while fetching receptionists.")

    def register_doctor(self, data: DoctorRegistration):
        from app.users.application.dtos import DoctorRegistrationDTO
        try:
            dto = DoctorRegistrationDTO(**data.model_dump(exclude_unset=True))
            return self.register_doctor_use_case.execute(data=dto)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            print(f"Error registering doctor: {repr(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while registering the doctor.")

    def get_patients_by_doctor(self, doctor_id: int):
        try:
            return self.get_patients_by_doctor_use_case.execute(doctor_id=doctor_id)
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while fetching patients.")

    def search_patients(self, doctor_id: int, name=None, last_name=None):
        try:
            patients = self.search_patients_by_name_use_case.execute(doctor_id=doctor_id, name=name, last_name=last_name)
            return [
                PatientSearchResult(
                    patient_id=p.patient_id,
                    user_id=p.user_id,
                    name=p.user.name,
                    last_name=p.user.last_name,
                    age=p.age,
                )
                for p in patients
            ]
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            print(f"Error searching patients: {repr(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while searching patients.")

    def search_patient_directory(
        self,
        doctor_id: int,
        risk_cluster: Optional[str] = None,
        linked_after: Optional[datetime] = None,
        linked_before: Optional[datetime] = None,
    ):
        try:
            patients = self.search_patient_directory_use_case.execute(
                doctor_id=doctor_id,
                risk_cluster=risk_cluster,
                linked_after=linked_after,
                linked_before=linked_before,
            )
            return [PatientDirectoryEntry.model_validate(p) for p in patients]
        except Exception as e:
            print(f"Error searching patient directory: {repr(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while searching the patient directory.")

    def get_doctor_by_id(self, doctor_id: int):
        try:
            doctor = self.get_doctor_by_id_use_case.execute(doctor_id=doctor_id)
            if not doctor:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
            return doctor
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error fetching doctor: {repr(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while fetching the doctor.")

    def get_doctor_dashboard(self, doctor_id: int):
        try:
            return self.get_doctor_dashboard_use_case.execute(doctor_id=doctor_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception as e:
            print(f"Error fetching doctor dashboard: {repr(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while fetching the doctor dashboard.")

    def get_receptionist_by_id(self, receptionist_id: int):
        try:
            receptionist = self.get_receptionist_by_id_use_case.execute(receptionist_id=receptionist_id)
            if not receptionist:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receptionist not found")
            return receptionist
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error fetching receptionist: {repr(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while fetching the receptionist.")

    def get_receptionist_dashboard(self, receptionist_id: int):
        try:
            return self.get_receptionist_dashboard_use_case.execute(receptionist_id=receptionist_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception as e:
            print(f"Error fetching receptionist dashboard: {repr(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while fetching the receptionist dashboard.")

    def generate_invitation_code(self, doctor_id: int):
        try:
            return self.generate_invitation_code_use_case.execute(doctor_id=doctor_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while generating the invitation code.")

    def list_unlink_requests(self, doctor_id: int, status_filter=None):
        try:
            return self.list_unlink_requests_use_case.execute(doctor_id=doctor_id, status=status_filter)
        except Exception as e:
            print(f"Error listing unlink requests: {repr(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while fetching unlink requests.")

    def resolve_unlink_request(self, doctor_id: int, request_id: int, data: ResolveUnlinkRequest):
        try:
            return self.resolve_unlink_request_use_case.execute(
                doctor_id=doctor_id, request_id=request_id, new_status=data.status
            )
        except ValueError as e:
            error_str = str(e)
            if "not found" in error_str:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_str)
            if "already" in error_str:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error_str)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_str)
        except Exception as e:
            print(f"Error resolving unlink request: {repr(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while resolving the unlink request.")
