import logging
import time
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("fraud_detection")

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from semantic_search import search_fraud_knowledge

from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
)
from investigation_service import (
    generate_investigation_summary,
)

from database import SessionLocal
from decision_engine import get_risk_assessment
from explanation_engine import generate_explanation
from model_service import predict_fraud
from models import FraudAssessment
from schemas import FraudEvent
from simulator import generate_simulated_event


app = FastAPI(
    title="Fraud Detection API",
    description="Real-time fraud detection platform for digital lending",
    version="1.0.0"
)

@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.perf_counter()

    try:
        response = await call_next(request)

        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

        logger.info(
            "%s %s -> %s (%.1f ms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        return response

    except Exception:
        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

        logger.exception(
            "%s %s -> 500 (%.1f ms)",
            request.method,
            request.url.path,
            duration_ms,
        )

        raise

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "https://fraudsense-frontend-fcif.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Basic routes
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Fraud Detection API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

@app.post("/api/auth/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = authenticate_user(
        form_data.username,
        form_data.password
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    access_token = create_access_token(user)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user
    }

# ---------------------------------------------------------
# Real-time fraud prediction
# ---------------------------------------------------------

@app.post("/api/fraud/check")
def check_fraud(
    event: FraudEvent,
    current_user: str = Depends(get_current_user)
):

    fraud_probability = predict_fraud(event)

    risk_assessment = get_risk_assessment(
        fraud_probability
    )

    reasons = generate_explanation(event)

    db = SessionLocal()

    try:
        assessment = FraudAssessment(
            transaction_amount=event.transaction_amount,
            transactions_last_10min=event.transactions_last_10min,
            time_since_last_transaction=event.time_since_last_transaction,
            device_is_new=event.device_is_new,
            location_is_unusual=event.location_is_unusual,
            ip_is_unusual=event.ip_is_unusual,
            is_unusual_time=event.is_unusual_time,
            account_age_days=event.account_age_days,
            fraud_probability=fraud_probability,
            risk_band=risk_assessment["risk_band"],
            decision=risk_assessment["decision"],
            reasons="; ".join(reasons)
        )

        db.add(assessment)
        db.commit()
        db.refresh(assessment)

        assessment_id = assessment.id
        
        logger.info(
    "Fraud assessment completed | user=%s | assessment_id=%s | risk=%s | decision=%s",
    current_user,
    assessment_id,
    risk_assessment["risk_band"],
    risk_assessment["decision"],
)

    finally:
        db.close()

    return {
        "assessment_id": assessment_id,
        "fraud_probability": round(
            fraud_probability,
            4
        ),
        "risk_band": risk_assessment["risk_band"],
        "decision": risk_assessment["decision"],
        "reasons": reasons
    }

@app.post("/api/fraud/simulate")
def simulate_fraud_event(
    current_user: str = Depends(get_current_user)
):

    simulated_event = generate_simulated_event()

    event = FraudEvent(
        **simulated_event
    )

    fraud_probability = predict_fraud(event)

    risk_assessment = get_risk_assessment(
        fraud_probability
    )

    reasons = generate_explanation(event)

    db = SessionLocal()

    try:
        assessment = FraudAssessment(
            transaction_amount=event.transaction_amount,
            transactions_last_10min=event.transactions_last_10min,
            time_since_last_transaction=event.time_since_last_transaction,
            device_is_new=event.device_is_new,
            location_is_unusual=event.location_is_unusual,
            ip_is_unusual=event.ip_is_unusual,
            is_unusual_time=event.is_unusual_time,
            account_age_days=event.account_age_days,
            fraud_probability=fraud_probability,
            risk_band=risk_assessment["risk_band"],
            decision=risk_assessment["decision"],
            reasons="; ".join(reasons)
        )

        db.add(assessment)
        db.commit()
        db.refresh(assessment)

        assessment_id = assessment.id

    finally:
        db.close()

    return {
        "assessment_id": assessment_id,
        "event_source": "SIMULATED_LIVE_EVENT",
        "event": simulated_event,
        "fraud_probability": round(
            fraud_probability,
            4
        ),
        "risk_band": risk_assessment["risk_band"],
        "decision": risk_assessment["decision"],
        "reasons": reasons
    }

# ---------------------------------------------------------
# AI fraud investigation
# ---------------------------------------------------------

@app.post("/api/fraud/investigate")
def investigate_fraud(
    event: FraudEvent,
    current_user: str = Depends(get_current_user)
):
    fraud_probability = predict_fraud(event)

    risk_assessment = get_risk_assessment(
        fraud_probability
    )

    investigation = (
        generate_investigation_summary(
            event=event.model_dump(),
            fraud_probability=fraud_probability,
            risk_band=risk_assessment["risk_band"],
            decision=risk_assessment["decision"],
        )
    )
    
    logger.info(
        "AI investigation completed | user=%s | risk=%s | decision=%s",
        current_user,
        risk_assessment["risk_band"],
        risk_assessment["decision"],
    )

    return {
        "fraud_probability": round(
            fraud_probability,
            4
        ),
        "risk_band": risk_assessment["risk_band"],
        "decision": risk_assessment["decision"],
        "reasons": generate_explanation(event),
        "ai_investigation": investigation["summary"],
        "knowledge": investigation["knowledge"],
    }
# ---------------------------------------------------------
# Semantic fraud knowledge search
# ---------------------------------------------------------

@app.get("/api/knowledge/search")
def search_knowledge(
    q: str,
    limit: int = 3,
    current_user: str = Depends(get_current_user)
):
    if not q.strip():
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )

    try:
        results = search_fraud_knowledge(
            q,
            limit
        )

        return {
            "query": q,
            "results": results
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


# ---------------------------------------------------------
# Get recent assessments
# ---------------------------------------------------------

@app.get("/api/assessments")
def get_assessments(
    limit: int = 20,
    current_user: str = Depends(get_current_user)
):

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100"
        )

    db = SessionLocal()

    try:
        statement = (
            select(FraudAssessment)
            .order_by(
                FraudAssessment.created_at.desc()
            )
            .limit(limit)
        )

        assessments = db.execute(statement).scalars().all()

        return [
            {
                "id": assessment.id,
                "transaction_amount": assessment.transaction_amount,
                "fraud_probability": round(
                    assessment.fraud_probability,
                    4
                ),
                "risk_band": assessment.risk_band,
                "decision": assessment.decision,
                "created_at": assessment.created_at
            }
            for assessment in assessments
        ]

    finally:
        db.close()


# ---------------------------------------------------------
# Get one assessment by ID
# ---------------------------------------------------------

@app.get("/api/assessments/{assessment_id}")
def get_assessment(
    assessment_id: int,
    current_user: str = Depends(get_current_user)
):

    db = SessionLocal()

    try:
        assessment = db.get(
            FraudAssessment,
            assessment_id
        )

        if assessment is None:
            raise HTTPException(
                status_code=404,
                detail="Assessment not found"
            )

        return {
            "id": assessment.id,
            "transaction_amount": assessment.transaction_amount,
            "transactions_last_10min": assessment.transactions_last_10min,
            "time_since_last_transaction": assessment.time_since_last_transaction,
            "device_is_new": assessment.device_is_new,
            "location_is_unusual": assessment.location_is_unusual,
            "ip_is_unusual": assessment.ip_is_unusual,
            "is_unusual_time": assessment.is_unusual_time,
            "account_age_days": assessment.account_age_days,
            "fraud_probability": round(
                assessment.fraud_probability,
                4
            ),
            "risk_band": assessment.risk_band,
            "decision": assessment.decision,
            "reasons": assessment.reasons.split("; "),
            "created_at": assessment.created_at
        }

    finally:
        db.close()


# ---------------------------------------------------------
# Dashboard summary
# ---------------------------------------------------------

@app.get("/api/dashboard/summary")
def get_dashboard_summary(
    current_user: str = Depends(get_current_user)
):

    db = SessionLocal()

    try:
        total = db.scalar(
            select(
                func.count(FraudAssessment.id)
            )
        ) or 0

        low_risk = db.scalar(
            select(
                func.count(FraudAssessment.id)
            ).where(
                FraudAssessment.risk_band == "LOW"
            )
        ) or 0

        medium_risk = db.scalar(
            select(
                func.count(FraudAssessment.id)
            ).where(
                FraudAssessment.risk_band == "MEDIUM"
            )
        ) or 0

        high_risk = db.scalar(
            select(
                func.count(FraudAssessment.id)
            ).where(
                FraudAssessment.risk_band == "HIGH"
            )
        ) or 0

        return {
            "total_assessments": total,
            "low_risk": low_risk,
            "medium_risk": medium_risk,
            "high_risk": high_risk
        }

    finally:
        db.close()