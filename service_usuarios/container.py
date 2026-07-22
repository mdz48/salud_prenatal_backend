"""Composition root del servicio usuarios — slice de la feature users (sin login)."""
from dependency_injector import containers, providers

from salud_prenatal_shared_core.database import get_session_factory

from app.users.infrastructure.repositories.user_repository import UserRepository
from app.users.infrastructure.repositories.patient_repository import PatientRepository
from app.users.infrastructure.repositories.doctor_repository import DoctorRepository
from app.users.infrastructure.repositories.receptionist_repository import ReceptionistRepository
from app.users.infrastructure.repositories.invitation_code_repository import InvitationCodeRepository
from app.users.infrastructure.repositories.unlink_request_repository import UnlinkRequestRepository

from app.users.infrastructure.adapters.medical_record_lookup_adapter import MedicalRecordLookupAdapter
from app.users.infrastructure.adapters.appointment_lookup_adapter import AppointmentLookupAdapter
from app.users.infrastructure.adapters.patient_linked_notifier_adapter import PatientLinkedNotifierAdapter
from app.users.infrastructure.adapters.risk_cluster_filter_adapter import RiskClusterFilterAdapter

from app.users.application.user.create_user_usecase import CreateUserUseCase
from app.users.application.user.get_users_usecase import GetUsersUseCase
from app.users.application.user.get_user_usecase import GetUserUseCase
from app.users.application.user.update_user_usecase import UpdateUserUseCase
from app.users.application.user.delete_user_usecase import DeleteUserUseCase
from app.users.application.patient.register_patient_usecase import RegisterPatientUseCase
from app.users.application.patient.get_patients_by_doctor_usecase import GetPatientsByDoctorUseCase
from app.users.application.patient.search_patients_by_name_usecase import SearchPatientsByNameUseCase
from app.users.application.patient.search_patient_directory_usecase import SearchPatientDirectoryUseCase
from app.users.application.patient.get_patient_dashboard_usecase import GetPatientDashboardUseCase
from app.users.application.patient.unlink_patient_usecase import UnlinkPatientUseCase
from app.users.application.patient.create_unlink_request_usecase import CreateUnlinkRequestUseCase
from app.users.application.patient.list_patient_unlink_requests_usecase import ListPatientUnlinkRequestsUseCase
from app.users.application.patient.cancel_unlink_request_usecase import CancelUnlinkRequestUseCase
from app.users.application.doctor.register_doctor_usecase import RegisterDoctorUseCase
from app.users.application.doctor.create_receptionist_usecase import CreateReceptionistUseCase
from app.users.application.doctor.get_receptionists_by_doctor_usecase import GetReceptionistsByDoctorUseCase
from app.users.application.doctor.generate_invitation_code_usecase import GenerateInvitationCodeUseCase
from app.users.application.doctor.get_doctor_by_id_usecase import GetDoctorByIdUseCase
from app.users.application.doctor.get_doctor_dashboard_usecase import GetDoctorDashboardUseCase
from app.users.application.doctor.get_receptionist_by_id_usecase import GetReceptionistByIdUseCase
from app.users.application.doctor.get_receptionist_dashboard_usecase import GetReceptionistDashboardUseCase
from app.users.application.doctor.list_unlink_requests_usecase import ListUnlinkRequestsUseCase
from app.users.application.doctor.resolve_unlink_request_usecase import ResolveUnlinkRequestUseCase
from app.users.application.invitation.redeem_invitation_code_usecase import RedeemInvitationCodeUseCase

from app.users.infrastructure.controllers.user_controller import UserController
from app.users.infrastructure.controllers.patient_controller import PatientController
from app.users.infrastructure.controllers.doctor_controller import DoctorController


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "main",
            "app.users.infrastructure.routes.user_router",
            "app.users.infrastructure.routes.doctor_router",
            "app.users.infrastructure.routes.patient_router",
        ]
    )

    db = providers.ContextLocalSingleton(lambda: get_session_factory()())

    # Repositories
    user_repository = providers.Factory(UserRepository, db=db)
    patient_repository = providers.Factory(PatientRepository, db=db)
    doctor_repository = providers.Factory(DoctorRepository, db=db)
    receptionist_repository = providers.Factory(ReceptionistRepository, db=db)
    invitation_code_repository = providers.Factory(InvitationCodeRepository, db=db)
    unlink_request_repository = providers.Factory(UnlinkRequestRepository, db=db)

    # Lookups cross-servicio: leen la DB compartida vía read-models (no HTTP).
    medical_record_lookup_adapter = providers.Factory(MedicalRecordLookupAdapter, db=db)
    appointment_lookup_adapter = providers.Factory(AppointmentLookupAdapter, db=db)
    patient_linked_notifier_adapter = providers.Factory(PatientLinkedNotifierAdapter)
    risk_cluster_filter_adapter = providers.Factory(RiskClusterFilterAdapter, db=db)

    # Use cases
    create_user_use_case = providers.Factory(CreateUserUseCase, user_repository=user_repository)
    get_users_use_case = providers.Factory(GetUsersUseCase, user_repository=user_repository)
    get_user_use_case = providers.Factory(GetUserUseCase, user_repository=user_repository)
    update_user_use_case = providers.Factory(UpdateUserUseCase, user_repository=user_repository)
    delete_user_use_case = providers.Factory(DeleteUserUseCase, user_repository=user_repository)

    register_patient_use_case = providers.Factory(RegisterPatientUseCase, user_repository=user_repository, patient_repository=patient_repository)
    get_patients_by_doctor_use_case = providers.Factory(GetPatientsByDoctorUseCase, patient_repository=patient_repository, medical_record_lookup=medical_record_lookup_adapter)
    search_patients_by_name_use_case = providers.Factory(SearchPatientsByNameUseCase, patient_repository=patient_repository)
    search_patient_directory_use_case = providers.Factory(SearchPatientDirectoryUseCase, patient_repository=patient_repository, clinical_filter_port=risk_cluster_filter_adapter)
    get_patient_dashboard_use_case = providers.Factory(GetPatientDashboardUseCase, patient_repository=patient_repository, user_repository=user_repository, doctor_repository=doctor_repository, appointment_lookup=appointment_lookup_adapter, medical_record_lookup=medical_record_lookup_adapter)
    unlink_patient_use_case = providers.Factory(UnlinkPatientUseCase, patient_repository=patient_repository, appointment_lookup=appointment_lookup_adapter)
    create_unlink_request_use_case = providers.Factory(CreateUnlinkRequestUseCase, patient_repository=patient_repository, unlink_request_repository=unlink_request_repository)
    list_patient_unlink_requests_use_case = providers.Factory(ListPatientUnlinkRequestsUseCase, unlink_request_repository=unlink_request_repository)
    cancel_unlink_request_use_case = providers.Factory(CancelUnlinkRequestUseCase, unlink_request_repository=unlink_request_repository)

    register_doctor_use_case = providers.Factory(RegisterDoctorUseCase, user_repository=user_repository, doctor_repository=doctor_repository)
    create_receptionist_use_case = providers.Factory(CreateReceptionistUseCase, user_repository=user_repository, doctor_repository=doctor_repository, receptionist_repository=receptionist_repository)
    get_receptionists_by_doctor_use_case = providers.Factory(GetReceptionistsByDoctorUseCase, doctor_repository=doctor_repository, receptionist_repository=receptionist_repository)
    generate_invitation_code_use_case = providers.Factory(GenerateInvitationCodeUseCase, doctor_repository=doctor_repository, invitation_code_repository=invitation_code_repository)
    get_doctor_by_id_use_case = providers.Factory(GetDoctorByIdUseCase, doctor_repository=doctor_repository, user_repository=user_repository)
    get_doctor_dashboard_use_case = providers.Factory(GetDoctorDashboardUseCase, doctor_repository=doctor_repository, user_repository=user_repository, patient_repository=patient_repository, receptionist_repository=receptionist_repository, appointment_lookup=appointment_lookup_adapter)
    get_receptionist_by_id_use_case = providers.Factory(GetReceptionistByIdUseCase, receptionist_repository=receptionist_repository, user_repository=user_repository)
    get_receptionist_dashboard_use_case = providers.Factory(GetReceptionistDashboardUseCase, receptionist_repository=receptionist_repository, user_repository=user_repository, patient_repository=patient_repository, appointment_lookup=appointment_lookup_adapter)

    redeem_invitation_code_use_case = providers.Factory(RedeemInvitationCodeUseCase, patient_repository=patient_repository, invitation_code_repository=invitation_code_repository, patient_linked_notifier=patient_linked_notifier_adapter)

    list_unlink_requests_use_case = providers.Factory(ListUnlinkRequestsUseCase, unlink_request_repository=unlink_request_repository)
    resolve_unlink_request_use_case = providers.Factory(ResolveUnlinkRequestUseCase, unlink_request_repository=unlink_request_repository, unlink_patient_use_case=unlink_patient_use_case)

    # Controllers
    user_controller = providers.Factory(UserController, get_users_use_case, get_user_use_case, update_user_use_case, delete_user_use_case, create_user_use_case)
    patient_controller = providers.Factory(PatientController, get_patient_dashboard_use_case, register_patient_use_case, redeem_invitation_code_use_case, create_unlink_request_use_case, list_patient_unlink_requests_use_case, cancel_unlink_request_use_case)
    doctor_controller = providers.Factory(DoctorController, create_receptionist_use_case, get_receptionists_by_doctor_use_case, register_doctor_use_case, get_patients_by_doctor_use_case, generate_invitation_code_use_case, search_patients_by_name_use_case, get_doctor_by_id_use_case, get_doctor_dashboard_use_case, get_receptionist_by_id_use_case, get_receptionist_dashboard_use_case, search_patient_directory_use_case, list_unlink_requests_use_case, resolve_unlink_request_use_case)
