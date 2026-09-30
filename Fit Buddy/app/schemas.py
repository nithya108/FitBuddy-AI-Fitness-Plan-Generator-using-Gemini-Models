from typing import Literal

from pydantic import BaseModel, Field, field_validator


Goal = Literal[
    "weight loss",
    "muscle gain",
    "general wellness",
    "flexibility",
    "endurance"
]


Intensity = Literal[
    "low",
    "medium",
    "high"
]


class UserInput(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=120
    )

    user_id: str = Field(
        min_length=2,
        max_length=100,
        pattern=r"^[A-Za-z0-9_-]+$"
    )

    age: int = Field(
        ge=13,
        le=100
    )

    weight: float = Field(
        gt=20,
        le=500
    )

    goal: Goal

    intensity: Intensity

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        return " ".join(value.strip().split())


class FeedbackRequest(BaseModel):
    user_id: str = Field(
        min_length=2,
        max_length=100
    )

    feedback: str = Field(
        min_length=5,
        max_length=2000
    )


class UserResponse(BaseModel):
    id: int
    user_id: str
    name: str
    age: int
    weight: float
    goal: str
    intensity: str


class PlanResponse(BaseModel):
    user: UserResponse
    original_plan: str
    updated_plan: str | None
    nutrition_tip: str
    feedback: str | None