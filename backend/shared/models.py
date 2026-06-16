from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from shared.database import Base
import uuid
from datetime import datetime

class Patient(Base):
    __tablename__ = "patients"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    readings = relationship("RPMReading", back_populates="patient", order_by="desc(RPMReading.timestamp)")

    @property
    def last_reading(self):
        return self.readings[0] if self.readings else None

    @property
    def latest_vitals(self):
        from sqlalchemy.orm import object_session
        from sqlalchemy import func
        session = object_session(self)
        if not session:
            return []
        subquery = session.query(
            RPMReading.vital_type,
            func.max(RPMReading.timestamp).label('max_timestamp')
        ).filter(RPMReading.patient_id == self.id).group_by(RPMReading.vital_type).subquery()
        
        return session.query(RPMReading).join(
            subquery,
            (RPMReading.vital_type == subquery.c.vital_type) &
            (RPMReading.timestamp == subquery.c.max_timestamp)
        ).filter(RPMReading.patient_id == self.id).all()

class RPMReading(Base):
    __tablename__ = "rpm_readings"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.id"))
    vital_type = Column(String, index=True)
    value = Column(Float, nullable=True)
    structured_value = Column(JSON, nullable=True)
    unit = Column(String, nullable=True)
    device_source = Column(String, nullable=True)
    reading_metadata = Column("metadata", JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="readings")

class AIFeature(Base):
    __tablename__ = "ai_features"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.id"))
    vital_type = Column(String(50))
    rolling_average_7d = Column(Float, nullable=True)
    trend_slope = Column(Float, nullable=True)
    deviation_from_baseline = Column(Float, nullable=True)
    variability_index = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AIAlert(Base):
    __tablename__ = "ai_alerts"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.id"))
    alert_type = Column(String(50))
    severity = Column(String(20)) # CRITICAL, HIGH, MEDIUM, LOW
    priority_score = Column(Integer)
    message = Column(Text)
    explanation = Column(Text)
    status = Column(String(20), default="open") # open, acknowledged, resolved
    source_engine = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

class AIDeteriorationEvent(Base):
    __tablename__ = "ai_deterioration_events"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.id"))
    deterioration_score = Column(Integer)
    risk_level = Column(String(20))
    predicted_condition = Column(String(100))
    confidence = Column(Float)
    contributing_factors = Column(JSON)
    time_window_days = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class PatientBaseline(Base):
    __tablename__ = "patient_baselines"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.id"))
    vital_type = Column(String(50))
    avg_value = Column(Float)
    min_value = Column(Float)
    max_value = Column(Float)
    std_dev = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AITrend(Base):
    __tablename__ = "ai_trends"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.id"))
    vital_type = Column(String(50))
    trend_direction = Column(String(20)) # increasing, decreasing, stable
    slope_value = Column(Float)
    confidence = Column(Float)
    period_days = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class AIAnomaly(Base):
    __tablename__ = "ai_anomalies"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.id"))
    vital_type = Column(String(50))
    anomaly_type = Column(String(50)) # spike, drop, deviation
    severity = Column(String(20)) # low, medium, high, critical
    value = Column(Float)
    baseline_value = Column(Float)
    reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class AIRiskScore(Base):
    __tablename__ = "ai_risk_scores"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.id"))
    risk_score = Column(Integer) # 0-100
    risk_level = Column(String(20)) # low, medium, high, critical
    contributing_factors = Column(JSON)
    calculated_at = Column(DateTime, default=datetime.utcnow)
