import unittest
from unittest.mock import MagicMock
from app.features.consultations.application.create_consultation_usecase import CreateConsultationUseCase
from app.features.consultations.application.get_consultations_by_medical_record_usecase import GetConsultationsByMedicalRecordUseCase
from app.features.consultations.domain.entities import ConsultationEntity

class TestConsultationUseCases(unittest.TestCase):
    def setUp(self):
        self.repo_mock = MagicMock()
        
    def test_create_consultation(self):
        usecase = CreateConsultationUseCase(self.repo_mock)
        entity = ConsultationEntity(
            medical_record_id=1, 
            notes="Notes", 
            objective="Objective", 
            plan="Plan", 
            reported_facts="Facts"
        )
        self.repo_mock.create.return_value = entity
        
        result = usecase.execute(entity)
        self.assertEqual(result.medical_record_id, 1)
        self.repo_mock.create.assert_called_once()
        
    def test_get_consultations_by_medical_record(self):
        usecase = GetConsultationsByMedicalRecordUseCase(self.repo_mock)
        entity = ConsultationEntity(
            consultation_id=1,
            medical_record_id=1, 
            notes="Notes", 
            objective="Objective", 
            plan="Plan", 
            reported_facts="Facts"
        )
        self.repo_mock.get_by_medical_record_id.return_value = [entity]
        
        result = usecase.execute(1)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].medical_record_id, 1)
        self.repo_mock.get_by_medical_record_id.assert_called_with(1)

if __name__ == '__main__':
    unittest.main()
