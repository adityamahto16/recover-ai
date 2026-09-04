from fastapi import FastAPI, HTTPException

from backend.models import Payment
from backend.agent import analyze_payment
from backend.execute import execute_action
from backend.database import (
    initialize_database,
    save_analysis,
    get_analysis,
    get_transaction_by_analysis_id,
    save_transaction,
    get_transactions,
    get_analysis_count,
    clear_transactions,
)


app = FastAPI(
    title="RecoverAI API",
    description="AI-powered payment failure recovery system",
    version="1.0.0",
)


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
def startup_event():
    initialize_database()


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "RecoverAI API is running"
    }


# ============================================================
# ANALYZE PAYMENT
# ============================================================

@app.post("/payments")
def analyze_payment_endpoint(payment: Payment):

    analysis = analyze_payment(payment)

    analysis_id = save_analysis(
        payment.customer,
        payment.amount,
        payment.status,
        payment.reason,
        payment.previous_successful_payments,
        payment.previous_failed_attempts,
        analysis["recovery_score"],
        analysis["action"],
        analysis["reason"],
    )

    return {
        "message": "payment analyzed",
        "analysis_id": analysis_id,
        "Payment": payment.model_dump(),
        "recommended_action": analysis["action"],
        "reason": analysis["reason"],
        "recovery_score": analysis["recovery_score"],
    }


# ============================================================
# GET ANALYSIS
# ============================================================

@app.get("/analysis/{analysis_id}")
def get_analysis_endpoint(
    analysis_id: int,
):

    if analysis_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="analysis_id must be greater than 0.",
        )

    analysis = get_analysis(
        analysis_id
    )

    if analysis is None:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found.",
        )

    return analysis


# ============================================================
# EXECUTE RECOVERY ACTION
# ============================================================

@app.post("/execute-action")
def execute_recovery_action(
    analysis_id: int,
    action: str,
    retry_success: bool | None = None,
):

    # --------------------------------------------------------
    # Validate analysis ID
    # --------------------------------------------------------

    if analysis_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="analysis_id must be greater than 0.",
        )


    # --------------------------------------------------------
    # Allowed actions
    # --------------------------------------------------------

    allowed_actions = {
        "retry_payment",
        "send_payment_reminder",
        "suggest_alternate_payment",
        "aggressive_personalized_reminder",
        "escalate_to_human",
    }

    if action not in allowed_actions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported recovery action: {action}",
        )


    # --------------------------------------------------------
    # Find analysis
    # --------------------------------------------------------

    analysis = get_analysis(
        analysis_id
    )

    if analysis is None:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found.",
        )


    # --------------------------------------------------------
    # Prevent duplicate recovery actions
    # --------------------------------------------------------

    existing_transaction = get_transaction_by_analysis_id(
        analysis_id
    )

    if existing_transaction:

        if existing_transaction.get(
            "payment_recovered"
        ) == "Yes":

            return {
                "message": "Payment already recovered",
                "analysis_id": analysis_id,
                "action_result": {
                    "action": existing_transaction.get(
                        "action"
                    ),
                    "status": existing_transaction.get(
                        "action_status"
                    ),
                    "message": (
                        "This payment has already been recovered."
                    ),
                },
                "payment_recovered": True,
                "already_recovered": True,
            }

        raise HTTPException(
            status_code=409,
            detail=(
                "A recovery action has already been "
                "executed for this analysis."
            ),
        )


    # --------------------------------------------------------
    # Execute action
    # --------------------------------------------------------

    action_result = execute_action(
        action,
        retry_success,
    )


    # --------------------------------------------------------
    # Determine recovery status
    # --------------------------------------------------------

    payment_recovered = (
        action_result.get("status") == "success"
        and action == "retry_payment"
    )


    # --------------------------------------------------------
    # Save transaction
    # --------------------------------------------------------

    save_transaction(
        analysis_id=analysis_id,
        customer=analysis["customer"],
        amount=analysis["amount"],
        status=analysis["status"],
        reason=analysis["reason"],
        recovery_score=analysis["recovery_score"],
        action=action,
        action_status=action_result.get("status"),
        payment_recovered=payment_recovered,
    )


    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "message": "recovery action executed",
        "analysis_id": analysis_id,
        "action_result": action_result,
        "payment_recovered": payment_recovered,
    }


# ============================================================
# TRANSACTION HISTORY
# ============================================================

@app.get("/transactions")
def get_transaction_history():

    return {
        "transactions": get_transactions(),
        "analyzed_payments": get_analysis_count(),
    }


# ============================================================
# CLEAR TRANSACTION HISTORY
# ============================================================

@app.delete("/transactions")
def clear_transaction_history():

    clear_transactions()

    return {
        "message": "Transaction history cleared successfully."
    }