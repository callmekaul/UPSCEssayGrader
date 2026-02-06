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
