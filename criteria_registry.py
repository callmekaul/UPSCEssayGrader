from dataclasses import dataclass

@dataclass
class Criterion:
    key: str
    name: str
    instruction: str
    rubric: str


CRITERIA: tuple[Criterion, ...] = (

    Criterion(
        key="content_depth",
        name="Content Depth & Analysis",
        instruction = """
Evaluate the depth, analytical strength, and intellectual seriousness of the essay.

Focus on whether ideas are DEVELOPED rather than merely mentioned.

MANDATORY EVIDENCE RULE:
You MUST support your evaluation with 2-4 direct quotes from the essay.
Select short, high-signal excerpts that reveal the level of reasoning.

Ask:
- Are arguments explored with explanation and implications?
- Does the essay move beyond obvious statements?
- Is there evidence of critical thinking?

IMPORTANT:
Do not reward verbosity. Length is not depth.
A long but shallow essay must score lower than a concise but analytical one.
""",
        rubric = """
Excellent: Exceptionally analytical and intellectually mature. Arguments are explored in depth with clear reasoning and implications.

Good: Demonstrates solid analysis with reasonably developed arguments, though some ideas could be pushed further.

Average: Contains basic explanation but relies heavily on surface-level observations.

Poor: Largely descriptive or generic with minimal reasoning.
"""
    ),

    Criterion(
        key="relevance_focus",
        name="Relevance & Thematic Focus",
        instruction = """
Evaluate whether the essay remains tightly aligned with the topic.

FIRST perform an Off-Topic Check:

Ask:
- Would a human UPSC examiner immediately recognize this as a response to the prompt?
- Is the central thread consistently tied to the topic?

MANDATORY RULE:
If the essay is primarily about a different subject, it MUST be rated Poor.

MANDATORY EVIDENCE RULE:
Provide direct quotes that demonstrate alignment OR drift.

Do NOT infer relevance from abstract philosophical language.
Subject match is required.
""",
        rubric = """
Excellent: Laser-focused on the topic. Nearly every major argument reinforces the central theme.

Good: Clearly relevant with only minor digressions.

Average: Broadly related but generic enough to fit multiple topics.

Poor: Weak alignment or substantially off-topic.
"""
    ),

    Criterion(
        key="structure_coherence",
        name="Structure & Coherence",
        instruction = """
Evaluate whether the response functions as a cohesive essay.

Check for:
- A purposeful introduction
- Logical paragraph progression
- Clear transitions
- A synthesizing conclusion

MANDATORY EVIDENCE RULE:
Quote lines that show structural intent (e.g., framing statements, transitions, conclusions).

IMPORTANT:
Local paragraph clarity is NOT the same as essay-level coherence.
An essay that reads like disconnected mini-articles should score lower.
""",
        rubric = """
Excellent: Cohesive and logically architected with strong progression from introduction to conclusion.

Good: Recognizable structure with mostly logical flow, though transitions may occasionally weaken.

Average: Basic structure exists but progression feels uneven or mechanical.

Poor: Disjointed, poorly ordered, or missing major structural elements.
"""
    ),

    Criterion(
        key="multidimensionality",
        name="Multi-dimensional Thinking",
        instruction = """
Evaluate the breadth and integration of perspectives.

High-scoring UPSC essays typically explore multiple dimensions such as:
social, ethical, philosophical, political, economic, historical, or psychological.

MANDATORY EVIDENCE RULE:
Quote passages that demonstrate dimensional thinking.

IMPORTANT:
Token mentions do NOT count.
A dimension must influence the argument to be credited.
""",
        rubric = """
Excellent: Seamlessly integrates multiple dimensions that deepen the analysis.

Good: Covers several perspectives but with uneven development.

Average: Limited breadth; largely relies on one dominant lens.

Poor: Extremely narrow with little evidence of layered thinking.
"""
    ),

    Criterion(
        key="originality_insight",
        name="Originality & Insight",
        instruction = """
Evaluate the presence of independent thinking and fresh interpretation.

Ask:
- Does the essay avoid clichés?
- Are familiar ideas reframed in a thoughtful way?
- Does the writer demonstrate intellectual ownership?

MANDATORY EVIDENCE RULE:
Quote lines that reveal originality OR conventional thinking.

IMPORTANT:
Originality does NOT mean being contrarian.
Reward thoughtful framing, not novelty for its own sake.
""",
        rubric = """
Excellent: Displays distinctive insight and thoughtful framing that elevates the essay.

Good: Shows some independent thinking, though many ideas remain conventional.

Average: Mostly predictable arguments with limited intellectual freshness.

Poor: Derivative, cliché-driven, or formulaic.
"""
    ),

    Criterion(
        key="examples_evidence",
        name="Examples & Substantiation",
        instruction = """
Evaluate the specificity, relevance, and argumentative role of examples.

Examples should STRENGTHEN reasoning — not function as decorative additions.

MANDATORY EVIDENCE RULE:
Quote at least one example used by the writer and evaluate how effectively it supports the claim.

IMPORTANT:
Generic references (e.g., "history shows", "many leaders") should be treated as weak evidence.
""",
        rubric = """
Excellent: Uses specific, relevant examples that are smoothly embedded into the argument.

Good: Appropriate examples are present, though integration may occasionally feel mechanical.

Average: Examples are generic, sparse, or weakly connected.

Poor: Assertions are largely unsupported.
"""
    ),

    Criterion(
        key="language_clarity",
        name="Language, Clarity & Expression",
        instruction = """
Evaluate readability, precision, and grammatical control.

Focus on whether language ENABLES thought rather than obstructing it.

MANDATORY EVIDENCE RULE:
Quote lines that illustrate strengths OR problems in expression.

IMPORTANT:
Do NOT reward unnecessarily complex vocabulary.
Clarity is superior to ornamentation.
""",
        rubric = """
Excellent: Clear, precise, and fluent language with strong sentence control.

Good: Generally clear with minor errors that do not hinder comprehension.

Average: Noticeable language issues or awkward phrasing that occasionally disrupt flow.

Poor: Frequent errors or unclear writing that obstructs understanding.
"""
    ),

    Criterion(
        key="argument_consistency",
        name="Argument Consistency & Logical Integrity",
        instruction = """
Evaluate whether the essay maintains logical stability.

Check for:
- Internal contradictions
- Sudden ideological shifts
- Unsupported leaps in reasoning
- Claims that do not follow from prior arguments

MANDATORY EVIDENCE RULE:
Quote lines that either demonstrate strong logical continuity OR reveal breaks.

IMPORTANT:
Sophisticated essays can acknowledge tension without becoming inconsistent.
Do not confuse nuance with contradiction.
""",
        rubric = """
Excellent: Logically consistent with tightly connected arguments.

Good: Mostly coherent with minor reasoning gaps.

Average: Several logical jumps or partially supported claims.

Poor: Contradictory or unstable reasoning.
"""
    ),

    Criterion(
        key="conclusion_quality",
        name="Conclusion Quality & Synthesis",
        instruction = """
Evaluate how effectively the essay closes.

A strong UPSC conclusion should synthesize rather than summarize.

Ask:
- Does it elevate the discussion?
- Does it provide direction, balance, or philosophical closure?

MANDATORY EVIDENCE RULE:
Quote the concluding lines and assess their effectiveness.

IMPORTANT:
Introducing brand-new arguments in the conclusion should be penalized.
""",
        rubric = """
Excellent: Insightful synthesis that provides intellectual closure.

Good: Solid ending that reinforces the essay's message.

Average: Functional but predictable summary-style ending.

Poor: Abrupt, underdeveloped, or missing conclusion.
"""
    ),

    Criterion(
        key="grammar",
        name="Grammar, Language & Expression",
        instruction = """
Evaluate grammar, language quality, and clarity.

Your task has TWO parts:
1. Identify clear grammatical mistakes and language issues.
2. Assign an overall rating using the rubric.

STRICT ANNOTATION RULES:
- Quote the EXACT phrase from the essay.
- DO NOT paraphrase.
- DO NOT invent text.
- Each quote MUST appear verbatim in the essay.
- Keep quotes SHORT (3-12 words).
- Only annotate high-confidence mistakes.

If unsure → DO NOT annotate.

DISTRIBUTION REQUIREMENT:
You MUST distribute annotations across the ENTIRE essay length:
- Scan the FIRST paragraphs for issues
- Scan MIDDLE paragraphs for issues
- CRITICALLY: Scan the FINAL paragraphs and conclusion for issues
- Do NOT concentrate all annotations in early sections
- Ensure coverage from start to finish

SEVERITY GUIDE:
error → harms readability or correctness
warning → awkward but understandable

Ignore trivial punctuation unless it affects meaning.
""",
        rubric = """
Excellent: Clear, precise, and fluent language with strong sentence control and minimal errors.

Good: Generally clear with minor grammatical or stylistic errors that do not hinder comprehension.

Average: Noticeable language issues or awkward phrasing that occasionally disrupt flow.

Poor: Frequent grammatical errors that disrupt readability or understandability.
"""
    ),

)