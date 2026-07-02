from dependency_injector import containers, providers
from app.core.database import get_db
from app.features.medical_record.infrastructure.adapters.ml_prediction_adapter import MlPredictionServiceAdapter

from app.features.appointments.infrastructure.repositories.appointment_repository import AppointmentRepository
from app.features.chat.infrastructure.chat_repository import ChatRepository
from app.features.consultations.infrastructure.repositories.consultation_repository import ConsultationRepository
from app.features.medical_record.infrastructure.repositories.medical_record_repository import MedicalRecordRepository
from app.features.patient_diaries.infrastructure.repositories.patient_diary_repository import PatientDiaryRepository
from app.features.users.infrastructure.repositories.doctor_repository import DoctorRepository
from app.features.users.infrastructure.repositories.invitation_code_repository import InvitationCodeRepository
from app.features.users.infrastructure.repositories.patient_repository import PatientRepository
from app.features.users.infrastructure.repositories.receptionist_repository import ReceptionistRepository
from app.features.users.infrastructure.repositories.user_repository import UserRepository
from app.features.appointments.application.create_appointment_usecase import CreateAppointmentUseCase
from app.features.appointments.application.delete_appointment_usecase import DeleteAppointmentUseCase
from app.features.appointments.application.get_appointments_by_doctor_usecase import GetAppointmentsByDoctorUseCase
from app.features.appointments.application.get_appointments_by_patient_usecase import GetAppointmentsByPatientUseCase
from app.features.appointments.application.get_appointment_usecase import GetAppointmentUseCase
from app.features.appointments.application.update_appointment_usecase import UpdateAppointmentUseCase
from app.features.chat.application.get_history_usecase import GetHistoryUseCase
from app.features.chat.application.save_message_usecase import SaveMessageUseCase
from app.features.consultations.application.create_consultation_usecase import CreateConsultationUseCase
from app.features.consultations.application.get_consultations_by_medical_record_usecase import GetConsultationsByMedicalRecordUseCase
from app.features.medical_record.application.create_medical_record_usecase import CreateMedicalRecordUseCase
from app.features.medical_record.application.get_patient_medical_record_usecase import GetPatientMedicalRecordUseCase
from app.features.patient_diaries.application.create_patient_diary_usecase import CreatePatientDiaryUseCase
from app.features.patient_diaries.application.delete_patient_diary_usecase import DeletePatientDiaryUseCase
from app.features.patient_diaries.application.get_all_patient_diaries_usecase import GetAllPatientDiariesUseCase
from app.features.patient_diaries.application.get_diaries_by_medical_record_usecase import GetDiariesByMedicalRecordUseCase
from app.features.patient_diaries.application.get_patient_diary_by_id_usecase import GetPatientDiaryByIdUseCase
from app.features.patient_diaries.application.update_patient_diary_usecase import UpdatePatientDiaryUseCase
from app.features.users.application.auth_usecases import AuthenticateUserUseCase
from app.features.users.application.doctor_usecases import RegisterDoctorUseCase
from app.features.users.application.doctor_usecases import CreateReceptionistUseCase
from app.features.users.application.doctor_usecases import GetReceptionistsByDoctorUseCase
from app.features.users.application.doctor_usecases import GenerateInvitationCodeUseCase
from app.features.users.application.invitation_usecases import RedeemInvitationCodeUseCase
from app.features.users.application.patient_usecases import RegisterPatientUseCase
from app.features.users.application.patient_usecases import GetPatientsByDoctorUseCase
from app.features.users.application.patient_usecases import GetPatientDashboardUseCase
from app.features.users.application.user_usecases import GetUsersUseCase
from app.features.users.application.user_usecases import GetUserUseCase
from app.features.users.application.user_usecases import UpdateUserUseCase
from app.features.users.application.user_usecases import DeleteUserUseCase

from app.features.appointments.infrastructure.controllers.appointment_controller import AppointmentController
from app.features.consultations.infrastructure.controllers.consultation_controller import ConsultationController
from app.features.medical_record.infrastructure.controllers.medical_record_controller import MedicalRecordController
from app.features.patient_diaries.infrastructure.controllers.patient_diary_controller import PatientDiaryController
from app.features.chat.infrastructure.controllers.chat_controller import ChatController
from app.features.users.infrastructure.controllers.user_controller import UserController
from app.features.users.infrastructure.controllers.auth_controller import AuthController
from app.features.users.infrastructure.controllers.patient_controller import PatientController
from app.features.users.infrastructure.controllers.doctor_controller import DoctorController

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "main",
            "app.features.appointments.infrastructure.routes.appointment_router",
            "app.features.chat.infrastructure.routes.chat_router",
            "app.features.consultations.infrastructure.routes.consultation_router",
            "app.features.medical_record.infrastructure.routes.medical_record_router",
            "app.features.patient_diaries.infrastructure.routes.patient_diary_router",
            "app.features.users.infrastructure.routes.doctor_router",
            "app.features.users.infrastructure.routes.patient_router",
            "app.features.users.infrastructure.routes.user_router",
        ]
    )

    db = providers.Resource(get_db)

    # ML Adapter
    ml_prediction_service = providers.Factory(MlPredictionServiceAdapter)

    # Repositories
    appointment_repository = providers.Factory(AppointmentRepository, db=db)
    chat_repository = providers.Factory(ChatRepository, db=db)
    consultation_repository = providers.Factory(ConsultationRepository, db=db)
    medical_record_repository = providers.Factory(MedicalRecordRepository, db=db)
    patient_diary_repository = providers.Factory(PatientDiaryRepository, db=db)
    doctor_repository = providers.Factory(DoctorRepository, db=db)
    invitation_code_repository = providers.Factory(InvitationCodeRepository, db=db)
    patient_repository = providers.Factory(PatientRepository, db=db)
    receptionist_repository = providers.Factory(ReceptionistRepository, db=db)
    user_repository = providers.Factory(UserRepository, db=db)

    # Use Cases
    create_appointment_use_case = providers.Factory(CreateAppointmentUseCase, appointment_repo=appointment_repository, patient_repo=patient_repository, doctor_repo=doctor_repository)
    delete_appointment_use_case = providers.Factory(DeleteAppointmentUseCase, appointment_repo=appointment_repository)
    get_appointments_by_doctor_use_case = providers.Factory(GetAppointmentsByDoctorUseCase, appointment_repo=appointment_repository)
    get_appointments_by_patient_use_case = providers.Factory(GetAppointmentsByPatientUseCase, appointment_repo=appointment_repository)
    get_appointment_use_case = providers.Factory(GetAppointmentUseCase, appointment_repo=appointment_repository)
    update_appointment_use_case = providers.Factory(UpdateAppointmentUseCase, appointment_repo=appointment_repository)
    get_history_use_case = providers.Factory(GetHistoryUseCase, chat_repository=chat_repository)
    save_message_use_case = providers.Factory(SaveMessageUseCase, chat_repository=chat_repository)
    create_consultation_use_case = providers.Factory(CreateConsultationUseCase, consultation_repo=consultation_repository)
    get_consultations_by_medical_record_use_case = providers.Factory(GetConsultationsByMedicalRecordUseCase, consultation_repo=consultation_repository)
    create_medical_record_use_case = providers.Factory(CreateMedicalRecordUseCase, medical_record_repository=medical_record_repository, patient_repository=patient_repository)
    get_patient_medical_record_use_case = providers.Factory(GetPatientMedicalRecordUseCase, medical_record_repository=medical_record_repository, patient_repository=patient_repository, ml_prediction_service=ml_prediction_service)
    create_patient_diary_use_case = providers.Factory(CreatePatientDiaryUseCase, repository=patient_diary_repository)
    delete_patient_diary_use_case = providers.Factory(DeletePatientDiaryUseCase, repository=patient_diary_repository)
    get_all_patient_diaries_use_case = providers.Factory(GetAllPatientDiariesUseCase, repository=patient_diary_repository)
    get_diaries_by_medical_record_use_case = providers.Factory(GetDiariesByMedicalRecordUseCase, repository=patient_diary_repository)
    get_patient_diary_by_id_use_case = providers.Factory(GetPatientDiaryByIdUseCase, repository=patient_diary_repository)
    update_patient_diary_use_case = providers.Factory(UpdatePatientDiaryUseCase, repository=patient_diary_repository)
    authenticate_user_use_case = providers.Factory(AuthenticateUserUseCase, user_repository=user_repository, patient_repository=patient_repository, doctor_repository=doctor_repository, receptionist_repository=receptionist_repository)
    register_doctor_use_case = providers.Factory(RegisterDoctorUseCase, user_repository=user_repository, doctor_repository=doctor_repository)
    create_receptionist_use_case = providers.Factory(CreateReceptionistUseCase, user_repository=user_repository, doctor_repository=doctor_repository, receptionist_repository=receptionist_repository)
    get_receptionists_by_doctor_use_case = providers.Factory(GetReceptionistsByDoctorUseCase, doctor_repository=doctor_repository, receptionist_repository=receptionist_repository)
    generate_invitation_code_use_case = providers.Factory(GenerateInvitationCodeUseCase, doctor_repository=doctor_repository, invitation_code_repository=invitation_code_repository)
    redeem_invitation_code_use_case = providers.Factory(RedeemInvitationCodeUseCase, patient_repository=patient_repository, invitation_code_repository=invitation_code_repository)
    register_patient_use_case = providers.Factory(RegisterPatientUseCase, user_repository=user_repository, patient_repository=patient_repository)
    get_patients_by_doctor_use_case = providers.Factory(GetPatientsByDoctorUseCase, patient_repository=patient_repository)
    get_patient_dashboard_use_case = providers.Factory(GetPatientDashboardUseCase, patient_repository=patient_repository, user_repository=user_repository, doctor_repository=doctor_repository, appointment_repository=appointment_repository)
    get_users_use_case = providers.Factory(GetUsersUseCase, user_repository=user_repository)
    get_user_use_case = providers.Factory(GetUserUseCase, user_repository=user_repository)
    update_user_use_case = providers.Factory(UpdateUserUseCase, user_repository=user_repository)
    delete_user_use_case = providers.Factory(DeleteUserUseCase, user_repository=user_repository)

    # Controllers
    appointment_controller = providers.Factory(AppointmentController, create_appointment_use_case, get_appointment_use_case, get_appointments_by_patient_use_case, get_appointments_by_doctor_use_case, update_appointment_use_case, delete_appointment_use_case)
    consultation_controller = providers.Factory(ConsultationController, create_consultation_use_case, get_consultations_by_medical_record_use_case)
    medical_record_controller = providers.Factory(MedicalRecordController, create_medical_record_use_case, get_patient_medical_record_use_case)
    patient_diary_controller = providers.Factory(PatientDiaryController, create_patient_diary_use_case, delete_patient_diary_use_case, get_all_patient_diaries_use_case, get_diaries_by_medical_record_use_case, get_patient_diary_by_id_use_case, update_patient_diary_use_case)
    chat_controller = providers.Factory(ChatController, get_history_use_case, save_message_use_case)
    user_controller = providers.Factory(UserController, get_users_use_case, get_user_use_case, update_user_use_case, delete_user_use_case)
    auth_controller = providers.Factory(AuthController, authenticate_user_use_case)
    patient_controller = providers.Factory(PatientController, register_patient_use_case, get_patients_by_doctor_use_case, get_patient_dashboard_use_case, redeem_invitation_code_use_case)
    doctor_controller = providers.Factory(DoctorController, register_doctor_use_case, create_receptionist_use_case, get_receptionists_by_doctor_use_case, generate_invitation_code_use_case)
