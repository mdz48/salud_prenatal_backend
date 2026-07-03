import unittest
from unittest.mock import MagicMock
from app.features.users.application.auth.authenticate_user_usecase import AuthenticateUserUseCase
from app.features.users.application.user.get_user_usecase import GetUserUseCase
from app.core.security import get_password_hash
from app.features.users.domain.user_entity import UserEntity
from app.features.users.domain.doctor_entity import DoctorEntity

class TestUserUseCases(unittest.TestCase):
    def setUp(self):
        self.user_repo_mock = MagicMock()
        self.patient_repo_mock = MagicMock()
        self.doctor_repo_mock = MagicMock()
        self.receptionist_repo_mock = MagicMock()
        
    def test_authenticate_user_success(self):
        usecase = AuthenticateUserUseCase(
            self.user_repo_mock,
            self.patient_repo_mock,
            self.doctor_repo_mock,
            self.receptionist_repo_mock
        )
        mock_user = MagicMock(spec=UserEntity)
        mock_user.password = get_password_hash("password123")
        mock_user.is_active = True
        mock_user.user_id = 1
        mock_user.email = "test@example.com"
        
        class MockRole:
            value = "medico"
            def __str__(self): return "medico"
        mock_user.role = MockRole()
        
        self.user_repo_mock.get_by_email.return_value = mock_user
        self.patient_repo_mock.get_by_user_id.return_value = None
        self.doctor_repo_mock.get_by_user_id.return_value = MagicMock(spec=DoctorEntity, doctor_id=10)
        
        result = usecase.execute("test@example.com", "password123")
        
        self.assertEqual(result["user_id"], 1)
        self.assertEqual(result["doctor_id"], 10)
        self.assertIn("access_token", result)
        
    def test_authenticate_user_wrong_password(self):
        usecase = AuthenticateUserUseCase(
            self.user_repo_mock,
            self.patient_repo_mock,
            self.doctor_repo_mock,
            self.receptionist_repo_mock
        )
        mock_user = MagicMock(spec=UserEntity)
        mock_user.password = get_password_hash("password123")
        self.user_repo_mock.get_by_email.return_value = mock_user
        
        with self.assertRaises(ValueError) as context:
            usecase.execute("test@example.com", "wrongpass")
            
        self.assertEqual(str(context.exception), "Incorrect email or password")
        
    def test_get_user(self):
        usecase = GetUserUseCase(self.user_repo_mock)
        self.user_repo_mock.get_by_id.return_value = {"id": 1, "name": "John"}
        
        result = usecase.execute(1)
        
        self.user_repo_mock.get_by_id.assert_called_once_with(1)
        self.assertEqual(result, {"id": 1, "name": "John"})

if __name__ == "__main__":
    unittest.main()
