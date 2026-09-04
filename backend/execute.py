def execute_action(action, retry_success=None):
    """
    Execute a recovery action and return a standardized result.
    """

    if action == "aggressive_personalized_reminder":
        return {
            "action": "aggressive_personalized_reminder",
            "status": "success",
            "channel": "SMS",
            "message": "Personalized payment reminder sent via SMS.",
        }

    if action == "send_payment_reminder":
        return {
            "action": "send_payment_reminder",
            "status": "success",
            "channel": "SMS,WP,EMAIL",
            "message": "Payment reminder sent successfully.",
        }

    if action == "suggest_alternate_payment":
        return {
            "action": "suggest_alternate_payment",
            "status": "success",
            "channel": "UPI,CC,DC,Pay_later",
            "message": "Alternate payment methods offered.",
        }

    if action == "retry_payment":

        if retry_success is None:
            retry_success = True

        if not isinstance(retry_success, bool):
            return {
                "action": "retry_payment",
                "status": "failed",
                "message": "retry_success must be a boolean value.",
            }

        if retry_success:
            return {
                "action": "retry_payment",
                "status": "success",
                "message": "Payment recovered successfully.",
            }

        return {
            "action": "retry_payment",
            "status": "failed",
            "message": "Payment retry failed.",
        }

    if action == "escalate_to_human":
        return {
            "action": "escalate_to_human",
            "status": "success",
            "message": "Case assigned to human support.",
        }

    return {
        "action": action,
        "status": "failed",
        "message": "Unknown recovery action.",
    }