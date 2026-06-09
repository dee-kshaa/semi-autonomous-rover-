from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.signal import SignalLogCreate
from app.services.prediction_service import PredictionService
from app.services.signal_service import SignalService

router = APIRouter(prefix='/signals', tags=['signals'])


@router.post('/ingest')
def ingest_signal(
    payload: SignalLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    signal = SignalService.create_signal_log(db, current_user.id, payload)
    prediction = PredictionService.infer_and_store(db, signal)
    return {
        'signal_log_id': signal.id,
        'prediction_id': prediction.id,
        'coverage_class': prediction.coverage_class,
        'dead_zone_probability': prediction.dead_zone_probability,
    }
