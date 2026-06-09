from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SignalLog(Base):
    __tablename__ = 'signal_logs'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False, index=True)
    location_id: Mapped[int] = mapped_column(ForeignKey('locations.id'), nullable=False, index=True)
    operator_id: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False, index=True)

    rssi: Mapped[int] = mapped_column(Integer, nullable=False)
    network_type: Mapped[str] = mapped_column(String(20), nullable=False)
    device_model: Mapped[str] = mapped_column(String(120), nullable=False)
    device_os: Mapped[str] = mapped_column(String(120), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, index=True)
    speed_mps: Mapped[float | None] = mapped_column(Float, nullable=True)

    user = relationship('User', back_populates='signal_logs')
    location = relationship('Location', back_populates='signal_logs')
    operator = relationship('Operator', back_populates='signal_logs')
    prediction = relationship('Prediction', back_populates='signal_log', uselist=False, cascade='all, delete-orphan')
