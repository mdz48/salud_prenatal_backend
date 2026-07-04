from fastapi import HTTPException, status

from app.features.appointments.domain.appointment_entity import AppointmentEntity
from app.features.appointments.infrastructure.schemas.appointment_schema import AppointmentCreate, AppointmentUpdate

from app.features.appointments.application.create_appointment_usecase import CreateAppointmentUseCase
from app.features.appointments.application.get_appointment_usecase import GetAppointmentUseCase
from app.features.appointments.application.get_appointments_by_patient_usecase import GetAppointmentsByPatientUseCase
from app.features.appointments.application.get_appointments_by_doctor_usecase import GetAppointmentsByDoctorUseCase
from app.features.appointments.application.update_appointment_usecase import UpdateAppointmentUseCase
from app.features.appointments.application.delete_appointment_usecase import DeleteAppointmentUseCase

class AppointmentController:
    def __init__(
        self,
        create_appointment_usecase: CreateAppointmentUseCase,
        get_appointment_usecase: GetAppointmentUseCase,
        get_appointments_by_patient_usecase: GetAppointmentsByPatientUseCase,
        get_appointments_by_doctor_usecase: GetAppointmentsByDoctorUseCase,
        update_appointment_usecase: UpdateAppointmentUseCase,
        delete_appointment_usecase: DeleteAppointmentUseCase,
    ):
        self.create_appointment_usecase = create_appointment_usecase
        self.get_appointment_usecase = get_appointment_usecase
        self.get_appointments_by_patient_usecase = get_appointments_by_patient_usecase
        self.get_appointments_by_doctor_usecase = get_appointments_by_doctor_usecase
        self.update_appointment_usecase = update_appointment_usecase
        self.delete_appointment_usecase = delete_appointment_usecase

    def create_appointment(self, data: AppointmentCreate):
        try:
            entity = AppointmentEntity(
                patient_id=data.patient_id,
                doctor_id=data.doctor_id,
                appointment_date=data.appointment_date,
                reason=data.reason
            )
            return self.create_appointment_usecase.execute(entity)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def get_appointment(self, appointment_id: int):
        try:
            return self.get_appointment_usecase.execute(appointment_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    def get_appointments_by_patient(self, patient_id: int):
        return self.get_appointments_by_patient_usecase.execute(patient_id)

    def get_appointments_by_doctor(self, doctor_id: int):
        return self.get_appointments_by_doctor_usecase.execute(doctor_id)

    def update_appointment(self, appointment_id: int, data: AppointmentUpdate):
        try:
            update_data = data.model_dump(exclude_unset=True)
            return self.update_appointment_usecase.execute(appointment_id, update_data)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    def delete_appointment(self, appointment_id: int):
        try:
            self.delete_appointment_usecase.execute(appointment_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
