import os
from celery import Celery
import time
from database import SessionLocal
import models
from datetime import datetime, timedelta
import math

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
celery_app = Celery("rpm_worker", broker=redis_url, backend=redis_url)

def calculate_slope(values):
    n = len(values)
    if n < 2: return 0
    x = list(range(n))
    y = values
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    denominator = sum((x[i] - mean_x) ** 2 for i in range(n))
    return numerator / denominator if denominator != 0 else 0

@celery_app.task(name="process_rpm_reading")
def process_rpm_reading(reading_id: str, patient_id: str):
    print(f"Processing RPM Reading: {reading_id} for Patient: {patient_id}")
    db = SessionLocal()
    try:
        current_reading = db.query(models.RPMReading).filter(models.RPMReading.id == reading_id).first()
        if not current_reading:
            return {"status": "error", "message": "Reading not found"}

        metric = current_reading.metric_type.upper()
        val = current_reading.value

        # 1. Feature Extraction & Baseline Update
        baseline = db.query(models.PatientBaseline).filter(
            models.PatientBaseline.patient_id == patient_id,
            models.PatientBaseline.metric_type == metric
        ).first()

        if not baseline:
            baseline = models.PatientBaseline(
                patient_id=patient_id, metric_type=metric,
                avg_value=val, min_value=val, max_value=val, std_dev=0.0
            )
            db.add(baseline)
        else:
            # Simple running average update (mock implementation)
            baseline.avg_value = (baseline.avg_value * 9 + val) / 10
            baseline.min_value = min(baseline.min_value, val)
            baseline.max_value = max(baseline.max_value, val)
            # Rough std dev estimation
            baseline.std_dev = abs(val - baseline.avg_value) * 0.5 

        db.commit()

        # Fetch recent readings for trend
        fourteen_days_ago = datetime.utcnow() - timedelta(days=14)
        recent_readings = db.query(models.RPMReading).filter(
            models.RPMReading.patient_id == patient_id,
            models.RPMReading.metric_type == metric,
            models.RPMReading.timestamp >= fourteen_days_ago
        ).order_by(models.RPMReading.timestamp.desc()).limit(14).all()

        recent_readings.reverse()
        values = [r.value for r in recent_readings]

        # 2. Trend Analysis Engine
        slope = calculate_slope(values)
        direction = "stable"
        if slope > 0.5: direction = "increasing"
        elif slope < -0.5: direction = "decreasing"

        trend = models.AITrend(
            patient_id=patient_id, metric_type=metric,
            trend_direction=direction, slope_value=slope,
            confidence=0.85, period_days=14
        )
        db.add(trend)

        # 3. Anomaly Detection Engine
        anomaly_detected = False
        anomaly_severity = "low"
        anomaly_reason = ""
        risk_score = 0

        if metric == "BP_SYS":
            if val > 180 or val < 90:
                anomaly_detected = True
                anomaly_severity = "critical"
                anomaly_reason = f"BP_SYS out of safe bounds: {val}"
                risk_score += 50
            elif val > 140:
                anomaly_detected = True
                anomaly_severity = "high"
                anomaly_reason = f"BP_SYS elevated: {val}"
                risk_score += 25
            
            # Baseline anomaly
            if baseline.std_dev > 0 and abs(val - baseline.avg_value) > (2 * baseline.std_dev):
                anomaly_detected = True
                anomaly_severity = max(anomaly_severity, "medium")
                anomaly_reason = f"BP_SYS deviated from patient baseline {baseline.avg_value:.1f}"

            if slope > 2:
                risk_score += 30

        if anomaly_detected:
            anomaly = models.AIAnomaly(
                patient_id=patient_id, metric_type=metric,
                anomaly_type="deviation", severity=anomaly_severity,
                value=val, baseline_value=baseline.avg_value, reason=anomaly_reason
            )
            db.add(anomaly)

        # 4. Risk Scoring Engine
        risk_level = "low"
        if risk_score > 75: risk_level = "critical"
        elif risk_score > 50: risk_level = "high"
        elif risk_score > 25: risk_level = "medium"

        r_score = models.AIRiskScore(
            patient_id=patient_id, risk_score=risk_score, risk_level=risk_level,
            contributing_factors={"trend_slope": slope, "anomaly_severity": anomaly_severity}
        )
        db.add(r_score)

        # 5. Smart Alert Engine
        if risk_score > 75 or anomaly_severity == "critical":
            alert = models.AIAlert(
                patient_id=patient_id, alert_type="Critical Risk",
                severity="CRITICAL", priority_score=risk_score + 20,
                message=f"Immediate review required for {metric}: {val}",
                source_engine="Orchestrator"
            )
            db.add(alert)
        elif risk_score > 50 or anomaly_severity == "high":
            alert = models.AIAlert(
                patient_id=patient_id, alert_type="High Risk",
                severity="HIGH", priority_score=risk_score + 10,
                message=f"Elevated {metric} detected: {val}",
                source_engine="Orchestrator"
            )
            db.add(alert)

        db.commit()
        return {"status": "success", "risk_score": risk_score}
    finally:
        db.close()
