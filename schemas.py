from pydantic import BaseModel, Field
from typing import Literal, TypedDict, Annotated


class Annotation(BaseModel):
    paragraph_number: int = Field(
        description="1-indexed paragraph number where this quote appears."
    )
    quote: str = Field(
        description="MUST be 5-25 words maximum. The exact phrase from the essay. Do NOT paraphrase or expand."
    )
    issue: str = Field(
        description="Concise identification of the problem. Be direct and specific."
    )
    impact: str = Field(
        description="1 sentence: why this issue weakens the essay or hurts the score."
    )
    suggestion: str = Field(
        description="A concrete rewrite or specific fix. Show exactly what to change, not vague advice."
    )
    severity: Literal["error", "warning"]

class EvaluationSchema(BaseModel):
    rating: Literal["Excellent", "Good", "Average", "Poor"] = Field(
        description="Overall rating for this criterion based strictly on the rubric."
    )

    feedback: str = Field(
        description="2-3 sentence examiner-style summary explaining the evaluation."
    )
    annotations: list[Annotation] = Field(
        description="List of specific issues identified in the essay related to this criterion."
    )

class EssayMetadata(TypedDict):
    word_count: int
    paragraphs: int
    avg_paragraph_words: float

class OverallEvaluationSchema(BaseModel):

    overall_strengths: list[str] = Field(
        description="3-5 major essay-level strengths from sections having higher than average rating. Empty if none"
    )

    overall_weaknesses: list[str] = Field(
        description="3-5 major essay-level weaknesses from sections having lower than good rating. Empty if none"
    )

    final_assessment: str = Field(
        description="120-180 word senior examiner assessment."
    )

    essay_score: int = Field(
        description="Overall score out of 100. Independently assessed based on all criterion feedbacks, strengths, and weaknesses. Not a simple average of ratings."
    )

class EssayState(TypedDict):
    topic: str
    essay: str
    intro: str
    conclusion: str
    metadata: EssayMetadata
    evaluations: Annotated[dict[str, EvaluationSchema], lambda a, b: {**a, **b}]
    strengths: list[str]
    weaknesses: list[str]
    overall: str
    score: int