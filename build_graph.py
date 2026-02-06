from langgraph.graph import StateGraph, START, END
from schemas import EssayState
from criteria_registry import CRITERIA
from nodes import metadata_node, build_evaluator, overall_evaluation


def build_evaluation_graph():

    graph = StateGraph(EssayState)

    graph.add_node("metadata", metadata_node)

    # ---------- Add criterion nodes ----------
    for criterion in CRITERIA:
        graph.add_node(
            criterion.key,
            build_evaluator(criterion)
        )

    # ---------- Add overall evaluation node ----------
    graph.add_node("overall_evaluation", overall_evaluation)

    # ---------- START → metadata ----------
    graph.add_edge(START, "metadata")

    # ---------- metadata → all evaluators ----------
    for criterion in CRITERIA:
        graph.add_edge("metadata", criterion.key)

    # ---------- all evaluators → overall_evaluation → END ----------
    for criterion in CRITERIA:
        graph.add_edge(criterion.key, "overall_evaluation")

    graph.add_edge("overall_evaluation", END)

    return graph.compile()

workflow = build_evaluation_graph()
