from dependency_injector import containers, providers
from app.core.database import get_db
from app.features.medical_record.infrastructure.adapters.ml_prediction_adapter import MlPredictionServiceAdapter

from app.features.appointments.infrastructure.repositories.appointment_repository import AppointmentRepository
from app.features.chat.infrastructure.repositories.chat_repository import ChatRepository
from app.features.consultations.infrastructure.repositories.consultation_repository import ConsultationRepository
from app.features.medical_record.infrastructure.repositories.medical_record_repository import MedicalRecordRepository
from app.features.patient_diaries.infrastructure.repositories.patient_diary_repository import PatientDiaryRepository
from app.features.users.infrastructure.repositories.doctor_repository import DoctorRepository
from app.features.users.infrastructure.repositories.invitation_code_repository import InvitationCodeRepository
from app.features.users.infrastructure.repositories.patient_repository import PatientRepository
from app.features.medical_record.infrastructure.adapters.patient_info_adapter import PatientInfoAdapter
from app.features.users.infrastructure.adapters.medical_record_lookup_adapter import MedicalRecordLookupAdapter
from app.features.users.infrastructure.adapters.appointment_lookup_adapter import AppointmentLookupAdapter
from app.features.chat.infrastructure.adapters.chat_user_lookup_adapter import ChatUserLookupAdapter
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
from app.features.chat.application.get_chat_inbox_usecase import GetChatInboxUseCase
from app.features.consultations.application.create_consultation_usecase import CreateConsultationUseCase
from app.features.consultations.application.get_consultations_by_medical_record_usecase import GetConsultationsByMedicalRecordUseCase
from app.features.medical_record.application.create_medical_record_usecase import CreateMedicalRecordUseCase
from app.features.medical_record.application.get_patient_medical_record_usecase import GetPatientMedicalRecordUseCase
from app.features.medical_record.application.update_medical_record_usecase import UpdateMedicalRecordUseCase
from app.features.medical_record.application.search_medical_records_by_patient_name_usecase import SearchMedicalRecordsByPatientNameUseCase
from app.features.medical_record.application.evaluate_patient_risk_usecase import EvaluatePatientRiskUseCase
from app.features.medical_record.infrastructure.repositories.risk_prediction_repository import RiskPredictionRepository
from app.features.patient_diaries.application.create_patient_diary_usecase import CreatePatientDiaryUseCase
from app.features.patient_diaries.application.delete_patient_diary_usecase import DeletePatientDiaryUseCase
from app.features.patient_diaries.application.get_all_patient_diaries_usecase import GetAllPatientDiariesUseCase
from app.features.patient_diaries.application.get_diaries_by_medical_record_usecase import GetDiariesByMedicalRecordUseCase
from app.features.patient_diaries.application.get_patient_diary_by_id_usecase import GetPatientDiaryByIdUseCase
from app.features.patient_diaries.application.update_patient_diary_usecase import UpdatePatientDiaryUseCase
from app.features.users.application.auth.authenticate_user_usecase import AuthenticateUserUseCase
from app.features.users.application.doctor.register_doctor_usecase import RegisterDoctorUseCase
from app.features.users.application.doctor.create_receptionist_usecase import CreateReceptionistUseCase
from app.features.users.application.doctor.get_receptionists_by_doctor_usecase import GetReceptionistsByDoctorUseCase
from app.features.users.application.doctor.generate_invitation_code_usecase import GenerateInvitationCodeUseCase
from app.features.users.application.invitation.redeem_invitation_code_usecase import RedeemInvitationCodeUseCase
from app.features.users.application.patient.register_patient_usecase import RegisterPatientUseCase
from app.features.users.application.patient.get_patients_by_doctor_usecase import GetPatientsByDoctorUseCase
from app.features.users.application.patient.search_patients_by_name_usecase import SearchPatientsByNameUseCase
from app.features.users.application.patient.get_patient_dashboard_usecase import GetPatientDashboardUseCase
from app.features.users.application.user.create_user_usecase import CreateUserUseCase
from app.features.users.application.user.get_users_usecase import GetUsersUseCase
from app.features.users.application.user.get_user_usecase import GetUserUseCase
from app.features.users.application.user.update_user_usecase import UpdateUserUseCase
from app.features.users.application.user.delete_user_usecase import DeleteUserUseCase

from app.features.forums.infrastructure.repositories.forums_repository import ForumsRepository
from app.features.forums.infrastructure.controllers.profiles_controller import ProfilesController
from app.features.forums.infrastructure.controllers.groups_controller import GroupsController
from app.features.forums.infrastructure.controllers.posts_controller import PostsController
from app.features.forums.infrastructure.controllers.reports_controller import ReportsController
from app.features.forums.application.profiles.create_profile_usecase import CreateProfileUseCase
from app.features.forums.application.profiles.get_profile_usecase import GetProfileUseCase
from app.features.forums.application.groups.create_group_usecase import CreateGroupUseCase
from app.features.forums.application.groups.get_groups_usecase import GetGroupsUseCase
from app.features.forums.application.posts.create_post_usecase import CreatePostUseCase
from app.features.forums.application.posts.get_global_feed_usecase import GetGlobalFeedUseCase
from app.features.forums.application.posts.get_group_feed_usecase import GetGroupFeedUseCase
from app.features.forums.application.posts.add_comment_usecase import AddCommentUseCase
from app.features.forums.application.posts.get_comments_usecase import GetCommentsUseCase
from app.features.forums.application.reports.create_report_usecase import CreateReportUseCase

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
            "app.core.dependencies",
            "app.features.appointments.infrastructure.routes.appointment_router",
            "app.features.chat.infrastructure.routes.chat_router",
            "app.features.consultations.infrastructure.routes.consultation_router",
            "app.features.medical_record.infrastructure.routes.medical_record_router",
            "app.features.patient_diaries.infrastructure.routes.patient_diary_router",
            "app.features.users.infrastructure.routes.doctor_router",
            "app.features.users.infrastructure.routes.patient_router",
            "app.features.users.infrastructure.routes.user_router",
            "app.features.forums.infrastructure.routes.profiles_router",
            "app.features.forums.infrastructure.routes.groups_router",
            "app.features.forums.infrastructure.routes.posts_router",
            "app.features.forums.infrastructure.routes.reports_router",
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
    risk_prediction_repository = providers.Factory(RiskPredictionRepository, db=db)
    patient_diary_repository = providers.Factory(PatientDiaryRepository, db=db)
    doctor_repository = providers.Factory(DoctorRepository, db=db)
    invitation_code_repository = providers.Factory(InvitationCodeRepository, db=db)
    patient_repository = providers.Factory(PatientRepository, db=db)
    patient_info_adapter = providers.Factory(PatientInfoAdapter, patient_repository=patient_repository)
    receptionist_repository = providers.Factory(ReceptionistRepository, db=db)
    user_repository = providers.Factory(UserRepository, db=db)
    forums_repository = providers.Factory(ForumsRepository, db=db)

    # Use Cases
    create_appointment_use_case = providers.Factory(CreateAppointmentUseCase, appointment_repo=appointment_repository, patient_repo=patient_repository, doctor_repo=doctor_repository)
    delete_appointment_use_case = providers.Factory(DeleteAppointmentUseCase, appointment_repo=appointment_repository)
    get_appointments_by_doctor_use_case = providers.Factory(GetAppointmentsByDoctorUseCase, appointment_repo=appointment_repository)
    get_appointments_by_patient_use_case = providers.Factory(GetAppointmentsByPatientUseCase, appointment_repo=appointment_repository)
    get_appointment_use_case = providers.Factory(GetAppointmentUseCase, appointment_repo=appointment_repository)
    update_appointment_use_case = providers.Factory(UpdateAppointmentUseCase, appointment_repo=appointment_repository)
    get_history_use_case = providers.Factory(GetHistoryUseCase, chat_repository=chat_repository)
    save_message_use_case = providers.Factory(SaveMessageUseCase, chat_repository=chat_repository)
    chat_user_lookup_adapter = providers.Factory(ChatUserLookupAdapter, user_repository=user_repository)
    get_chat_inbox_use_case = providers.Factory(GetChatInboxUseCase, chat_repository=chat_repository, user_lookup=chat_user_lookup_adapter)
    create_consultation_use_case = providers.Factory(CreateConsultationUseCase, consultation_repo=consultation_repository)
    get_consultations_by_medical_record_use_case = providers.Factory(GetConsultationsByMedicalRecordUseCase, consultation_repo=consultation_repository)
    create_medical_record_use_case = providers.Factory(CreateMedicalRecordUseCase, medical_record_repository=medical_record_repository, patient_repository=patient_info_adapter)
    get_patient_medical_record_use_case = providers.Factory(GetPatientMedicalRecordUseCase, medical_record_repository=medical_record_repository, patient_repository=patient_info_adapter, risk_prediction_repository=risk_prediction_repository)
    evaluate_patient_risk_use_case = providers.Factory(EvaluatePatientRiskUseCase, medical_record_repository=medical_record_repository, patient_repository=patient_info_adapter, ml_prediction_service=ml_prediction_service, risk_prediction_repository=risk_prediction_repository)
    update_medical_record_use_case = providers.Factory(UpdateMedicalRecordUseCase, medical_record_repository=medical_record_repository)
    search_medical_records_by_patient_name_use_case = providers.Factory(SearchMedicalRecordsByPatientNameUseCase, medical_record_repository=medical_record_repository, patient_repository=patient_info_adapter)
    create_patient_diary_use_case = providers.Factory(CreatePatientDiaryUseCase, repository=patient_diary_repository)
    delete_patient_diary_use_case = providers.Factory(DeletePatientDiaryUseCase, repository=patient_diary_repository)
    get_all_patient_diaries_use_case = providers.Factory(GetAllPatientDiariesUseCase, repository=patient_diary_repository)
    get_diaries_by_medical_record_use_case = providers.Factory(GetDiariesByMedicalRecordUseCase, repository=patient_diary_repository)
    get_patient_diary_by_id_use_case = providers.Factory(GetPatientDiaryByIdUseCase, repository=patient_diary_repository)
    update_patient_diary_use_case = providers.Factory(UpdatePatientDiaryUseCase, repository=patient_diary_repository)
    
    appointment_lookup_adapter = providers.Factory(AppointmentLookupAdapter, appointment_repository=appointment_repository)
    medical_record_lookup_adapter = providers.Factory(MedicalRecordLookupAdapter, medical_record_repository=medical_record_repository)
    
    authenticate_user_use_case = providers.Factory(AuthenticateUserUseCase, user_repository=user_repository, patient_repository=patient_repository, doctor_repository=doctor_repository, receptionist_repository=receptionist_repository, medical_record_lookup=medical_record_lookup_adapter)
    register_doctor_use_case = providers.Factory(RegisterDoctorUseCase, user_repository=user_repository, doctor_repository=doctor_repository)
    create_receptionist_use_case = providers.Factory(CreateReceptionistUseCase, user_repository=user_repository, doctor_repository=doctor_repository, receptionist_repository=receptionist_repository)
    get_receptionists_by_doctor_use_case = providers.Factory(GetReceptionistsByDoctorUseCase, doctor_repository=doctor_repository, receptionist_repository=receptionist_repository)
    generate_invitation_code_use_case = providers.Factory(GenerateInvitationCodeUseCase, doctor_repository=doctor_repository, invitation_code_repository=invitation_code_repository)
    redeem_invitation_code_use_case = providers.Factory(RedeemInvitationCodeUseCase, patient_repository=patient_repository, invitation_code_repository=invitation_code_repository)
    register_patient_use_case = providers.Factory(RegisterPatientUseCase, user_repository=user_repository, patient_repository=patient_repository)
    get_patients_by_doctor_use_case = providers.Factory(GetPatientsByDoctorUseCase, patient_repository=patient_repository)
    search_patients_by_name_use_case = providers.Factory(SearchPatientsByNameUseCase, patient_repository=patient_repository)
    get_patient_dashboard_use_case = providers.Factory(GetPatientDashboardUseCase, patient_repository=patient_repository, user_repository=user_repository, doctor_repository=doctor_repository, appointment_lookup=appointment_lookup_adapter, medical_record_lookup=medical_record_lookup_adapter)
    create_user_use_case = providers.Factory(CreateUserUseCase, user_repository=user_repository)
    get_users_use_case = providers.Factory(GetUsersUseCase, user_repository=user_repository)
    get_user_use_case = providers.Factory(GetUserUseCase, user_repository=user_repository)
    update_user_use_case = providers.Factory(UpdateUserUseCase, user_repository=user_repository)
    delete_user_use_case = providers.Factory(DeleteUserUseCase, user_repository=user_repository)
    create_profile_use_case = providers.Factory(CreateProfileUseCase, forums_repo=forums_repository)
    get_profile_use_case = providers.Factory(GetProfileUseCase, forums_repo=forums_repository)
    create_group_use_case = providers.Factory(CreateGroupUseCase, forums_repo=forums_repository)
    get_groups_use_case = providers.Factory(GetGroupsUseCase, forums_repo=forums_repository)
    create_post_use_case = providers.Factory(CreatePostUseCase, forums_repo=forums_repository)
    get_global_feed_use_case = providers.Factory(GetGlobalFeedUseCase, forums_repo=forums_repository)
    get_group_feed_use_case = providers.Factory(GetGroupFeedUseCase, forums_repo=forums_repository)
    add_comment_use_case = providers.Factory(AddCommentUseCase, forums_repo=forums_repository)
    get_comments_use_case = providers.Factory(GetCommentsUseCase, forums_repo=forums_repository)
    create_report_use_case = providers.Factory(CreateReportUseCase, forums_repo=forums_repository)

    # Controllers
    appointment_controller = providers.Factory(AppointmentController, create_appointment_use_case, get_appointment_use_case, get_appointments_by_patient_use_case, get_appointments_by_doctor_use_case, update_appointment_use_case, delete_appointment_use_case)
    consultation_controller = providers.Factory(ConsultationController, create_consultation_use_case, get_consultations_by_medical_record_use_case)
    medical_record_controller = providers.Factory(MedicalRecordController, create_medical_record_use_case, get_patient_medical_record_use_case, update_medical_record_use_case, search_medical_records_by_patient_name_use_case, evaluate_patient_risk_use_case)
    patient_diary_controller = providers.Factory(PatientDiaryController, create_patient_diary_use_case, get_all_patient_diaries_use_case, get_diaries_by_medical_record_use_case, get_patient_diary_by_id_use_case, update_patient_diary_use_case, delete_patient_diary_use_case)
    chat_controller = providers.Factory(ChatController, get_history_use_case, save_message_use_case, get_chat_inbox_use_case)
    user_controller = providers.Factory(UserController, get_users_use_case, get_user_use_case, update_user_use_case, delete_user_use_case, create_user_use_case)
    auth_controller = providers.Factory(AuthController, authenticate_user_use_case)
    patient_controller = providers.Factory(PatientController, get_patient_dashboard_use_case, register_patient_use_case, redeem_invitation_code_use_case)
    doctor_controller = providers.Factory(DoctorController, create_receptionist_use_case, get_receptionists_by_doctor_use_case, register_doctor_use_case, get_patients_by_doctor_use_case, generate_invitation_code_use_case, search_patients_by_name_use_case)
    profiles_controller = providers.Factory(ProfilesController, create_profile_use_case, get_profile_use_case)
    groups_controller = providers.Factory(GroupsController, create_group_use_case, get_groups_use_case)
    posts_controller = providers.Factory(PostsController, create_post_use_case, get_global_feed_use_case, get_group_feed_use_case, add_comment_use_case, get_comments_use_case)
    reports_controller = providers.Factory(ReportsController, create_report_use_case)
