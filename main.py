from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import TypedDict, Annotated
import operator
from dotenv import load_dotenv

from criteria_registry import CRITERIA, Criterion

load_dotenv()

def merge_dicts(a, b):
    return {**a, **b}

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

class EssayState(TypedDict):
    essay: str
    evaluations: Annotated[dict[str, EvaluationSchema], merge_dicts]
    overall: str
    scores: Annotated[list[int], operator.add]
    total_score: int

def build_evaluator(criterion: Criterion):

    def evaluator(state: EssayState):

        prompt = f"""
        Strictly evaluate the essay for {criterion.name}.

        Scoring rubric:
        {criterion.rubric}

        Return:
        - score
        - strengths
        - weaknesses
        - feedback (2-3 sentences)

        Essay:
        {state['essay']}
        """

        response = structured_model.invoke(prompt)

        return {
            "evaluations": {
                criterion.key: response
            },
            "scores": [response.score]
        }

    return evaluator

def overall_evaluation(state: EssayState):
    total = sum(state['scores'])
    prompt = f"""
    Based on the following evaluations, provide a concise and summarized feedback for the essay:

    Topic Relevance Feedback: {state['evaluations']['topic_relevance'].feedback}
    Thought Depth Feedback: {state['evaluations']['thought_depth'].feedback}
    Presentation Feedback: {state['evaluations']['presentation'].feedback}
    Multidimensionality Feedback: {state['evaluations']['multidimensionality'].feedback}
    Examples Feedback: {state['evaluations']['examples'].feedback}

    Total Score: {total} out of 50
    """
    overall_evaluation = model.invoke(prompt).content
    return {'overall': overall_evaluation, 'total_score': total}

def build_evaluation_graph():

    graph = StateGraph(EssayState)

    # ---------- Add criterion nodes ----------
    for criterion in CRITERIA:
        graph.add_node(
            criterion.key,
            build_evaluator(criterion)
        )

    # ---------- Add overall node ----------
    graph.add_node("overall_evaluation", overall_evaluation)

    # ---------- START → all evaluators ----------
    for criterion in CRITERIA:
        graph.add_edge(START, criterion.key)

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


model = ChatOpenAI(model="gpt-4o-mini")
structured_model = model.with_structured_output(EvaluationSchema)

graph = StateGraph(EssayState)

workflow = build_evaluation_graph()

essay = """Human life has always been a mystery that thinkers, poets, and philosophers have tried to unravel through the ages. From the earliest civilizations to the modern world, the question of what constitutes a meaningful life has preoccupied the human mind. One of the most profound insights emerging from this reflection is the realization that life is best seen as a journey, not as a destination. To perceive life as a journey is to value growth over arrival, process over outcome, and experience over mere achievement. It is to live fully in the present moment, to embrace both joy and suffering as parts of an evolving process, and to recognize that the essence of life lies not in where we end up, but in how we travel through its varied paths. 

Every success is followed by new challenges, every fulfillment by fresh desires. To see life as a journey is to accept this impermanence with courage and joy. It is to celebrate the unfolding of each moment, to learn from every twist and turn, and to move forward with hope. As T.S. Eliot wrote, “We shall not cease from exploration, and the end of all our exploring will be to arrive where we started and know the place for the first time.” Thus, the greatest wisdom lies in walking the path with awareness, gratitude, and love - for in the journey itself, we find our true destination."""

inital_state: EssayState = {
    'essay': essay
}

result = workflow.invoke(inital_state)

pretty_print(result)