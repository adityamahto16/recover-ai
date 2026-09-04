# RecoverAI

RecoverAI is a local prototype for turning a failed-payment signal into a recommended recovery action. It evaluates payment history and failure context, assigns a recovery score, recommends an action, and records analysis and recovery activity in SQLite. A Streamlit dashboard provides a simple operator workflow over the FastAPI backend.

> RecoverAI simulates recovery decisions and actions. It does not connect to a payment processor, send real messages, or process money.

## Features

- Validates incoming payment data with Pydantic.
- Scores recovery likelihood on a 0–100 scale using payment amount and previous successful and failed attempts.
- Recommends contextual recovery actions for timeouts, insufficient funds, and declined cards.
- Supports simulated retries, reminders, alternate-payment suggestions, and human escalation.
- Stores payment analyses and action history in a local SQLite database.
- Prevents a second recovery action from being recorded for the same analysis.
- Includes a Streamlit dashboard with analysis inputs, result cards, action controls, and history metrics.
- Exposes interactive API documentation through FastAPI.

## Tech stack

| Layer | Technology |
| --- | --- |
| API | Python, FastAPI, Uvicorn |
| Validation | Pydantic |
| UI | Streamlit |
| HTTP client | Requests |
| Storage | SQLite (Python standard library) |

## Project structure

```text
recover-ai/
├── backend/
│   ├── main.py       # FastAPI routes and application startup
│   ├── models.py     # Payment request model and validation rules
│   ├── agent.py      # Recovery scoring and recommendation logic
│   ├── execute.py    # Simulated recovery-action executor
│   └── database.py   # SQLite schema and data-access functions
├── frontend/
│   └── app.py        # Streamlit operator dashboard
├── recoverai.db      # Local SQLite database (created/used at runtime)
└── README.md
```

## Prerequisites

- Python 3.10 or later
- `pip`

## Setup

Clone the repository and create an isolated environment:

```bash
git clone <repository-url>
cd recover-ai
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

Install the application dependencies:

```bash
python -m pip install fastapi "uvicorn[standard]" pydantic streamlit requests
```

## Run the application

Start the API from the repository root:

```bash
uvicorn backend.main:app --reload --port 8003
```

Then, in a second terminal with the same virtual environment activated, start the dashboard:

```bash
streamlit run frontend/app.py
```

Open the Streamlit URL printed in the terminal (normally `http://localhost:8501`). The API is available at `http://127.0.0.1:8003`, and its interactive OpenAPI documentation is at `http://127.0.0.1:8003/docs`.

The frontend currently has its API address set to `http://127.0.0.1:8003` in `frontend/app.py`. Keep the backend on that port unless you update that setting.

## API reference

### `GET /`

Returns a basic health message.

```json
{"message": "RecoverAI API is running"}
```

### `POST /payments`

Analyzes a payment and persists its recommendation. Request body:

```json
{
  "customer": "Rahul",
  "amount": 1999.0,
  "status": "failed",
  "reason": "timeout",
  "previous_successful_payments": 5,
  "previous_failed_attempts": 0
}
```

Validation rules: `customer` and `reason` cannot be blank, `amount` must be a finite value greater than zero, history counters must be non-negative, and `status` is either `failed` or `success`.

On success, the response includes an `analysis_id`, the submitted payment, a recommended action, reason, and recovery score. Possible recommendations are:

- `no_action`
- `retry_payment`
- `send_payment_reminder`
- `aggressive_personalized_reminder`
- `suggest_alternate_payment`
- `escalate_to_human`

### `GET /analysis/{analysis_id}`

Retrieves a saved analysis. `analysis_id` must be a positive integer. Returns `400` for an invalid ID and `404` when no matching analysis exists.

### `POST /execute-action`

Executes one simulated recovery action for an analysis. Parameters are sent as query parameters:

```text
POST /execute-action?analysis_id=1&action=retry_payment&retry_success=true
```

`action` must be one of the supported recovery actions listed above except `no_action`. `retry_success` is optional and applies to `retry_payment`; it defaults to `true`. A successful simulated retry is the only action considered a recovered payment. The endpoint returns `409` if an unrecovered analysis already has an action recorded.

### `GET /transactions`

Returns the action history and count of analyzed payments:

```json
{
  "transactions": [],
  "analyzed_payments": 0
}
```

### `DELETE /transactions`

Removes all locally stored transaction and analysis history. This is intended for resetting the local demo environment.

## Demo flow

1. Start the backend and dashboard.
2. In the dashboard sidebar, enter a customer, amount, payment status, failure reason, and payment history.
3. Select **Analyze Payment** to receive a recovery score and recommended action.
4. Use the recovery action panel to simulate the recommendation. For a timeout, choose a successful retry to demonstrate a recovered payment.
5. Review the dashboard metrics and transaction history.
6. Select **Clear Transaction History** when you want to reset the local demo data.

You can also exercise the API directly:

```bash
curl -X POST http://127.0.0.1:8003/payments \
  -H "Content-Type: application/json" \
  -d '{"customer":"Rahul","amount":1999,"status":"failed","reason":"timeout","previous_successful_payments":5,"previous_failed_attempts":0}'
```

## Testing

There is currently no automated test suite in the repository. At minimum, verify that the Python modules compile:

```bash
python -m py_compile backend/*.py frontend/app.py
```

For functional testing, start both services and use the dashboard or FastAPI docs to test a failed `timeout` payment, execute `retry_payment`, inspect `GET /transactions`, and reset with `DELETE /transactions`.

## Security and data handling

- This is a development prototype, not a production payment service.
- The API has no authentication, authorization, rate limiting, audit trail, encryption, or role separation.
- SQLite data is stored locally in `recoverai.db`; do not place sensitive customer or payment data in a shared or unprotected workspace.
- Recovery actions are simulations only. Add authenticated payment-provider integrations, webhook verification, secrets management, idempotency controls, structured logging, and production-grade database operations before any real deployment.
- Avoid storing card numbers, CVVs, tokens, or other regulated payment data in this application.

## Project status

**Prototype / in active development.** The decision logic, UI, and local-storage design are suitable for demonstrating the workflow, but the project is not production ready.

Current implementation note: the route layer calls `save_analysis` and `save_transaction` with signatures that do not match the current functions in `backend/database.py`. As a result, an end-to-end `POST /payments` or action execution may fail until those persistence contracts are aligned. The API reference above describes the intended interface; resolve this mismatch and add automated tests before relying on the demo flow.

## License

No license has been specified for this repository. Add a license before distributing or using the project outside its intended development context.
