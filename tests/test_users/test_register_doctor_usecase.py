import unittest
from unittest.mock import MagicMock
from app.features.users.application.doctor.register_doctor_usecase import RegisterDoctorUseCase
from app.features.users.application.dtos import DoctorRegistrationDTO
from app.features.users.domain.user_entity import UserEntity
from app.core.enums import RoleEnum


class TestRegisterDoctorUseCase(unittest.TestCase):
    def setUp(self):
        self.user_repo = MagicMock()
        self.doctor_repo = MagicMock()
        self.subscription_initializer = MagicMock()
        self.usecase = RegisterDoctorUseCase(
            self.user_repo, self.doctor_repo, self.subscription_initializer
        )
        self.dto = DoctorRegistrationDTO(
            name="Ada", last_name="Lovelace", email="ada@x.com", password="secret",
            professional_license="LIC-1", specialty="gineco", office="101",
        )

    def test_creates_pending_subscription_for_new_doctor(self):
        self.user_repo.get_by_email.return_value = None
        self.user_repo.create.return_value = UserEntity(
            user_id=42, name="Ada", last_name="Lovelace", email="ada@x.com",
            password="hashed", role=RoleEnum.doctor,
        )

        self.usecase.execute(self.dto)

        self.subscription_initializer.create_pending.assert_called_once_with(42)

    def test_rejects_duplicate_email_without_subscription(self):
        self.user_repo.get_by_email.return_value = MagicMock()

        with self.assertRaises(ValueError):
            self.usecase.execute(self.dto)

        self.subscription_initializer.create_pending.assert_not_called()


if __name__ == "__main__":
    unittest.main()
