from langgraph.graph import StateGraph, START, END
from schemas import EssayState
from criteria_registry import CRITERIA
from nodes import metadata_node, build_evaluator, calibration_node, overall_evaluation


def build_evaluation_graph():

    graph = StateGraph(EssayState)

    graph.add_node("metadata", metadata_node)

    # ---------- Add criterion nodes ----------
    for criterion in CRITERIA:
        graph.add_node(
            criterion.key,
            build_evaluator(criterion)
        )

    # ---------- Add calibration and overall node ----------
    graph.add_node("calibration", calibration_node)
    graph.add_node("overall_evaluation", overall_evaluation)

    # ---------- START → metadata ----------
    graph.add_edge(START, "metadata")

    # ---------- metadata → all evaluators ----------
    for criterion in CRITERIA:
        graph.add_edge("metadata", criterion.key)

    # ---------- all evaluators → calibration ----------
    for criterion in CRITERIA:
        graph.add_edge(criterion.key, "calibration")

    # ---------- calibration → overall → END ----------
    graph.add_edge("calibration", "overall_evaluation")
    graph.add_edge("overall_evaluation", END)

    return graph.compile()

workflow = build_evaluation_graph()
