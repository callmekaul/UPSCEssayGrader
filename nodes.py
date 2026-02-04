from criteria_registry import Criterion, CRITERIA
from schemas import EssayState
from utils import count_words, extract_paragraphs, normalize_text
from models import model, structured_model

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

Strength / Weakness Requirements:

- No Strength if rating is Poor.
- No Weakness if rating is Excellent.
- At least 2 Strengths for Good or Excellent ratings.
- At least 2 Weaknesses for Average or Poor ratings.
- Each point must reference a specific observable trait in the essay.
- Avoid generic phrases like "good analysis."
- Weaknesses must have a corrective actionable advice.


Essay Topic:
{topic}

Essay:
{essay}
"""

        response = structured_model.invoke(prompt)

        return {
            "evaluations": {
                key: response
            },
            "ratings": [response.rating]
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
Strengths: {e.strengths}
Weaknesses: {e.weaknesses}
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

Write a professional final assessment that:

- Synthesizes the major strengths.
- Identifies the most critical weaknesses affecting the score.
- Comments on essay-level qualities such as development, structure, and depth.
- Avoids repeating criterion feedback verbatim.
- Sounds like a real examiner — not an AI summary.
- Remains concise but authoritative (120-180 words).

Do NOT mention scoring mechanics.
Do NOT list bullets.
Write in cohesive paragraphs.
"""

    overall_feedback = model.invoke(prompt).content

    return {
        "overall": overall_feedback,
    }
