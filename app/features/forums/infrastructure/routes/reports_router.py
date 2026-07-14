from dependency_injector.wiring import inject, Provide
from app.core.containers import Container
from app.core.dependencies import get_current_user
from fastapi import APIRouter, Depends, status
from app.features.forums.infrastructure.schemas.forums_schemas import ReportCreate, ReportResponse
from app.features.forums.infrastructure.controllers.reports_controller import ReportsController
from app.features.users.domain.user_entity import UserEntity

router = APIRouter(prefix="/forums", tags=["Forums - Reports"])

@router.post("/reports", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
@inject
def create_report(
    data: ReportCreate,
    current_user: UserEntity = Depends(get_current_user),
    controller: ReportsController = Depends(Provide[Container.reports_controller])
):
    return controller.create_report(data, current_user.user_id)
