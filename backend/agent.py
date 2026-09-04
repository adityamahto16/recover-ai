from backend.models import Payment

def analyze_payment(payment: Payment):
    if payment.status.lower() == "success":
        return {
            "action": "no_action",
            "reason": "Payment is already successful; no recovery action is required.",
            "recovery_score": 100,
            "recovery_level": "high",
        }


    score = 50
    score += min(payment.previous_successful_payments * 5, 30)
    score -= min(payment.previous_failed_attempts * 10, 30)
    if payment.amount <= 5000:
        score += 5
    score = max(0, min(score, 100))

    if score >= 80:
        recovery_level = "high"
    elif score >= 50:
        recovery_level = "medium"
    else:
        recovery_level = "low"

    if recovery_level == "low":
        action = "escalate_to_human"
        decision_reason = "Low recovery probability; human review is recommended."

    elif recovery_level == "high":
        if payment.reason == "insufficient_funds" :
            action ="aggressive_personalized_reminder"
            decision_reason = "high recovery probability"
        elif payment.reason == "card_declined" :
            action ="suggest_alternate_payment"
            decision_reason ="high recovery probability"
        elif payment.reason == "timeout" :
            action ="retry_payment"
            decision_reason ="high recovery probability"
        else :
            action ="escalate_to_human"
            decision_reason ="high recovery probability"

    else :
        if payment.reason == "insufficient_funds":
            action = "send_payment_reminder"
            decision_reason = "Customer may complete the payment after funds are available."

        elif payment.reason == "card_declined":
            action = "suggest_alternate_payment"
            decision_reason = "The customer should be offered an alternate payment method."

        elif payment.reason == "timeout":
            action = "retry_payment"
            decision_reason = "The payment may have failed because of a network error."

        else:
            action = "escalate_to_human"
            decision_reason = "The failure reason is not recognized by the recovery system."

    return {
        "action": action,
        "reason": decision_reason,
        "recovery_score": score,
        "recovery_level": recovery_level,
    }
