from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces import IMetricsRepository
from app.models.document import Metrics
from typing import List, Optional

class MetricsRepository(BaseRepository, IMetricsRepository):
    def increment(self, action: str, user_id: str) -> Metrics:
        metric = self.db.query(Metrics).filter(Metrics.action == action, Metrics.user_id == user_id).first()
        if metric:
            metric.count += 1
        else:
            metric = Metrics(action=action, count=1, user_id=user_id)
            self.db.add(metric)
        self.db.commit()
        self.db.refresh(metric)
        return metric

    def get_metric(self, action: str, user_id: str) -> Optional[Metrics]:
        return self.db.query(Metrics).filter(Metrics.action == action, Metrics.user_id == user_id).first()

    def get_all(self, user_id: str) -> List[Metrics]:
        return self.db.query(Metrics).filter(Metrics.user_id == user_id).all()
