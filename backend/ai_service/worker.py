import os
from celery import Celery
from shared.database import SessionLocal
from shared import models
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

        metric = current_reading.vital_type.upper()
        val = current_reading.value if current_reading.value is not None else 0.0

        # 1. Feature Extraction & Baseline Update
        baseline = db.query(models.PatientBaseline).filter(
            models.PatientBaseline.patient_id == patient_id,
            models.PatientBaseline.vital_type == metric
        ).first()

        if not baseline:
            baseline = models.PatientBaseline(
                patient_id=patient_id, vital_type=metric,
                avg_value=val, min_value=val, max_value=val, std_dev=0.0
            )
            db.add(baseline)
        else:
            baseline.avg_value = (baseline.avg_value * 9 + val) / 10
            baseline.min_value = min(baseline.min_value, val)
            baseline.max_value = max(baseline.max_value, val)
            baseline.std_dev = abs(val - baseline.avg_value) * 0.5 

        db.commit()
        
        # Calculate rolling averages & fetch readings for trends
        now = datetime.utcnow()
        readings_7d = db.query(models.RPMReading).filter(
            models.RPMReading.patient_id == patient_id,
            models.RPMReading.vital_type == metric,
            models.RPMReading.timestamp >= now - timedelta(days=7),
            models.RPMReading.value.isnot(None)
        ).order_by(models.RPMReading.timestamp.asc()).all()
        
        readings_30d = db.query(models.RPMReading).filter(
            models.RPMReading.patient_id == patient_id,
            models.RPMReading.vital_type == metric,
            models.RPMReading.timestamp >= now - timedelta(days=30),
            models.RPMReading.value.isnot(None)
        ).order_by(models.RPMReading.timestamp.asc()).all()

        values_7d = [r.value for r in readings_7d]
        values_30d = [r.value for r in readings_30d]
        
        rolling_avg_7d = sum(values_7d) / len(values_7d) if values_7d else val
        deviation_from_baseline = val - baseline.avg_value
        variability_index = baseline.std_dev / baseline.avg_value if baseline.avg_value != 0 else 0
        
        # Calculate Trends
        slope_7d = calculate_slope(values_7d)
        direction_7d = "stable"
        if slope_7d > 0.5: direction_7d = "increasing"
        elif slope_7d < -0.5: direction_7d = "decreasing"
        
        trend_7d = models.AITrend(
            patient_id=patient_id, vital_type=metric,
            trend_direction=direction_7d, slope_value=slope_7d,
            confidence=0.85, period_days=7
        )
        db.add(trend_7d)

        slope_30d = calculate_slope(values_30d)
        direction_30d = "stable"
        if slope_30d > 0.1: direction_30d = "increasing"
        elif slope_30d < -0.1: direction_30d = "decreasing"

        trend_30d = models.AITrend(
            patient_id=patient_id, vital_type=metric,
            trend_direction=direction_30d, slope_value=slope_30d,
            confidence=0.85, period_days=30
        )
        db.add(trend_30d)

        # Store AI Features
        ai_feature = models.AIFeature(
            patient_id=patient_id,
            vital_type=metric,
            rolling_average_7d=rolling_avg_7d,
            trend_slope=slope_7d,
            deviation_from_baseline=deviation_from_baseline,
            variability_index=variability_index
        )
        db.add(ai_feature)

        # 3. Anomaly Detection Engine
        anomaly_detected = False
        anomaly_severity = "low"
        anomaly_reason = ""
        risk_score = 0

        if metric == "SPO2":
            if val < 90:
                anomaly_detected = True
                anomaly_severity = "critical"
                anomaly_reason = f"SpO2 critically low: {val}"
                risk_score += 80
            elif val < 95:
                anomaly_detected = True
                anomaly_severity = "medium"
                anomaly_reason = f"SpO2 moderately low: {val}"
                risk_score += 30

        if metric == "BP_SYS":
            if val > baseline.avg_value * 1.2:
                anomaly_detected = True
                anomaly_severity = "high"
                anomaly_reason = f"BP_SYS deviated 20% from baseline {baseline.avg_value:.1f}"
                risk_score += 40

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

            # Z-score baseline anomaly
            if baseline.std_dev > 0:
                z_score = abs(val - baseline.avg_value) / baseline.std_dev
                if z_score > 3:
                    anomaly_detected = True
                    anomaly_severity = max(anomaly_severity, "high")
                    anomaly_reason = anomaly_reason + f" High Z-score ({z_score:.1f})."

            if slope_7d > 2:
                risk_score += 30

        if anomaly_detected:
            anomaly = models.AIAnomaly(
                patient_id=patient_id, vital_type=metric,
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
            contributing_factors={"trend_slope": slope_7d, "anomaly_severity": anomaly_severity}
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
