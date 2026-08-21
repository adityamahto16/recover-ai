from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Payment(BaseModel):
    customer: str
    amount: float
    status: str
    reason: str
    previous_successfull_payments:int
    previous_failed_attempts:int


@app.get("/")
def home():
    return {"message": "RecoverAI backend is running"}


@app.post("/payments")
def create_payment(payment: Payment):
    if payment.reason == "insufficient funds":
        if payment.previous_successfull_payments >= 5 and payment.previous_failed_attempts <= 2:
            action = "send_personalised_remainder"
            decision_reason = "High-value returning customer with a strong payment history."
        else:
            action = "send_payment_remainder"
            decision_reason = "customer may complete the payment after funds are available"
    elif payment.reason == "card_declined":
        action = "suggest_alternate_payment"
        decision_reason = "the customer should be offered alternate payment method"
    elif payment.reason == "timeout":
        action = "retry_payment"
        decision_reason = "the payment may have failed because of network error"
    else:
        action = "escalate to human"
        decision_reason = "the failure reason is not recognized by the recovery system"

    return {
        "message": "payment analyzed",
        "Payment": payment,
        "recommended_action": action,
        "reason": decision_reason,
    }
