from pydantic import BaseModel, Field
from typing import Literal, TypedDict, Annotated


class EvaluationSchema(BaseModel):
    rating: Literal["Excellent", "Good", "Average", "Poor"] = Field(
        description="Overall rating for this criterion based strictly on the rubric."
    )

    strengths: list[str] = Field(
        default_factory=list,
        description="Specific aspects executed well."
    )

    weaknesses: list[str] = Field(
        default_factory=list,
        description="Specific issues that limited the score."
    )

    feedback: str = Field(
        description="2-3 sentence examiner-style summary explaining the evaluation."
    )

class EssayMetadata(TypedDict):
    word_count: int
    paragraphs: int
    avg_paragraph_words: float

class EssayState(TypedDict):
    topic: str
    essay: str
    metadata: EssayMetadata
    evaluations: Annotated[dict[str, EvaluationSchema], lambda a, b: {**a, **b}]
    overall: str
