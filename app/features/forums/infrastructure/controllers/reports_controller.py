from fastapi import HTTPException, status
from app.features.forums.domain.entities import ReportEntity
from app.features.forums.infrastructure.schemas.forums_schemas import ReportCreate, ReportResponse
from app.features.forums.application.reports_usecases import CreateReportUseCase

class ReportsController:
    def __init__(self, create_report_uc: CreateReportUseCase):
        self.create_report_uc = create_report_uc

    def create_report(self, data: ReportCreate) -> ReportResponse:
        try:
            entity = ReportEntity(**data.model_dump())
            result = self.create_report_uc.execute(entity)
            return ReportResponse.model_validate(result)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
