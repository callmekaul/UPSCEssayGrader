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
        instruction="""
Evaluate how accurately the essay interprets the topic and sustains focus on it across the entire essay.
""",
        rubric="""
9-10: Precisely interprets the topic and sustains sharp relevance throughout a fully developed essay.

7-8: Largely relevant with minor digressions; demonstrates clear understanding of the topic.

5-6: Broadly related but shows drift, generalisation, or inconsistent linkage to the topic.

3-4: Partial relevance; misunderstands important aspects of the topic.

0-2: Misinterprets the topic or does not resemble an essay response.
"""
    ),

    Criterion(
        key="thought_depth",
        name="Depth of Thought",
        instruction="""
Evaluate the intellectual maturity, analytical depth, and originality demonstrated across the essay.
Reward sustained reasoning rather than isolated good points.
""",
        rubric="""
9-10: Demonstrates sustained, nuanced, and original reasoning across a fully developed essay.

7-8: Logical and balanced analysis with some depth, though largely predictable.

5-6: Basic arguments with limited analytical development.

3-4: Superficial, descriptive, or repetitive thinking.

0-2: Extremely shallow response or fragmented content that does not resemble an essay.
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
        rubric="""
9-10: Exceptionally well-structured essay with a clear introduction, multiple logically ordered paragraphs, smooth transitions, and a strong conclusion.

7-8: Well-organized essay with minor structural lapses.

5-6: Recognizable essay structure but uneven development or weak transitions.

3-4: Major structural deficiencies such as missing introduction, missing conclusion, or very limited paragraphing.

0-2: Does not resemble an essay (e.g., single paragraph, notes, or fragment).
"""
    ),

    Criterion(
        key="multidimensionality",
        name="Multi-dimensional Coverage",
        instruction="""
Evaluate the breadth of perspectives explored in the essay.
Reward meaningful integration of multiple dimensions rather than token mentions.
""",
        rubric="""
9-10: Explores multiple dimensions (social, political, economic, ethical, etc.) in an integrated manner across the essay.

7-8: Covers several relevant dimensions but with uneven depth.

5-6: Limited dimensional exploration; relies heavily on one perspective.

3-4: Largely one-dimensional.

0-2: Extremely narrow response or insufficient content to demonstrate dimensional thinking.
"""
    ),

    Criterion(
        key="examples",
        name="Examples & Evidence",
        instruction="""
Evaluate the specificity, relevance, and integration of examples used to support arguments throughout the essay.
""",
        rubric="""
9-10: Uses precise, relevant examples seamlessly throughout the essay to strengthen arguments.

7-8: Provides relevant examples but integration may be inconsistent.

5-6: Examples are generic, sparse, or unevenly used.

3-4: Few weak examples or largely unsupported claims.

0-2: No meaningful examples or insufficient content to demonstrate evidence-based writing.
"""
    ),
)
