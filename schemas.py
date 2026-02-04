from pydantic import BaseModel, Field
from typing import Literal, TypedDict, Annotated


class EvaluationSchema(BaseModel):
    rating: Literal["Excellent", "Good", "Average", "Poor"] = Field(
        description="Overall rating for this criterion based strictly on the rubric."
    )

    feedback: str = Field(
        description="2-3 sentence examiner-style summary explaining the evaluation."
    )

class GrammarAnnotation(BaseModel):
    quote: str
    issue: str
    suggestion: str
    severity: Literal["error", "warning"]

class GrammarEvaluation(BaseModel):
    rating: Literal["Excellent", "Good", "Average", "Poor"]
    feedback: str
    annotations: list[GrammarAnnotation]

class EssayMetadata(TypedDict):
    word_count: int
    paragraphs: int
    avg_paragraph_words: float

class OverallEvaluationSchema(BaseModel):

    overall_strengths: list[str] = Field(
        description="3-5 major essay-level strengths from sections having higher than average rating. EMpty if none"
    )

    overall_weaknesses: list[str] = Field(
        description="3-5 major essay-level weaknesses from sections having lower than good rating. Empty if none"
    )

    final_assessment: str = Field(
        description="120-180 word senior examiner assessment."
    )

class EssayState(TypedDict):
    topic: str
    essay: str
    metadata: EssayMetadata
    evaluations: Annotated[dict[str, EvaluationSchema], lambda a, b: {**a, **b}]
    strengths: list[str]
    weaknesses: list[str]
    overall: str
    annotations: list[dict]