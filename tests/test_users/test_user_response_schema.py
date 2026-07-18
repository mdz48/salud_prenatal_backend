import pytest

from app.features.users.infrastructure.schemas.user_schema import UserResponse


def test_user_response_accepts_legacy_short_fields():
    data = {
        "user_id": 1,
        "name": "Ana",
        "last_name": "Do",
        "email": "ana@example.com",
        "phone": "12345678",
        "role": "paciente",
        "is_active": True,
        "image_url": None,
        "created_at": "2026-07-07T00:00:00Z",
        "updated_at": None,
    }
    
    result = UserResponse.model_validate(data)

    assert result.last_name == "Do"
    assert result.phone == "12345678"
