"""Composition root del servicio transaccional — slice de 7 features:
appointments, consultations, medical_record, patient_diaries, forums, chat,
notifications.

Los adapters que en el monolito cruzaban a `users`/`subscriptions` ahora leen la
DB compartida vía read-models (reciben `db=db`), no repos de otro servicio ni HTTP.
Los adapters internos (medical_record<->patient_diaries/forums) quedan en-proceso.
"""
from dependency_injector import containers, providers

from salud_prenatal_shared_core.database import get_session_factory

# Repositorios propios (features de este servicio)
from app.appointments.infrastructure.repositories.appointment_repository import AppointmentRepository
from app.chat.infrastructure.repositories.chat_repository import ChatRepository
from app.consultations.infrastructure.repositories.consultation_repository import ConsultationRepository
from app.medical_record.infrastructure.repositories.medical_record_repository import MedicalRecordRepository
from app.medical_record.infrastructure.repositories.risk_prediction_repository import RiskPredictionRepository
from app.patient_diaries.infrastructure.repositories.patient_diary_repository import PatientDiaryRepository
from app.patient_diaries.infrastructure.repositories.diary_symptom_extraction_repository import DiarySymptomExtractionRepository
from app.forums.infrastructure.repositories.forums_repository import ForumsRepository
from app.notifications.infrastructure.repositories.device_token_repository import DeviceTokenRepository

# Read-repo sobre la DB compartida (solo lectura de `users`)
from app.readmodels.users_read_repository import UsersReadRepository

# Adapters
from app.medical_record.infrastructure.adapters.ml_prediction_adapter import MlPredictionServiceAdapter
from app.patient_diaries.infrastructure.adapters.nlp_symptom_adapter import NlpSymptomAdapter
from app.medical_record.infrastructure.adapters.patient_info_adapter import PatientInfoAdapter
from app.medical_record.infrastructure.adapters.social_cluster_adapter import SocialClusterAdapter
from app.medical_record.infrastructure.adapters.latest_diary_adapter import LatestDiaryAdapter
from app.medical_record.infrastructure.adapters.diary_symptom_summary_adapter import DiarySymptomSummaryAdapter
from app.forums.infrastructure.adapters.patient_cluster_adapter import PatientClusterAdapter
from app.forums.infrastructure.adapters.ad_eligibility_adapter import AdEligibilityAdapter
from app.chat.infrastructure.adapters.chat_contacts_lookup_adapter import ChatContactsLookupAdapter
from app.chat.infrastructure.adapters.chat_user_lookup_adapter import ChatUserLookupAdapter
from app.appointments.infrastructure.adapters.patient_doctor_lookup_adapter import PatientLookupAdapter, DoctorLookupAdapter

# Use cases — appointments
from app.appointments.application.create_appointment_usecase import CreateAppointmentUseCase
from app.appointments.application.delete_appointment_usecase import DeleteAppointmentUseCase
from app.appointments.application.get_appointments_by_doctor_usecase import GetAppointmentsByDoctorUseCase
from app.appointments.application.get_appointments_by_patient_usecase import GetAppointmentsByPatientUseCase
from app.appointments.application.get_appointment_usecase import GetAppointmentUseCase
from app.appointments.application.update_appointment_usecase import UpdateAppointmentUseCase
# Use cases — chat
from app.chat.application.get_history_usecase import GetHistoryUseCase
from app.chat.application.save_message_usecase import SaveMessageUseCase
from app.chat.application.get_chat_inbox_usecase import GetChatInboxUseCase
from app.chat.application.get_chat_contacts_usecase import GetChatContactsUseCase
# Use cases — consultations
from app.consultations.application.create_consultation_usecase import CreateConsultationUseCase
from app.consultations.application.get_consultations_by_medical_record_usecase import GetConsultationsByMedicalRecordUseCase
# Use cases — medical_record
from app.medical_record.application.create_medical_record_usecase import CreateMedicalRecordUseCase
from app.medical_record.application.get_patient_medical_record_usecase import GetPatientMedicalRecordUseCase
from app.medical_record.application.update_medical_record_usecase import UpdateMedicalRecordUseCase
from app.medical_record.application.search_medical_records_by_patient_name_usecase import SearchMedicalRecordsByPatientNameUseCase
from app.medical_record.application.evaluate_patient_risk_usecase import EvaluatePatientRiskUseCase
# Use cases — patient_diaries
from app.patient_diaries.application.create_patient_diary_usecase import CreatePatientDiaryUseCase
from app.patient_diaries.application.delete_patient_diary_usecase import DeletePatientDiaryUseCase
from app.patient_diaries.application.get_all_patient_diaries_usecase import GetAllPatientDiariesUseCase
from app.patient_diaries.application.get_diaries_by_medical_record_usecase import GetDiariesByMedicalRecordUseCase
from app.patient_diaries.application.get_patient_diary_by_id_usecase import GetPatientDiaryByIdUseCase
from app.patient_diaries.application.update_patient_diary_usecase import UpdatePatientDiaryUseCase
from app.patient_diaries.application.get_diary_symptoms_usecase import GetDiarySymptomsUseCase
from app.patient_diaries.application.get_medical_record_symptom_history_usecase import GetMedicalRecordSymptomHistoryUseCase
# Use cases — forums
from app.forums.application.profiles.create_profile_usecase import CreateProfileUseCase
from app.forums.application.profiles.get_profile_usecase import GetProfileUseCase
from app.forums.application.profiles.update_profile_usecase import UpdateProfileUseCase
from app.forums.application.profiles.get_profile_timeline_usecase import GetProfileTimelineUseCase
from app.forums.application.groups.create_group_usecase import CreateGroupUseCase
from app.forums.application.groups.get_groups_usecase import GetGroupsUseCase
from app.forums.application.groups.get_recommended_groups_usecase import GetRecommendedGroupsUseCase
from app.forums.application.posts.create_post_usecase import CreatePostUseCase
from app.forums.application.posts.get_global_feed_usecase import GetGlobalFeedUseCase
from app.forums.application.posts.get_group_feed_usecase import GetGroupFeedUseCase
from app.forums.application.posts.get_recommended_feed_usecase import GetRecommendedFeedUseCase
from app.forums.application.posts.add_comment_usecase import AddCommentUseCase
from app.forums.application.posts.get_comments_usecase import GetCommentsUseCase
from app.forums.application.reports.create_report_usecase import CreateReportUseCase
# Use cases — notifications
from app.notifications.application.use_cases.register_device_token_use_case import RegisterDeviceTokenUseCase
from app.notifications.application.use_cases.unregister_device_token_use_case import UnregisterDeviceTokenUseCase

# Controllers
from app.appointments.infrastructure.controllers.appointment_controller import AppointmentController
from app.consultations.infrastructure.controllers.consultation_controller import ConsultationController
from app.medical_record.infrastructure.controllers.medical_record_controller import MedicalRecordController
from app.patient_diaries.infrastructure.controllers.patient_diary_controller import PatientDiaryController
from app.chat.infrastructure.controllers.chat_controller import ChatController
from app.notifications.infrastructure.controllers.notification_controller import NotificationController
from app.forums.infrastructure.controllers.profiles_controller import ProfilesController
from app.forums.infrastructure.controllers.groups_controller import GroupsController
from app.forums.infrastructure.controllers.posts_controller import PostsController
from app.forums.infrastructure.controllers.reports_controller import ReportsController


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "main",
            "app.appointments.infrastructure.routes.appointment_router",
            "app.chat.infrastructure.routes.chat_router",
            "app.consultations.infrastructure.routes.consultation_router",
            "app.medical_record.infrastructure.routes.medical_record_router",
            "app.patient_diaries.infrastructure.routes.patient_diary_router",
            "app.forums.infrastructure.routes.profiles_router",
            "app.forums.infrastructure.routes.groups_router",
            "app.forums.infrastructure.routes.posts_router",
            "app.forums.infrastructure.routes.reports_router",
            "app.notifications.infrastructure.routes.notification_router",
        ]
    )

    db = providers.ContextLocalSingleton(lambda: get_session_factory()())

    # Adapters externos (HTTP a ML/NLP) — sin cambios
    ml_prediction_service = providers.Factory(MlPredictionServiceAdapter)
    symptom_extraction_port = providers.Factory(NlpSymptomAdapter)

    # Repositorios propios
    appointment_repository = providers.Factory(AppointmentRepository, db=db)
    chat_repository = providers.Factory(ChatRepository, db=db)
    consultation_repository = providers.Factory(ConsultationRepository, db=db)
    medical_record_repository = providers.Factory(MedicalRecordRepository, db=db)
    risk_prediction_repository = providers.Factory(RiskPredictionRepository, db=db)
    patient_diary_repository = providers.Factory(PatientDiaryRepository, db=db)
    diary_symptom_repository = providers.Factory(DiarySymptomExtractionRepository, db=db)
    forums_repository = providers.Factory(ForumsRepository, db=db)
    device_token_repository = providers.Factory(DeviceTokenRepository, db=db)

    # Lectura de `users` en la DB compartida (read-model)
    users_read_repository = providers.Factory(UsersReadRepository, db=db)

    # Adapters cross-servicio -> read-models (db). In-proceso -> repos propios.
    patient_info_adapter = providers.Factory(PatientInfoAdapter, db=db)
    latest_diary_adapter = providers.Factory(LatestDiaryAdapter, patient_diary_repository=patient_diary_repository)
    diary_symptom_summary_adapter = providers.Factory(DiarySymptomSummaryAdapter, diary_symptom_repository=diary_symptom_repository)
    social_cluster_adapter = providers.Factory(SocialClusterAdapter, forums_repository=forums_repository)
    patient_cluster_adapter = providers.Factory(PatientClusterAdapter, db=db, medical_record_repository=medical_record_repository, risk_prediction_repository=risk_prediction_repository)
    ad_eligibility_adapter = providers.Factory(AdEligibilityAdapter, db=db)
    chat_user_lookup_adapter = providers.Factory(ChatUserLookupAdapter, db=db)
    chat_contacts_lookup_adapter = providers.Factory(ChatContactsLookupAdapter, db=db)
    appointment_patient_lookup = providers.Factory(PatientLookupAdapter, db=db)
    appointment_doctor_lookup = providers.Factory(DoctorLookupAdapter, db=db)

    # Use cases — appointments
    create_appointment_use_case = providers.Factory(CreateAppointmentUseCase, appointment_repo=appointment_repository, patient_repo=appointment_patient_lookup, doctor_repo=appointment_doctor_lookup)
    delete_appointment_use_case = providers.Factory(DeleteAppointmentUseCase, appointment_repo=appointment_repository)
    get_appointments_by_doctor_use_case = providers.Factory(GetAppointmentsByDoctorUseCase, appointment_repo=appointment_repository)
    get_appointments_by_patient_use_case = providers.Factory(GetAppointmentsByPatientUseCase, appointment_repo=appointment_repository)
    get_appointment_use_case = providers.Factory(GetAppointmentUseCase, appointment_repo=appointment_repository)
    update_appointment_use_case = providers.Factory(UpdateAppointmentUseCase, appointment_repo=appointment_repository)

    # Use cases — chat
    get_history_use_case = providers.Factory(GetHistoryUseCase, chat_repository=chat_repository)
    save_message_use_case = providers.Factory(SaveMessageUseCase, chat_repository=chat_repository)
    get_chat_inbox_use_case = providers.Factory(GetChatInboxUseCase, chat_repository=chat_repository, user_lookup=chat_user_lookup_adapter)
    get_chat_contacts_use_case = providers.Factory(GetChatContactsUseCase, contacts_lookup=chat_contacts_lookup_adapter)

    # Use cases — consultations
    create_consultation_use_case = providers.Factory(CreateConsultationUseCase, consultation_repo=consultation_repository)
    get_consultations_by_medical_record_use_case = providers.Factory(GetConsultationsByMedicalRecordUseCase, consultation_repo=consultation_repository)

    # Use cases — medical_record
    create_medical_record_use_case = providers.Factory(CreateMedicalRecordUseCase, medical_record_repository=medical_record_repository, patient_repository=patient_info_adapter)
    get_patient_medical_record_use_case = providers.Factory(GetPatientMedicalRecordUseCase, medical_record_repository=medical_record_repository, patient_repository=patient_info_adapter, risk_prediction_repository=risk_prediction_repository, latest_diary_repository=latest_diary_adapter, symptom_summary_port=diary_symptom_summary_adapter)
    evaluate_patient_risk_use_case = providers.Factory(EvaluatePatientRiskUseCase, medical_record_repository=medical_record_repository, patient_repository=patient_info_adapter, ml_prediction_service=ml_prediction_service, risk_prediction_repository=risk_prediction_repository, social_cluster_port=social_cluster_adapter, latest_diary_repository=latest_diary_adapter)
    update_medical_record_use_case = providers.Factory(UpdateMedicalRecordUseCase, medical_record_repository=medical_record_repository)
    search_medical_records_by_patient_name_use_case = providers.Factory(SearchMedicalRecordsByPatientNameUseCase, medical_record_repository=medical_record_repository, patient_repository=patient_info_adapter)

    # Use cases — patient_diaries
    create_patient_diary_use_case = providers.Factory(CreatePatientDiaryUseCase, repository=patient_diary_repository, symptom_extraction_port=symptom_extraction_port, symptom_repository=diary_symptom_repository)
    delete_patient_diary_use_case = providers.Factory(DeletePatientDiaryUseCase, repository=patient_diary_repository)
    get_all_patient_diaries_use_case = providers.Factory(GetAllPatientDiariesUseCase, repository=patient_diary_repository)
    get_diaries_by_medical_record_use_case = providers.Factory(GetDiariesByMedicalRecordUseCase, repository=patient_diary_repository)
    get_patient_diary_by_id_use_case = providers.Factory(GetPatientDiaryByIdUseCase, repository=patient_diary_repository)
    update_patient_diary_use_case = providers.Factory(UpdatePatientDiaryUseCase, repository=patient_diary_repository)
    get_diary_symptoms_use_case = providers.Factory(GetDiarySymptomsUseCase, symptom_repository=diary_symptom_repository)
    get_medical_record_symptom_history_use_case = providers.Factory(GetMedicalRecordSymptomHistoryUseCase, symptom_repository=diary_symptom_repository)

    # Use cases — forums
    create_profile_use_case = providers.Factory(CreateProfileUseCase, forums_repo=forums_repository, cluster_lookup=patient_cluster_adapter)
    get_profile_use_case = providers.Factory(GetProfileUseCase, forums_repo=forums_repository)
    update_profile_use_case = providers.Factory(UpdateProfileUseCase, forums_repo=forums_repository)
    get_profile_timeline_use_case = providers.Factory(GetProfileTimelineUseCase, forums_repo=forums_repository)
    create_group_use_case = providers.Factory(CreateGroupUseCase, forums_repo=forums_repository)
    get_groups_use_case = providers.Factory(GetGroupsUseCase, forums_repo=forums_repository)
    get_recommended_groups_use_case = providers.Factory(GetRecommendedGroupsUseCase, forums_repo=forums_repository)
    create_post_use_case = providers.Factory(CreatePostUseCase, forums_repo=forums_repository, ad_eligibility=ad_eligibility_adapter)
    get_global_feed_use_case = providers.Factory(GetGlobalFeedUseCase, forums_repo=forums_repository)
    get_recommended_feed_use_case = providers.Factory(GetRecommendedFeedUseCase, forums_repo=forums_repository)
    get_group_feed_use_case = providers.Factory(GetGroupFeedUseCase, forums_repo=forums_repository)
    add_comment_use_case = providers.Factory(AddCommentUseCase, forums_repo=forums_repository)
    get_comments_use_case = providers.Factory(GetCommentsUseCase, forums_repo=forums_repository)
    create_report_use_case = providers.Factory(CreateReportUseCase, forums_repo=forums_repository)

    # Use cases — notifications
    register_device_token_use_case = providers.Factory(RegisterDeviceTokenUseCase, device_token_repository=device_token_repository)
    unregister_device_token_use_case = providers.Factory(UnregisterDeviceTokenUseCase, device_token_repository=device_token_repository)

    # Controllers
    appointment_controller = providers.Factory(AppointmentController, create_appointment_use_case, get_appointment_use_case, get_appointments_by_patient_use_case, get_appointments_by_doctor_use_case, update_appointment_use_case, delete_appointment_use_case)
    consultation_controller = providers.Factory(ConsultationController, create_consultation_use_case, get_consultations_by_medical_record_use_case)
    medical_record_controller = providers.Factory(MedicalRecordController, create_medical_record_use_case, get_patient_medical_record_use_case, update_medical_record_use_case, search_medical_records_by_patient_name_use_case, evaluate_patient_risk_use_case)
    patient_diary_controller = providers.Factory(PatientDiaryController, create_patient_diary_use_case, get_all_patient_diaries_use_case, get_diaries_by_medical_record_use_case, get_patient_diary_by_id_use_case, update_patient_diary_use_case, delete_patient_diary_use_case, get_diary_symptoms_use_case, get_medical_record_symptom_history_use_case)
    chat_controller = providers.Factory(ChatController, get_history_use_case, save_message_use_case, get_chat_inbox_use_case, get_chat_contacts_use_case, device_token_repository, users_read_repository)
    notification_controller = providers.Factory(NotificationController, register_device_token_use_case, unregister_device_token_use_case)
    profiles_controller = providers.Factory(ProfilesController, create_profile_use_case, get_profile_use_case, update_profile_use_case, get_profile_timeline_use_case)
    groups_controller = providers.Factory(GroupsController, create_group_use_case, get_groups_use_case, get_recommended_groups_use_case)
    posts_controller = providers.Factory(PostsController, create_post_use_case, get_global_feed_use_case, get_group_feed_use_case, add_comment_use_case, get_comments_use_case, get_recommended_feed_use_case)
    reports_controller = providers.Factory(ReportsController, create_report_use_case)
