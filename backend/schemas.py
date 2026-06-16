from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class PatientBase(BaseModel):
    name: str

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class RPMReadingBase(BaseModel):
    metric_type: str
    value: float

class RPMReadingCreate(RPMReadingBase):
    patient_id: str

class RPMReading(RPMReadingBase):
    id: str
    patient_id: str
    timestamp: datetime

    class Config:
        from_attributes = True

class AIAlert(BaseModel):
    id: str
    patient_id: str
    alert_type: str
    severity: str
    priority_score: int
    message: str
    explanation: Optional[str] = None
    status: str
    source_engine: str
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AIDeteriorationEvent(BaseModel):
    id: str
    patient_id: str
    deterioration_score: int
    risk_level: str
    predicted_condition: str
    confidence: float
    contributing_factors: Dict[str, Any]
    time_window_days: int
    created_at: datetime

    class Config:
        from_attributes = True

class PatientBaseline(BaseModel):
    id: str
    patient_id: str
    metric_type: str
    avg_value: float
    min_value: float
    max_value: float
    std_dev: float
    updated_at: datetime

    class Config:
        from_attributes = True

class AITrend(BaseModel):
    id: str
    patient_id: str
    metric_type: str
    trend_direction: str
    slope_value: float
    confidence: float
    period_days: int
    created_at: datetime

    class Config:
        from_attributes = True

class AIAnomaly(BaseModel):
    id: str
    patient_id: str
    metric_type: str
    anomaly_type: str
    severity: str
    value: float
    baseline_value: float
    reason: str
    created_at: datetime

    class Config:
        from_attributes = True

class AIRiskScore(BaseModel):
    id: str
    patient_id: str
    risk_score: int
    risk_level: str
    contributing_factors: Dict[str, Any]
    calculated_at: datetime

    class Config:
        from_attributes = True
