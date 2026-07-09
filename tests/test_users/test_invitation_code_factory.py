"""ADR-12 Factory Method: generación del código de invitación."""
from datetime import datetime, timezone

from app.features.users.domain.invitation_code_factory import (
    InvitationCodeFactory,
    UuidInvitationCodeFactory,
)


def test_uuid_factory_builds_payload():
    payload = UuidInvitationCodeFactory().build(doctor_id=7)
    assert payload["doctor_id"] == 7
    assert isinstance(payload["code"], str) and len(payload["code"]) == 8
    assert payload["expires_at"] > datetime.now(timezone.utc)


def test_factory_method_is_overridable():
    class FixedFactory(InvitationCodeFactory):
        def generate_code(self) -> str:
            return "FIXED123"

    payload = FixedFactory().build(doctor_id=1)
    assert payload["code"] == "FIXED123"
