import streamlit as st
import requests


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="RecoverAI | Payment Recovery",
    page_icon="💳",
    layout="wide",
)


# ============================================================
# CONFIG
# ============================================================

API_URL = "http://127.0.0.1:8000"


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #0e1117;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 18px;
        color: #9ca3af;
        margin-bottom: 30px;
    }

    .metric-card {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        background-color: #161b22;
        text-align: center;
    }

    .metric-title {
        color: #9ca3af;
        font-size: 14px;
    }

    .metric-value {
        font-size: 30px;
        font-weight: 700;
    }

    .section-title {
        font-size: 24px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "result" not in st.session_state:
    st.session_state.result = None

if "analysis_id" not in st.session_state:
    st.session_state.analysis_id = None

if "action_result" not in st.session_state:
    st.session_state.action_result = None


# ============================================================
# LOAD TRANSACTION HISTORY
# ============================================================

def load_history():
    try:
        response = requests.get(
            f"{API_URL}/transactions",
            timeout=5,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException:
        return {
            "transactions": [],
            "analyzed_payments": 0,
        }


history_data = load_history()

transactions = history_data.get(
    "transactions",
    [],
)


# ============================================================
# ANALYZED PAYMENT COUNT
# ============================================================

# Count each executed recovery case only once.
executed_analysis_ids = {
    transaction.get("analysis_id")
    for transaction in transactions
    if transaction.get("analysis_id") is not None
}

current_analysis_id = st.session_state.get(
    "analysis_id"
)

analyzed_payments = len(
    executed_analysis_ids
)

# Include an analysis that has been created but
# has not yet had a recovery action executed.
if (
    current_analysis_id is not None
    and current_analysis_id not in executed_analysis_ids
):
    analyzed_payments += 1


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="title">RecoverAI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">AI-powered payment failure recovery system</div>',
    unsafe_allow_html=True,
)


# ============================================================
# DASHBOARD METRICS
# ============================================================

successful_recoveries = sum(
    1
    for transaction in transactions
    if transaction.get("payment_recovered") in (
        True,
        1,
        "True",
        "true",
        "Yes",
        "yes",
        "1",
    )
)

failed_recoveries = sum(
    1
    for transaction in transactions
    if transaction.get("payment_recovered") in (
        False,
        0,
        "False",
        "false",
        "No",
        "no",
        "0",
    )
)

if analyzed_payments > 0:

    recovery_rate = (
        successful_recoveries / analyzed_payments
    ) * 100

else:

    recovery_rate = 0


col1, col2, col3, col4 = st.columns(4)

with col1:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Analyzed Payments</div>
            <div class="metric-value">{analyzed_payments}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Recovered</div>
            <div class="metric-value">{successful_recoveries}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Failed Recovery</div>
            <div class="metric-value">{failed_recoveries}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Recovery Rate</div>
            <div class="metric-value">{recovery_rate:.1f}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Payment Details")

customer = st.sidebar.text_input(
    "Customer Name",
    value="Rahul",
)

amount = st.sidebar.number_input(
    "Amount",
    min_value=0.01,
    value=1999.0,
    step=100.0,
)

status = st.sidebar.selectbox(
    "Payment Status",
    [
        "failed",
        "success",
    ],
)

reason = st.sidebar.selectbox(
    "Failure Reason",
    [
        "timeout",
        "insufficient_funds",
        "card_declined",
        "invalid_card",
    ],
)

previous_successful_payments = st.sidebar.number_input(
    "Previous Successful Payments",
    min_value=0,
    value=5,
    step=1,
)

previous_failed_attempts = st.sidebar.number_input(
    "Previous Failed Attempts",
    min_value=0,
    value=0,
    step=1,
)


# ============================================================
# BUTTONS
# ============================================================

analyze_button = st.sidebar.button(
    "Analyze Payment",
    use_container_width=True,
)

clear_button = st.sidebar.button(
    "Clear Transaction History",
    use_container_width=True,
)


# ============================================================
# CLEAR HISTORY
# ============================================================

if clear_button:

    try:

        response = requests.delete(
            f"{API_URL}/transactions",
            timeout=5,
        )

        response.raise_for_status()

        st.session_state.result = None
        st.session_state.analysis_id = None
        st.session_state.action_result = None

        st.success(
            "Transaction history cleared successfully."
        )

        st.rerun()

    except requests.RequestException as exc:

        st.error(
            "Unable to clear transaction history."
        )

        error_detail = None

        response = getattr(
            exc,
            "response",
            None,
        )

        if response is not None:

            try:

                error_data = response.json()

                error_detail = error_data.get(
                    "detail"
                )

            except (
                ValueError,
                AttributeError,
            ):

                pass

        if error_detail:

            st.warning(
                f"Backend: {error_detail}"
            )

        else:

            st.warning(
                "Please make sure the RecoverAI backend is running."
            )


# ============================================================
# ANALYZE PAYMENT
# ============================================================

if analyze_button:

    if not customer.strip():

        st.warning(
            "Please enter a customer name before analyzing."
        )

        st.stop()

    payment_data = {
        "customer": customer.strip(),
        "amount": amount,
        "status": status,
        "reason": reason,
        "previous_successful_payments": int(
            previous_successful_payments
        ),
        "previous_failed_attempts": int(
            previous_failed_attempts
        ),
    }

    try:

        response = requests.post(
            f"{API_URL}/payments",
            json=payment_data,
            timeout=10,
        )

        response.raise_for_status()

        result = response.json()

        st.session_state.result = result

        st.session_state.analysis_id = result.get(
            "analysis_id"
        )

        st.session_state.action_result = None

        st.rerun()

    except requests.RequestException as exc:

        st.error(
            "RecoverAI could not process the payment."
        )

        error_detail = None

        response = getattr(
            exc,
            "response",
            None,
        )

        if response is not None:

            try:

                error_data = response.json()

                error_detail = error_data.get(
                    "detail"
                )

            except (
                ValueError,
                AttributeError,
            ):

                pass

        if error_detail:

            st.warning(
                f"Backend: {error_detail}"
            )

        else:

            st.warning(
                "Please make sure the RecoverAI backend is running."
            )

        st.stop()


# ============================================================
# ANALYSIS RESULT
# ============================================================

if st.session_state.result:

    result = st.session_state.result

    st.markdown(
        '<div class="section-title">AI Analysis</div>',
        unsafe_allow_html=True,
    )

    analysis_col1, analysis_col2, analysis_col3 = st.columns(3)

    recovery_score = result.get(
        "recovery_score",
        0,
    )

    recommended_action = result.get(
        "recommended_action",
        "unknown",
    )

    analysis_reason = result.get(
        "reason",
        "",
    )

    with analysis_col1:

        st.metric(
            "Recovery Score",
            f"{recovery_score}/100",
        )

    with analysis_col2:

        st.metric(
            "Recommended Action",
            recommended_action,
        )

    with analysis_col3:

        if recovery_score >= 80:

            level = "High"

        elif recovery_score >= 50:

            level = "Medium"

        else:

            level = "Low"

        st.metric(
            "Recovery Probability",
            level,
        )

    st.info(
        analysis_reason
    )


    # ========================================================
    # ACTION CENTER
    # ========================================================

    st.markdown(
        '<div class="section-title">Recovery Action Center</div>',
        unsafe_allow_html=True,
    )

    payment_already_recovered = (
        st.session_state.action_result is not None
        and st.session_state.action_result.get(
            "payment_recovered"
        ) is True
    )


    # ========================================================
    # NO ACTION
    # ========================================================

    if recommended_action == "no_action":

        st.success(
            "No recovery action required — payment is already successful."
        )


    # ========================================================
    # RETRY PAYMENT
    # ========================================================

    elif recommended_action == "retry_payment":

        if payment_already_recovered:

            st.success(
                "Payment has already been recovered. No further action is required."
            )

        else:

            st.write(
                "The AI recommends retrying the payment."
            )

            retry_success = st.checkbox(
                "Simulate successful payment retry",
                value=True,
            )

            if st.button(
                "Execute Retry Payment",
                use_container_width=True,
            ):

                try:

                    response = requests.post(
                        f"{API_URL}/execute-action",
                        params={
                            "analysis_id": st.session_state.analysis_id,
                            "action": "retry_payment",
                            "retry_success": retry_success,
                        },
                        timeout=10,
                    )

                    response.raise_for_status()

                    action_result = response.json()

                    st.session_state.action_result = action_result

                    st.rerun()

                except requests.RequestException as exc:

                    st.error(
                        "Unable to execute recovery action."
                    )

                    error_detail = None

                    response = getattr(
                        exc,
                        "response",
                        None,
                    )

                    if response is not None:

                        try:

                            error_data = response.json()

                            error_detail = error_data.get(
                                "detail"
                            )

                        except (
                            ValueError,
                            AttributeError,
                        ):

                            pass

                    if error_detail:

                        st.warning(
                            f"Backend: {error_detail}"
                        )

                    else:

                        st.warning(
                            "Please make sure the RecoverAI backend is running."
                        )


    # ========================================================
    # PAYMENT REMINDER
    # ========================================================

    elif recommended_action == "send_payment_reminder":

        if payment_already_recovered:

            st.success(
                "Payment has already been recovered. No further action is required."
            )

        else:

            st.write(
                "The AI recommends sending a payment reminder."
            )

            if st.button(
                "Send Payment Reminder",
                use_container_width=True,
            ):

                try:

                    response = requests.post(
                        f"{API_URL}/execute-action",
                        params={
                            "analysis_id": st.session_state.analysis_id,
                            "action": "send_payment_reminder",
                        },
                        timeout=10,
                    )

                    response.raise_for_status()

                    action_result = response.json()

                    st.session_state.action_result = action_result

                    st.rerun()

                except requests.RequestException as exc:

                    st.error(
                        "Unable to execute recovery action."
                    )

                    error_detail = None

                    response = getattr(
                        exc,
                        "response",
                        None,
                    )

                    if response is not None:

                        try:

                            error_data = response.json()

                            error_detail = error_data.get(
                                "detail"
                            )

                        except (
                            ValueError,
                            AttributeError,
                        ):

                            pass

                    if error_detail:

                        st.warning(
                            f"Backend: {error_detail}"
                        )

                    else:

                        st.warning(
                            "Please make sure the RecoverAI backend is running."
                        )


    # ========================================================
    # ALTERNATE PAYMENT
    # ========================================================

    elif recommended_action == "suggest_alternate_payment":

        if payment_already_recovered:

            st.success(
                "Payment has already been recovered. No further action is required."
            )

        else:

            st.write(
                "The AI recommends suggesting an alternate payment method."
            )

            if st.button(
                "Suggest Alternate Payment",
                use_container_width=True,
            ):

                try:

                    response = requests.post(
                        f"{API_URL}/execute-action",
                        params={
                            "analysis_id": st.session_state.analysis_id,
                            "action": "suggest_alternate_payment",
                        },
                        timeout=10,
                    )

                    response.raise_for_status()

                    action_result = response.json()

                    st.session_state.action_result = action_result

                    st.rerun()

                except requests.RequestException as exc:

                    st.error(
                        "Unable to execute recovery action."
                    )

                    error_detail = None

                    response = getattr(
                        exc,
                        "response",
                        None,
                    )

                    if response is not None:

                        try:

                            error_data = response.json()

                            error_detail = error_data.get(
                                "detail"
                            )

                        except (
                            ValueError,
                            AttributeError,
                        ):

                            pass

                    if error_detail:

                        st.warning(
                            f"Backend: {error_detail}"
                        )

                    else:

                        st.warning(
                            "Please make sure the RecoverAI backend is running."
                        )


    # ========================================================
    # AGGRESSIVE PERSONALIZED REMINDER
    # ========================================================

    elif recommended_action == "aggressive_personalized_reminder":

        if payment_already_recovered:

            st.success(
                "Payment has already been recovered. No further action is required."
            )

        else:

            st.write(
                "The AI recommends an aggressive personalized reminder."
            )

            if st.button(
                "Send Personalized Reminder",
                use_container_width=True,
            ):

                try:

                    response = requests.post(
                        f"{API_URL}/execute-action",
                        params={
                            "analysis_id": st.session_state.analysis_id,
                            "action": "aggressive_personalized_reminder",
                        },
                        timeout=10,
                    )

                    response.raise_for_status()

                    action_result = response.json()

                    st.session_state.action_result = action_result

                    st.rerun()

                except requests.RequestException as exc:

                    st.error(
                        "Unable to execute recovery action."
                    )

                    error_detail = None

                    response = getattr(
                        exc,
                        "response",
                        None,
                    )

                    if response is not None:

                        try:

                            error_data = response.json()

                            error_detail = error_data.get(
                                "detail"
                            )

                        except (
                            ValueError,
                            AttributeError,
                        ):

                            pass

                    if error_detail:

                        st.warning(
                            f"Backend: {error_detail}"
                        )

                    else:

                        st.warning(
                            "Please make sure the RecoverAI backend is running."
                        )


    # ========================================================
    # ESCALATE TO HUMAN
    # ========================================================

    elif recommended_action == "escalate_to_human":

        if payment_already_recovered:

            st.success(
                "Payment has already been recovered. No further action is required."
            )

        else:

            st.warning(
                "The AI recommends escalating this case to human support."
            )

            if st.button(
                "Escalate to Human",
                use_container_width=True,
            ):

                try:

                    response = requests.post(
                        f"{API_URL}/execute-action",
                        params={
                            "analysis_id": st.session_state.analysis_id,
                            "action": "escalate_to_human",
                        },
                        timeout=10,
                    )

                    response.raise_for_status()

                    action_result = response.json()

                    st.session_state.action_result = action_result

                    st.rerun()

                except requests.RequestException as exc:

                    st.error(
                        "Unable to execute recovery action."
                    )

                    error_detail = None

                    response = getattr(
                        exc,
                        "response",
                        None,
                    )

                    if response is not None:

                        try:

                            error_data = response.json()

                            error_detail = error_data.get(
                                "detail"
                            )

                        except (
                            ValueError,
                            AttributeError,
                        ):

                            pass

                    if error_detail:

                        st.warning(
                            f"Backend: {error_detail}"
                        )

                    else:

                        st.warning(
                            "Please make sure the RecoverAI backend is running."
                        )


# ============================================================
# ACTION RESULT
# ============================================================

if st.session_state.action_result:

    action_result = st.session_state.action_result

    st.markdown(
        '<div class="section-title">Recovery Result</div>',
        unsafe_allow_html=True,
    )

    action_data = action_result.get(
        "action_result",
        {},
    )

    action_status = action_data.get(
        "status",
        "unknown",
    )

    action_message = action_data.get(
        "message",
        "",
    )

    payment_recovered = action_result.get(
        "payment_recovered"
    )

    if payment_recovered is True:

        st.success(
            "Payment recovered successfully."
        )

    elif action_status == "success":

        if action_message:

            st.success(
                action_message
            )

    else:

        if action_message:

            st.error(
                action_message
            )

        if payment_recovered is False:

            st.warning(
                "Payment was not recovered."
            )


# ============================================================
# TRANSACTION HISTORY
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">Transaction History</div>',
    unsafe_allow_html=True,
)

if transactions:

    for transaction in transactions:

        with st.expander(
            f"Transaction #{transaction.get('id')} — "
            f"{transaction.get('customer')}"
        ):

            col1, col2, col3 = st.columns(3)

            with col1:

                st.write(
                    f"**Amount:** ₹{transaction.get('amount')}"
                )

                st.write(
                    f"**Status:** {transaction.get('status')}"
                )

                st.write(
                    f"**Reason:** {transaction.get('reason')}"
                )

            with col2:

                st.write(
                    f"**Recovery Score:** "
                    f"{transaction.get('recovery_score')}/100"
                )

                st.write(
                    f"**Action:** "
                    f"{transaction.get('action')}"
                )

                st.write(
                    f"**Action Status:** "
                    f"{transaction.get('action_status')}"
                )

            with col3:

                st.write(
                    f"**Payment Recovered:** "
                    f"{transaction.get('payment_recovered')}"
                )

else:

    st.info(
        "No recovery transactions yet."
    )