from criteria_registry import Criterion, CRITERIA
from schemas import EssayState
from utils import count_words, extract_paragraphs, normalize_text
from models import structured_model, overall_model

def metadata_node(state: EssayState):

    text = normalize_text(state["essay"])

    paragraphs = extract_paragraphs(text)

    word_counts = [count_words(p) for p in paragraphs] or [0]

    total_words = sum(word_counts)
    para_count = len(paragraphs)

    if total_words < 700:
        return {
            "overall": "Essay is too short for meaningful evaluation. UPSC essays typically require around 1000-1200 words. Please expand your essay to meet the expected length." ,
            "strengths": [],
            "weaknesses": []
        }
    elif total_words > 2000:
        return {
            "overall": "Essay exceeds typical length for UPSC exams. Aim for around 1000-1200 words. Consider condensing your essay to focus on the most relevant points and improve clarity." ,
            "strengths": [],
            "weaknesses": []
        }
    else:
        return {
            "metadata": {
                "word_count": total_words,
                "paragraph_count": para_count,
                "avg_paragraph_words": round(total_words / max(para_count, 1), 1),
            }
        }

def introConclusion_extractor(state: EssayState):

    text = normalize_text(state["essay"])

    paragraphs = extract_paragraphs(text)

    intro = paragraphs[0] if paragraphs else ""
    conclusion = paragraphs[-1] if len(paragraphs) > 1 else ""

    return {
        "intro": intro,
        "conclusion": conclusion
    }

def _number_paragraphs(essay: str) -> str:
    """Prepend [P1], [P2], ... to each paragraph for LLM paragraph referencing."""
    paragraphs = extract_paragraphs(essay)
    return "\n\n".join(f"[P{i}] {p}" for i, p in enumerate(paragraphs, 1))


def build_evaluator(criterion: Criterion):

    key = criterion.key
    name = criterion.name
    instruction = criterion.instruction
    rubric = criterion.rubric

    def evaluator(state: EssayState):

        topic = state["topic"]
        essay = state["essay"]
        meta = state["metadata"]
        numbered_essay = _number_paragraphs(essay)

        prompt = f"""
You are a STRICT UPSC examiner. Rate honestly — NOT generously.

Criterion: {name}

Focus:
{instruction}

Rating Rubric:
{rubric}

Essay metadata:
- Word count: {meta['word_count']}
- Paragraph count: {meta['paragraph_count']}
- Average paragraph length: {meta['avg_paragraph_words']} words

RATING CALIBRATION (Use these EXACT standards):

Excellent (RARE):
- Essay demonstrates exceptional depth OR originality for this criterion
- Few or NO weaknesses; work is demonstrably superior
- Not the default for competent work
- Examples: brilliant insight, seamless execution, standout examples

Good (COMMON for decent work):
- Solid execution with minor room for improvement
- Competent but not exceptional
- Meets UPSC standards well
- Some sentences/ideas could be strengthened

Average (COMMON for mediocre work):
- Noticeable limitations or gaps
- Work is functional but noticeably weaker than "Good"
- Significant room for improvement
- Ideas are present but underdeveloped OR poorly connected

Poor (RARE, for serious issues):
- Major weaknesses that undermine the criterion
- Barely meets minimum standards or falls short
- Serious logical, structural, or evidence issues

EVALUATION PROCESS:

Step 1: Read the ENTIRE essay. Find 2-3 specific quotes that show the essay's strength OR weakness on this criterion.

Step 2: Compare the essay against the rubric. Which band does it genuinely fit?

Step 3: Ask yourself: "Would a harsh but fair UPSC examiner rate this the same way?"

Step 4: If your first instinct is "Good", PAUSE. Could it actually be Average (too many minor issues)? Could it be Excellent (unusual strength)? Or is Good genuinely right?

Feedback Requirements:

Write 2 sentences of simple, direct feedback:
- Sentence 1: One concrete observation about what you see (e.g., "Your examples are too generic" or "Your argument flows logically")
- Sentence 2: ONE specific way to improve (e.g., "Replace 'many historians' with an actual historian name and detail")

Use simple English. Avoid jargon. Be direct. Make it actionable.

ANNOTATION RULES (CRITICAL):

Identify MAJOR issues. Focus on HIGH-IMPACT problems that directly relate to the rating.

Each annotation MUST include ALL of these fields:
- paragraph_number: The paragraph number (1-indexed) where the quote appears. Use the [P1], [P2] labels in the essay below.
- quote: 3-15 words, copy-pasted EXACTLY from the essay (do NOT include the [P1] prefix)
- issue: 1 sentence identifying the specific problem
- impact: 1 sentence explaining WHY this hurts the essay's score or quality
- suggestion: A concrete rewrite or specific replacement. Show EXACTLY what to write instead — not vague advice like "be more specific" or "consider adding examples"
- severity: "error" (major, directly hurts the rating) or "warning" (minor, room for improvement)

DO NOT annotate:
- Trivial details
- Minor variations when meaning is clear
- Redundant issues already highlighted

Example of GOOD annotation:
  paragraph_number: 3
  quote: "many scholars agree on this"
  issue: Generic reference lacks specificity and credibility
  impact: UPSC examiners expect evidence-backed claims; vague references weaken your argument
  suggestion: Replace with "As Amartya Sen argues in his capability approach, development must prioritize..."
  severity: warning

Example of BAD annotation (too vague):
  quote: "the example shows"
  issue: Could be more specific
  suggestion: Consider being more specific
  → SKIP — suggestion is not actionable

Essay Topic:
{topic}

Essay (paragraphs numbered for reference — do NOT include [P#] tags in your quotes):
{numbered_essay}
"""

        response = structured_model.invoke(prompt)

        return {
            "evaluations": {
                key: response
            }
        }

    return evaluator


def overall_evaluation(state: EssayState):

    evaluations = state["evaluations"]
    metadata = state["metadata"]

    # Build dynamic evaluation summary
    evaluation_block = ""

    for criterion in CRITERIA:
        e = evaluations[criterion.key]

        evaluation_block += f"""
{criterion.name}:
Rating: {e.rating}
Feedback: {e.feedback}
"""

    prompt = f"""
You are a SENIOR UPSC examiner writing the final assessment. Be consistent, precise, and authoritative.

Essay Metadata:
- Word count: {metadata['word_count']}
- Paragraphs: {metadata['paragraph_count']}
- Avg paragraph length: {metadata['avg_paragraph_words']}

Essay Topic:
{state["topic"]}

Criterion-wise Evaluation Summary:
{evaluation_block}

TASK: Produce FOUR outputs based ONLY on the evaluations above:

1. **Overall Strengths** (3-5 bullet points)
   - Extract the highest-rated criterion areas
   - Synthesize into essay-level insights
   - Example: "Strong use of historical examples to ground abstract arguments"
   - Do NOT repeat generic praise

2. **Overall Weaknesses** (3-5 bullet points)
   - Focus on criteria that scored Average or Poor
   - Be SPECIFIC: Reference the actual weakness patterns
   - Make each weakness imply a concrete improvement
   - Example: "Limited exploration of counterarguments weakens coherence"
   - Do NOT be vague ("Could be better")

3. **Final Assessment** (120-180 words)
   - Write like a senior examiner reviewing a candidate's performance
   - Reference specific strengths AND weaknesses from above
   - Be authoritative and precise
   - Avoid: ratings, mechanics, repetition of earlier feedback
   - Use clear, direct language appropriate for Indian students
   - Do NOT list bullets; write in prose

4. **Essay Score** (integer 0-100)
   - Calculate INDEPENDENTLY based on the criterion evaluations, strengths, and weaknesses
   - This is NOT a simple average or sum of ratings
   - Use your holistic judgment: How would this essay perform in a real UPSC exam?
   - Guidelines:
     * 90-100: Exceptional (mostly Excellent ratings, brilliant execution)
     * 80-89: Very Good (mostly Good/Excellent, minor weaknesses)
     * 70-79: Good (mixed Good/Average, manageable issues)
     * 60-69: Average (significant weaknesses, several Average ratings)
     * 50-59: Below Average (many Average/Poor ratings, major issues)
     * Below 50: Poor (predominantly Poor ratings, serious flaws)
   - Consider the IMPACT of weaknesses on overall quality
   - Consider the DEPTH and CONSISTENCY of strengths

CONSISTENCY RULE:
Synthesize the criterion ratings into a coherent overall picture.
If most ratings are "Average" or "Poor", the final assessment should reflect limited overall quality.
Do NOT write an encouraging tone if scores don't support it.
"""

    overall_result = overall_model.invoke(prompt)

    return {
    "overall": overall_result.final_assessment,
    "strengths": overall_result.overall_strengths,
    "weaknesses": overall_result.overall_weaknesses,
    "score": overall_result.essay_score,
    }
