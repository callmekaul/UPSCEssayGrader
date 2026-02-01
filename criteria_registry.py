from dataclasses import dataclass

@dataclass
class Criterion:
    key: str
    name: str
    rubric: str


CRITERIA = [

    Criterion(
        key="topic_relevance",
        name="Topic Relevance",
        rubric="""
9-10: Fully and deeply addresses the topic  
7-8: Mostly relevant with minor digressions  
5-6: Broadly related but noticeable drift  
3-4: Partial relevance  
0-2: Largely irrelevant
"""
    ),

    Criterion(
        key="thought_depth",
        name="Depth of Thought",
        rubric="""
9-10: Nuanced and original reasoning  
7-8: Logical and balanced  
5-6: Basic arguments  
3-4: Superficial ideas  
0-2: No analysis
"""
    ),

    Criterion(
        key="presentation",
        name="Presentation & Structure",
        rubric="""
9-10: Exceptionally well-structured, fluent, and polished throughout.
7-8: Clear and coherent with minor lapses.
5-6: Understandable but uneven or mechanically written.
3-4: Weak flow, poor structure, or frequent language issues.
0-2: Very difficult to follow or poorly written.
"""
    ),

    Criterion(
        key="multidimensionality",
        name="Multi-dimensional Coverage",
        rubric="""
9-10: Integrates many dimensions meaningfully  
7-8: Several dimensions covered  
5-6: Limited dimensionality  
3-4: One-dimensional  
0-2: Extremely narrow
"""
    ),

    Criterion(
        key="examples",
        name="Examples & Evidence",
        rubric="""
9-10: Precise and well-integrated examples  
7-8: Relevant but uneven  
5-6: Generic examples  
3-4: Weak examples  
0-2: No meaningful examples
"""
    ),
]
