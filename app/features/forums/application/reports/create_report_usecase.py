from app.features.forums.domain.ports import IForumsRepository
from app.features.forums.domain.report_entity import ReportEntity

class CreateReportUseCase:
    def __init__(self, forums_repo: IForumsRepository):
        self.forums_repo = forums_repo

    def execute(self, report: ReportEntity) -> ReportEntity:
        return self.forums_repo.create_report(report)
