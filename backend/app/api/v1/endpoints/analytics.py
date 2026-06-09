from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analytics import AnalyticsSummary, TrendPoint
from app.schemas.signal import HeatmapPoint, OperatorComparison
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix='/analytics', tags=['analytics'])


@router.get('/summary', response_model=AnalyticsSummary)
def get_summary(db: Session = Depends(get_db)):
    return AnalyticsService.summary(db)


@router.get('/trend', response_model=list[TrendPoint])
def get_trend(hours: int = Query(default=24, ge=1, le=168), db: Session = Depends(get_db)):
    return AnalyticsService.trend(db, hours)


@router.get('/heatmap', response_model=list[HeatmapPoint])
def get_heatmap(db: Session = Depends(get_db)):
    return AnalyticsService.heatmap(db)


@router.get('/operator-comparison', response_model=list[OperatorComparison])
def get_operator_comparison(db: Session = Depends(get_db)):
    return AnalyticsService.operator_comparison(db)
