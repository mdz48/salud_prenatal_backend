"""Re-emite un JWT con el subscription_status fresco desde la DB.

No verifica credenciales: la identidad ya viene probada por el token válido que
presentó el cliente (validado en la ruta vía get_current_user de shared_core).
Solo re-lee el status y re-firma, para cerrar la ventana de staleness del claim
tras un pago (webhook activa la DB, pero el token viejo sigue diciendo 'pending').
"""
from salud_prenatal_shared_core.security import create_access_token

from app.auth.domain.ports import IAuthReadPort


class RefreshTokenUseCase:
    def __init__(self, auth_read: IAuthReadPort):
        self.auth_read = auth_read

    def execute(self, email: str, user_id: int, role: str) -> dict:
        subscription_status = None
        subscription_current_period_end = None
        if role == "doctor":
            sub_info = self.auth_read.get_subscription_status(user_id)
            if sub_info:
                subscription_status = sub_info[0]
                if sub_info[1]:
                    subscription_current_period_end = sub_info[1].isoformat()

        access_token = create_access_token(
            data={
                "sub": email,
                "user_id": user_id,
                "role": role,
                "subscription_status": subscription_status,
                "subscription_current_period_end": subscription_current_period_end,
            }
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "subscription_status": subscription_status,
            "subscription_current_period_end": subscription_current_period_end,
        }
