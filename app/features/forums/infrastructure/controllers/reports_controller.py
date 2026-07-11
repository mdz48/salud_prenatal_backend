from fastapi import HTTPException, status
from app.features.forums.domain.report_entity import ReportEntity
from app.features.forums.application.reports.create_report_usecase import CreateReportUseCase
from app.features.forums.infrastructure.schemas.forums_schemas import ReportCreate, ReportResponse
from app.core.error_handlers import internal_error

class ReportsController:
    def __init__(self, create_report_uc: CreateReportUseCase):
        self.create_report_uc = create_report_uc

    def create_report(self, data: ReportCreate, reporter_id: int) -> ReportResponse:
        try:
            entity = ReportEntity(**data.model_dump(), reporter_id=reporter_id)
            result = self.create_report_uc.execute(entity)
            return ReportResponse.model_validate(result)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            raise internal_error(e)
