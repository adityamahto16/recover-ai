from typing import Literal

from pydantic import BaseModel, Field


class Payment(BaseModel):
    customer: str = Field(min_length=1)

    amount: float = Field(
        gt=0,
        allow_inf_nan=False,
    )

    status: Literal[
        "failed",
        "success",
    ]

    reason: str = Field(min_length=1)

    previous_successful_payments: int = Field(
        ge=0,
    )

    previous_failed_attempts: int = Field(
        ge=0,
    )