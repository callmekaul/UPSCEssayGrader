from pydantic import BaseModel, Field
from typing import TypedDict, Annotated
import operator


class EvaluationSchema(BaseModel):
    score: int = Field(
        ge=0,
        le=10,
        description="Score awarded for this criterion on a 0-10 scale."
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
    scores: Annotated[list[int], operator.add]
    total_score: int

class AdjustedScore(BaseModel):
    criterion: str
    score: int = Field(ge=0, le=10)

class CalibrationResult(BaseModel):
    adjusted_scores: list[AdjustedScore]
    rationale: str