from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Prediction(Base):
    __tablename__ = 'predictions'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    signal_log_id: Mapped[int] = mapped_column(ForeignKey('signal_logs.id'), unique=True, nullable=False)
    predicted_signal_strength: Mapped[float] = mapped_column(Float, nullable=False)
    dead_zone_probability: Mapped[float] = mapped_column(Float, nullable=False)
    recommended_operator: Mapped[str | None] = mapped_column(String(100), nullable=True)
    coverage_class: Mapped[str] = mapped_column(String(50), nullable=False)
    anomaly_score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    signal_log = relationship('SignalLog', back_populates='prediction')
