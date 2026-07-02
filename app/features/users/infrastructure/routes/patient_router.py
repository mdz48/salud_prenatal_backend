from dependency_injector.wiring import inject, Provide
from app.core.containers import Container
from fastapi import APIRouter, Depends, HTTPException, status
from app.features.users.infrastructure.schemas.patient_schema import PatientRegistration, PatientResponse, PatientDashboardResponse
from app.features.users.infrastructure.schemas.invitation_code_schema import RedeemCodeRequest


from app.features.users.application.patient_usecases import GetPatientDashboardUseCase, RegisterPatientUseCase
from app.features.users.application.invitation_usecases import RedeemInvitationCodeUseCase

router = APIRouter(prefix="/patients", tags=["Patients"])






@router.get("/{patient_id}/dashboard", response_model=PatientDashboardResponse, status_code=status.HTTP_200_OK)
@inject
def get_patient_dashboard(patient_id: int, usecase: GetPatientDashboardUseCase = Depends(Provide[Container.get_patient_dashboard_use_case])):
    try:
        return usecase.execute(patient_id=patient_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while fetching the dashboard.")

@router.post("/register", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
@inject
def register_patient(data: PatientRegistration, usecase: RegisterPatientUseCase = Depends(Provide[Container.register_patient_use_case])):
    try:
        return usecase.execute(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while registering the patient.")

@router.post("/{patient_id}/redeem-code", response_model=PatientResponse, status_code=status.HTTP_200_OK)
@inject
def redeem_code(patient_id: int, data: RedeemCodeRequest, usecase: RedeemInvitationCodeUseCase = Depends(Provide[Container.redeem_invitation_code_use_case])):
    try:
        return usecase.execute(patient_id=patient_id, code=data.code)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while redeeming the code.")
