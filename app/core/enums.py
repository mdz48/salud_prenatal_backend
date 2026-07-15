from enum import Enum

class RoleEnum(str, Enum):
    admin = "admin"
    patient = "paciente"
    doctor = "doctor"
    recepcionist = "recepcionista"

class BloodTypeEnum(str, Enum):
    A_pos = "A+"
    A_neg = "A-"
    B_pos = "B+"
    B_neg = "B-"
    AB_pos = "AB+"
    AB_neg = "AB-"
    O_pos = "O+"
    O_neg = "O-"

class AppointmentStatusEnum(str, Enum):
    pending = "pendiente"
    confirmed = "confirmada"
    cancelled = "cancelada"
    rescheduled = "reprogramada"

class PlanTypeEnum(str, Enum):
    basic = "basic"
    premium = "premium"

class SubscriptionStatusEnum(str, Enum):
    pending = "pending"
    active = "active"
    past_due = "past_due"
    canceled = "canceled"