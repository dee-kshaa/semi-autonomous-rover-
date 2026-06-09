from pydantic import BaseModel


class QualityDistribution(BaseModel):
    excellent: int
    good: int
    fair: int
    poor: int


class TrendPoint(BaseModel):
    bucket: str
    avg_rssi: float


class AnalyticsSummary(BaseModel):
    total_samples: int
    active_users: int
    avg_rssi: float
    quality_distribution: QualityDistribution
