from container import Container
from salud_prenatal_shared_core.db_cleanup import close_db_after
from salud_prenatal_shared_core.auth_dependencies import get_current_user
from fastapi import APIRouter, Depends, status
from app.forums.infrastructure.schemas.forums_schemas import ReportCreate, ReportResponse
from app.forums.infrastructure.controllers.reports_controller import ReportsController
from salud_prenatal_shared_core.auth_dependencies import Principal as UserEntity

router = APIRouter(prefix="/forums", tags=["Forums - Reports"])


@router.post("/reports", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
@close_db_after(Container)
def create_report(
    data: ReportCreate,
    current_user: UserEntity = Depends(get_current_user),
):
    controller = Container.reports_controller()
    return controller.create_report(data, current_user.user_id)
