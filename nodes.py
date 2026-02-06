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

    return {
        "metadata": {
            "word_count": total_words,
            "paragraph_count": para_count,
            "avg_paragraph_words": round(total_words / max(para_count, 1), 1),
        }
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
You are a strict UPSC examiner evaluating an essay written under timed exam conditions.

Criterion: {name}

Focus:
{instruction}

Rating rubric:
{rubric}

Essay metadata:
- Word count: {meta['word_count']}
- Paragraph count: {meta['paragraph_count']}
- Average paragraph length: {meta['avg_paragraph_words']} words

Evaluation Guidelines:

- Choose ONE rating only from:
  **Excellent, Good, Average, Poor**

- Do NOT hedge between ratings.
- If uncertain, choose the lower rating.
- Do not reward basic competence — reward clear distinction.
- Evaluate relative to expectations from a full-length UPSC essay.
- Strong paragraph-level writing must NOT be mistaken for essay-level quality.
- High ratings require sustained development across the essay.

Feedback Requirements:

- Write concise examiner-style feedback (2-3 sentences).
- Explicitly justify why the essay belongs in this rating instead of the rating above it.


Essay Topic:
{topic}

Essay:
{essay}
"""

        response = structured_model.invoke(prompt)

        return {
            "evaluations": {
                key: response
            }
        }

    return evaluator


def grammar_node(state):

    essay = state["essay"]

    prompt = f"""
You are a strict examiner evaluating grammar and language quality.

Your task has TWO parts:

1 Identify clear grammatical mistakes.
2 Assign an overall rating using the rubric.

-------------------------

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

If errors exist in later paragraphs, you MUST identify them.

-------------------------

SEVERITY GUIDE:

error → harms readability or correctness  
warning → awkward but understandable  

Ignore trivial punctuation unless it affects meaning.

-------------------------

RATING RULE:

Frequent grammatical errors with "error" severity that disrupt readability MUST NOT be rated above Average.

Minor mistakes severity that do not affect comprehension should not heavily penalize the score.

Prioritize readability over perfection.

-------------------------

Essay:
{essay}
"""

    response = structured_model.invoke(prompt)

    return {
        "evaluations": {
            "grammar": response
        }
    }


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
You are a senior UPSC examiner writing the final assessment of a candidate's essay.

Essay metadata:
- Word count: {metadata['word_count']}
- Paragraphs: {metadata['paragraph_count']}
- Avg paragraph length: {metadata['avg_paragraph_words']}

Essay Topic:
{state["topic"]}

Criterion-wise evaluation:
{evaluation_block}

Write a professional final assessment

Produce THREE outputs:

1. Overall Strengths (3-5 points)
   - Identify the most important essay-level qualities.
   - Synthesize across criteria — do NOT repeat section feedback.
   - Focus on structural or intellectual positives.

2. Overall Weaknesses (3-5 points)
   - Identify the issues that most constrained the essay's quality.
   - Prioritize high-impact flaws over minor ones.
   - Weaknesses must imply how the essay could be improved.

3. Final Assessment (120-180 words)
   - Write like a senior UPSC examiner.
   - Be authoritative, precise, and unsentimental.
   - Comment on development, coherence, depth, and maturity.
   - Do NOT list bullets.
   - Do NOT mention ratings or evaluation mechanics.
   - Do NOT repeat earlier feedback verbatim.

   
Use easy to understand language suitable for Indian Students.
"""

    overall_result = overall_model.invoke(prompt)

    return {
    "overall": overall_result.final_assessment,
    "strengths": overall_result.overall_strengths,
    "weaknesses": overall_result.overall_weaknesses,
    }
