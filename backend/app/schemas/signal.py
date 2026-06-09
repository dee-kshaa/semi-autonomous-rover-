from datetime import datetime
from pydantic import BaseModel, Field


class SignalLogCreate(BaseModel):
    rssi: int = Field(ge=-140, le=0)
    network_type: str = Field(pattern='^(2G|3G|4G|5G)$')
    operator_name: str = Field(min_length=2, max_length=100)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    city: str | None = None
    timestamp: datetime
    device_model: str = Field(min_length=1, max_length=120)
    device_os: str = Field(min_length=1, max_length=120)
    speed_mps: float | None = None


class SignalLogResponse(BaseModel):
    id: int
    user_id: int
    rssi: int
    network_type: str
    operator_name: str
    latitude: float
    longitude: float
    timestamp: datetime


class HeatmapPoint(BaseModel):
    latitude: float
    longitude: float
    avg_rssi: float
    sample_count: int


class OperatorComparison(BaseModel):
    operator_name: str
    avg_rssi: float
    sample_count: int
    dead_zone_rate: float
