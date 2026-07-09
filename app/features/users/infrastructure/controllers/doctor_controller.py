from fastapi import HTTPException, status
from app.features.users.infrastructure.schemas.doctor_schema import DoctorRegistration
from app.features.users.application.doctor.register_doctor_usecase import RegisterDoctorUseCase
from app.features.users.application.doctor.create_receptionist_usecase import CreateReceptionistUseCase
from app.features.users.application.doctor.get_receptionists_by_doctor_usecase import GetReceptionistsByDoctorUseCase
from app.features.users.application.doctor.generate_invitation_code_usecase import GenerateInvitationCodeUseCase
from app.features.users.application.doctor.get_doctor_by_id_usecase import GetDoctorByIdUseCase
from app.features.users.application.doctor.get_doctor_dashboard_usecase import GetDoctorDashboardUseCase
from app.features.users.application.doctor.get_receptionist_by_id_usecase import GetReceptionistByIdUseCase
from app.features.users.application.doctor.get_receptionist_dashboard_usecase import GetReceptionistDashboardUseCase
from app.features.users.infrastructure.schemas.receptionist_schema import ReceptionistCreate
from app.features.users.infrastructure.schemas.patient_schema import PatientSearchResult

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
        get_receptionist_dashboard_use_case
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

    def create_receptionist(self, doctor_id: int, data: ReceptionistCreate):
        from app.features.users.application.dtos import ReceptionistCreateDTO
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
        from app.features.users.application.dtos import DoctorRegistrationDTO
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
