import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "recoverai.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():

    with get_connection() as connection:

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL,
                reason TEXT NOT NULL,
                previous_successful_payments INTEGER NOT NULL,
                previous_failed_attempts INTEGER NOT NULL,
                recovery_score REAL NOT NULL,
                recommended_action TEXT NOT NULL,
                ai_reason TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL UNIQUE,
                customer TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL,
                reason TEXT NOT NULL,
                recovery_score REAL NOT NULL,
                action TEXT NOT NULL,
                action_status TEXT NOT NULL,
                payment_recovered TEXT NOT NULL,
                FOREIGN KEY (analysis_id) REFERENCES analyses(id)
            )
            """
        )


# ============================================================
# ANALYSIS
# ============================================================

def save_analysis(
    customer,
    amount,
    status,
    reason,
    previous_successful_payments,
    previous_failed_attempts,
    recovery_score,
    recommended_action,
    ai_reason,
):

    with get_connection() as connection:

        cursor = connection.execute(
            """
            INSERT INTO analyses (
                customer,
                amount,
                status,
                reason,
                previous_successful_payments,
                previous_failed_attempts,
                recovery_score,
                recommended_action,
                ai_reason
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                customer,
                amount,
                status,
                reason,
                previous_successful_payments,
                previous_failed_attempts,
                recovery_score,
                recommended_action,
                ai_reason,
            ),
        )

        return cursor.lastrowid


def get_analysis(analysis_id):

    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT *
            FROM analyses
            WHERE id = ?
            """,
            (analysis_id,),
        ).fetchone()

        if row:
            return dict(row)

        return None


def get_analysis_count():

    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM analyses
            """
        ).fetchone()

        return row["count"]


# ============================================================
# TRANSACTIONS
# ============================================================

def save_transaction(
    analysis_id,
    customer,
    amount,
    status,
    reason,
    recovery_score,
    action,
    action_status,
    payment_recovered,
):

    with get_connection() as connection:

        connection.execute(
            """
            INSERT INTO transactions (
                analysis_id,
                customer,
                amount,
                status,
                reason,
                recovery_score,
                action,
                action_status,
                payment_recovered
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                analysis_id,
                customer,
                amount,
                status,
                reason,
                recovery_score,
                action,
                action_status,
                payment_recovered,
            ),
        )


def get_transaction_by_analysis_id(analysis_id):

    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT
                id,
                analysis_id,
                customer,
                amount,
                status,
                reason,
                recovery_score,
                action,
                action_status,
                payment_recovered
            FROM transactions
            WHERE analysis_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (analysis_id,),
        ).fetchone()

        if row:
            return dict(row)

        return None


def get_transactions():

    with get_connection() as connection:

        rows = connection.execute(
            """
            SELECT
                id,
                analysis_id,
                customer,
                amount,
                status,
                reason,
                recovery_score,
                action,
                action_status,
                payment_recovered
            FROM transactions
            ORDER BY id DESC
            """
        ).fetchall()

        return [dict(row) for row in rows]


def clear_transactions():

    with get_connection() as connection:

        connection.execute(
            "DELETE FROM transactions"
        )

        connection.execute(
            "DELETE FROM analyses"
        )