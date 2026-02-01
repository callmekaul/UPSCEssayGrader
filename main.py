from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import TypedDict, Annotated
from dotenv import load_dotenv
import operator, re

from criteria_registry import CRITERIA, Criterion

load_dotenv()

def merge_dicts(a, b):
    return {**a, **b}

def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n")      # Windows → Unix
    text = re.sub(r"\n{3,}", "\n\n", text) # collapse large gaps
    return text.strip()

def extract_paragraphs(text: str) -> list[str]:
    paragraphs = re.split(r"\n+", text.strip())
    return [p.strip() for p in paragraphs if p.strip()]

def count_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))

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
    evaluations: Annotated[dict[str, EvaluationSchema], merge_dicts]
    overall: str
    scores: Annotated[list[int], operator.add]
    total_score: int

def build_metadata(text: str) -> EssayMetadata:

    text = normalize_text(text)

    paragraphs = extract_paragraphs(text)

    word_counts = [count_words(p) for p in paragraphs] or [0]

    total_words = sum(word_counts)
    para_count = len(paragraphs)

    return {
        "word_count": total_words,
        "paragraph_count": para_count,
        "avg_paragraph_words": round(total_words / max(para_count, 1), 1),
    }

def build_evaluator(criterion: Criterion):

    key = criterion.key
    name = criterion.name
    instruction = criterion.instruction
    rubric = criterion.rubric

    def evaluator(state: EssayState):

        topic = state["topic"]
        essay = state["essay"]
        meta = state["metadata"]

        prompt = f"""
You are a UPSC examiner evaluating an essay written under timed exam conditions.

Criterion: {name}

Focus:
{instruction}

Scoring rubric:
{rubric}

Essay metadata:
- Word count: {meta['word_count']}
- Paragraph count: {meta['paragraph_count']}
- Average paragraph length: {meta['avg_paragraph_words']} words

Evaluation Guidelines:
- Evaluate relative to what is expected from a full-length UPSC essay.
- Assign a score from 0-10 based strictly on the rubric bands.
- Strong paragraph-level writing must not be mistaken for essay-level quality.
- High scores require sustained development across the essay.
- Provide up to 3 strengths.
- Provide up to 3 weaknesses (leave empty if score is 10).
- Write concise examiner-style feedback (2-3 sentences).

Essay Topic:
{topic}

Essay:
{essay}
"""

        response = structured_model.invoke(prompt)

        return {
            "evaluations": {
                key: response
            },
            "scores": [response.score]
        }

    return evaluator

def metadata_node(state: EssayState):

    essay = state["essay"]

    metadata = build_metadata(essay)

    return {
        "metadata": metadata
    }


def overall_evaluation(state: EssayState):

    evaluations = state["evaluations"]
    metadata = state["metadata"]

    # ALWAYS compute total here
    total_score = sum(e.score for e in evaluations.values())

    # Build dynamic evaluation summary
    evaluation_block = ""

    for criterion in CRITERIA:
        e = evaluations[criterion.key]

        evaluation_block += f"""
{criterion.name}:
Score: {e.score}/10
Strengths: {e.strengths}
Weaknesses: {e.weaknesses}
Feedback: {e.feedback}

"""

    prompt = f"""
You are a senior UPSC examiner writing the final assessment of a candidate's essay.

Essay metadata:
- Word count: {metadata['word_count']}
- Paragraphs: {metadata['paragraph_count']}
- Avg paragraph length: {metadata['avg_paragraph_words']}

Essay Topic:
{state["topic"]}

Criterion-wise evaluation:
{evaluation_block}

Total Score: {total_score} / 50


Write a professional final assessment that:

- Synthesizes the major strengths.
- Identifies the most critical weaknesses affecting the score.
- Comments on essay-level qualities such as development, structure, and depth.
- Avoids repeating criterion feedback verbatim.
- Sounds like a real examiner — not an AI summary.
- Remains concise but authoritative (120–180 words).

Do NOT mention scoring mechanics.
Do NOT list bullets.
Write in cohesive paragraphs.
"""

    overall_feedback = model.invoke(prompt).content

    return {
        "overall": overall_feedback,
        "total_score": total_score
    }


def build_evaluation_graph():

    graph = StateGraph(EssayState)

    graph.add_node("metadata", metadata_node)

    # ---------- Add criterion nodes ----------
    for criterion in CRITERIA:
        graph.add_node(
            criterion.key,
            build_evaluator(criterion)
        )

    # ---------- Add overall node ----------
    graph.add_node("overall_evaluation", overall_evaluation)

    # ---------- START → metadata ----------
    graph.add_edge(START, "metadata")

    # ---------- metadata → all evaluators ----------
    for criterion in CRITERIA:
        graph.add_edge("metadata", criterion.key)

    # ---------- all evaluators → overall ----------
    for criterion in CRITERIA:
        graph.add_edge(criterion.key, "overall_evaluation")

    # ---------- overall → END ----------
    graph.add_edge("overall_evaluation", END)

    return graph.compile()

def pretty_print(result: dict):

    print("\n" + "=" * 70)
    print("📝 UPSC ESSAY EVALUATION REPORT")
    print("=" * 70)

    # ---------- Essay ----------
    print("\n📄 ESSAY:\n")
    print(result["essay"])

    print("\n" + "-" * 70)
    print("📊 DIMENSION-WISE EVALUATION")
    print("-" * 70)

    evaluations = result["evaluations"]

    for i, criterion in enumerate(CRITERIA, start=1):

        eval_obj = evaluations[criterion.key]

        print(f"\n{i}️⃣ {criterion.name.upper()} ({eval_obj.score}/10)")

        # ---------- Strengths ----------
        if eval_obj.strengths:
            print("\n✅ Strengths:")
            for s in eval_obj.strengths:
                print(f"  • {s}")

        # ---------- Weaknesses ----------
        if eval_obj.weaknesses:
            print("\n⚠️ Weaknesses:")
            for w in eval_obj.weaknesses:
                print(f"  • {w}")

        # ---------- Feedback ----------
        print("\n🧾 Examiner Feedback:")
        print(f"  {eval_obj.feedback}")

        print("\n" + "-" * 70)

    # ---------- Overall ----------
    print("\n🧠 OVERALL ASSESSMENT")
    print("-" * 70)
    print(result["overall"])

    print("\n" + "=" * 70)
    print(f"🏁 TOTAL SCORE: {result['total_score']} / 50")
    print("=" * 70 + "\n")

    print(f"Word Count: {result['metadata']['word_count']}")
    print(f"Paragraph Count: {result['metadata']['paragraph_count']}")
    print(f"Average Paragraph Length: {result['metadata']['avg_paragraph_words']} words")
    


model = ChatOpenAI(model="gpt-4o-mini")
structured_model = model.with_structured_output(EvaluationSchema)

graph = StateGraph(EssayState)

workflow = build_evaluation_graph()

topic = "Life is a journey, not a destination."
essay = """Human life has always been a mystery that thinkers, poets, and philosophers have tried to unravel through the ages. From the earliest civilizations to the modern world, the question of what constitutes a meaningful life has preoccupied the human mind. One of the most profound insights emerging from this reflection is the realization that life is best seen as a journey, not as a destination. To perceive life as a journey is to value growth over arrival, process over outcome, and experience over mere achievement. It is to live fully in the present moment, to embrace both joy and suffering as parts of an evolving process, and to recognize that the essence of life lies not in where we end up, but in how we travel through its varied paths.
Every success is followed by new challenges, every fulfillment by fresh desires. To see life as a journey is to accept this impermanence with courage and joy. It is to celebrate the unfolding of each moment, to learn from every twist and turn, and to move forward with hope. As T.S. Eliot wrote, “We shall not cease from exploration, and the end of all our exploring will be to arrive where we started and know the place for the first time.” Thus, the greatest wisdom lies in walking the path with awareness, gratitude, and love - for in the journey itself, we find our true destination."""

initial_state: EssayState = {
    "topic": topic,
    "essay": essay
}

result = workflow.invoke(initial_state)
pretty_print(result)