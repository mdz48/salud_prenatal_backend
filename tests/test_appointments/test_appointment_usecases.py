import unittest
from unittest.mock import MagicMock
from app.features.appointments.application.create_appointment_usecase import CreateAppointmentUseCase
from app.features.appointments.application.get_appointment_usecase import GetAppointmentUseCase
from app.features.appointments.application.get_appointments_by_patient_usecase import GetAppointmentsByPatientUseCase
from app.features.appointments.application.get_appointments_by_doctor_usecase import GetAppointmentsByDoctorUseCase
from app.features.appointments.application.update_appointment_usecase import UpdateAppointmentUseCase
from app.features.appointments.application.delete_appointment_usecase import DeleteAppointmentUseCase
from app.features.appointments.domain.entities import AppointmentEntity
import app.features.users.infrastructure.repositories.patient_repository as pr
import app.features.users.infrastructure.repositories.doctor_repository as dr

class TestAppointmentUseCases(unittest.TestCase):
    def setUp(self):
        self.repo_mock = MagicMock()
        self.db_mock = MagicMock()
        
    def test_create_appointment_success(self):
        patient_repo_mock = MagicMock()
        doctor_repo_mock = MagicMock()
        usecase = CreateAppointmentUseCase(self.repo_mock, patient_repo_mock, doctor_repo_mock)
        entity = AppointmentEntity(
            patient_id=1, 
            doctor_id=2, 
            appointment_date="2026-08-01T10:00:00", 
            reason="Checkup"
        )
        
        patient_repo_mock.get_by_id.return_value = True
        doctor_repo_mock.get_by_id.return_value = True
        self.repo_mock.create.return_value = entity
        
        result = usecase.execute(entity)
        self.assertEqual(result.patient_id, 1)
        self.assertEqual(result.doctor_id, 2)
        self.repo_mock.create.assert_called_once()
        
    def test_create_appointment_patient_not_found(self):
        patient_repo_mock = MagicMock()
        doctor_repo_mock = MagicMock()
        usecase = CreateAppointmentUseCase(self.repo_mock, patient_repo_mock, doctor_repo_mock)
        entity = AppointmentEntity(
            patient_id=1, 
            doctor_id=2, 
            appointment_date="2026-08-01T10:00:00", 
            reason="Checkup"
        )
        
        patient_repo_mock.get_by_id.return_value = None
        
        with self.assertRaises(ValueError):
            usecase.execute(entity)
            
    def test_get_appointment(self):
        usecase = GetAppointmentUseCase(self.repo_mock)
        entity = AppointmentEntity(appointment_id=1, patient_id=1, doctor_id=2, appointment_date="2026-08-01T10:00:00")
        self.repo_mock.get_by_id.return_value = entity
        
        result = usecase.execute(1)
        self.assertEqual(result.appointment_id, 1)
        self.repo_mock.get_by_id.assert_called_with(1)
        
    def test_get_appointments_by_patient(self):
        usecase = GetAppointmentsByPatientUseCase(self.repo_mock)
        entity = AppointmentEntity(appointment_id=1, patient_id=1, doctor_id=2, appointment_date="2026-08-01T10:00:00")
        self.repo_mock.get_by_patient_id.return_value = [entity]
        
        result = usecase.execute(1)
        self.assertEqual(len(result), 1)
        self.repo_mock.get_by_patient_id.assert_called_with(1)
        
    def test_get_appointments_by_doctor(self):
        usecase = GetAppointmentsByDoctorUseCase(self.repo_mock)
        entity = AppointmentEntity(appointment_id=1, patient_id=1, doctor_id=2, appointment_date="2026-08-01T10:00:00")
        self.repo_mock.get_by_doctor_id.return_value = [entity]
        
        result = usecase.execute(1)
        self.assertEqual(len(result), 1)
        self.repo_mock.get_by_doctor_id.assert_called_with(1)
        
    def test_update_appointment(self):
        usecase = UpdateAppointmentUseCase(self.repo_mock)
        entity = AppointmentEntity(appointment_id=1, patient_id=1, doctor_id=2, appointment_date="2026-08-01T10:00:00", reason="New reason")
        self.repo_mock.get_by_id.return_value = entity
        self.repo_mock.update.return_value = entity
        
        result = usecase.execute(entity)
        self.assertEqual(result.reason, "New reason")
        
    def test_delete_appointment(self):
        usecase = DeleteAppointmentUseCase(self.repo_mock)
        entity = AppointmentEntity(appointment_id=1, patient_id=1, doctor_id=2, appointment_date="2026-08-01T10:00:00")
        self.repo_mock.get_by_id.return_value = entity
        
        usecase.execute(1)
        self.repo_mock.delete.assert_called_with(1)

if __name__ == '__main__':
    unittest.main()
