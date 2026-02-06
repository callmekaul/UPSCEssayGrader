from langgraph.graph import StateGraph, START, END
from schemas import EssayState
from criteria_registry import CRITERIA
from nodes import metadata_node, introConclusion_extractor, build_evaluator, overall_evaluation

def checkValidEssay(state: EssayState):

    if not state["overall"]:
        return "intro_conclusion"
    else:
        return END


def build_evaluation_graph():

    graph = StateGraph(EssayState)

    # ----------------------- GRAPH NODES -----------------------
    
    # PRE-EVALUATION NODES
    graph.add_node("metadata", metadata_node)
    graph.add_node("intro_conclusion", introConclusion_extractor)

    # EVALUATION CRITERIA NODES
    for criterion in CRITERIA:
        graph.add_node(
            criterion.key,
            build_evaluator(criterion)
        )

    # OVERALL EVALUATION NODE
    graph.add_node("overall_evaluation", overall_evaluation)

    # ----------------------- GRAPH EDGES -----------------------

    # START > metadata > checkValidEssay ? intro_conclusion : END
    graph.add_edge(START, "metadata")
    graph.add_conditional_edges("metadata", checkValidEssay)

    # intro_conclusion > evaluators
    for criterion in CRITERIA:
        graph.add_edge("intro_conclusion", criterion.key)

    # evaluators > overall_evaluation
    for criterion in CRITERIA:
        graph.add_edge(criterion.key, "overall_evaluation")

    # overall_evaluation > END
    graph.add_edge("overall_evaluation", END)

    return graph.compile()

workflow = build_evaluation_graph()
