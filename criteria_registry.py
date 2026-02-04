from dataclasses import dataclass

@dataclass
class Criterion:
    key: str
    name: str
    instruction: str
    rubric: str


CRITERIA: tuple[Criterion, ...] = (

    Criterion(
        key="topic_relevance",
        name="Topic Relevance",
        instruction = """
Evaluate whether the essay directly responds to the given topic.

FIRST perform an Off-Topic Check:

Ask:
- Would a human examiner immediately recognize this as a response to the prompt?
- Is the core subject of the essay the same as the topic?

If the essay primarily discusses a different subject, it is OFF-TOPIC.

IMPORTANT RULE:
An off-topic essay MUST be rated Poor.
Do NOT assign Average for partial philosophical overlap or abstract connections.

Topic relevance requires SUBJECT MATCH, not thematic creativity.
Do not infer relevance unless it is explicit and central.
""",
        rubric = """
Excellent: Directly and precisely answers the topic. The central theme is unmistakably aligned with the prompt, and nearly every major idea reinforces it.

Good: Clearly relevant to the topic. The essay demonstrates a solid understanding of the prompt, with only minor generalisation that does not weaken alignment.

Average: Broadly related but somewhat generic. The essay could fit multiple similar topics with moderate changes, indicating partial but not sharp interpretation.

Poor: Weak, superficial, or minimal connection to the topic. Large portions drift away from the prompt, or the response could easily belong to a different question.
"""


    ),

    Criterion(
        key="thought_depth",
        name="Depth of Thought",
        instruction="""
Evaluate the intellectual maturity, analytical depth, and originality demonstrated across the essay.
Reward sustained reasoning rather than isolated good points.
""",
        rubric = """
Excellent: Demonstrates mature, nuanced, and sustained reasoning. Ideas are explored rather than merely stated, showing clear intellectual engagement.

Good: Logical and clear analysis with some depth, though insights may be predictable rather than original.

Average: Relies on straightforward or familiar arguments with limited exploration or analytical development.

Poor: Superficial, repetitive, or largely descriptive thinking with little evidence of reasoning.
"""

    ),

    Criterion(
        key="presentation",
        name="Presentation & Structure",
        instruction="""
Evaluate whether the response functions as a well-structured essay.
Check for introduction, logical body progression, paragraphing, coherence, and conclusion.
Responses that do not resemble an essay should fall in the lowest bands regardless of language quality.
Local paragraph coherence should not be mistaken for essay-level structure.
""",
        rubric = """
Excellent: Functions as a cohesive essay with a clear introduction, logically ordered paragraphs, smooth progression of ideas, and a purposeful conclusion.

Good: Well-organized overall with recognizable essay structure, though transitions or balance may occasionally falter.

Average: Shows basic essay structure but development is uneven, with weak progression or limited paragraph control.

Poor: Does not function as a proper essay — major structural elements are missing or ideas appear disjointed.
"""

    ),

    Criterion(
        key="multidimensionality",
        name="Multi-dimensional Coverage",
        instruction="""
Evaluate the breadth of perspectives explored in the essay.
Reward meaningful integration of multiple dimensions rather than token mentions.
""",
        rubric = """
Excellent: Integrates multiple relevant dimensions (e.g., social, ethical, philosophical, economic) in a natural and connected manner.

Good: Covers several perspectives but with uneven emphasis or depth.

Average: Demonstrates limited breadth and relies primarily on a single perspective.

Poor: Extremely narrow response with little to no evidence of dimensional thinking.
"""

    ),

    Criterion(
        key="examples",
        name="Examples & Evidence",
        instruction="""
Evaluate the specificity, relevance, and integration of examples used to support arguments throughout the essay.
""",
        rubric = """
Excellent: Uses specific, relevant examples that are smoothly integrated and clearly strengthen the arguments.

Good: Provides appropriate examples, though integration may occasionally feel mechanical or uneven.

Average: Examples are generic, sparse, or not consistently connected to the argument.

Poor: Lacks meaningful examples or relies on unsupported assertions.
"""
    ),
)
