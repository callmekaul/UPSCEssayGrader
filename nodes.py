from criteria_registry import Criterion, CRITERIA
from schemas import EssayState
from utils import count_words, extract_paragraphs, normalize_text
from models import model, structured_model, calibration_model

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
You are a UPSC examiner evaluating an essay written under timed exam conditions.

Criterion: {name}

Focus:
{instruction}

Scoring rubric:
{rubric}

Essay metadata:
- Word count: {meta['word_count']}
- Paragraph count: {meta['paragraph_count']}
- Average paragraph length: {meta['avg_paragraph_words']} words

Evaluation Guidelines:
- Evaluate relative to what is expected from a full-length UPSC essay.
- Assign a score from 0-10 based strictly on the rubric bands.
- Strong paragraph-level writing must not be mistaken for essay-level quality.
- High scores require sustained development across the essay.
- Provide up to 3 strengths.
- Provide up to 3 weaknesses (leave empty if score is 10).
- Write concise examiner-style feedback (2-3 sentences).

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
            "scores": [response.score]
        }

    return evaluator

def calibration_node(state: EssayState):

    evaluations = state["evaluations"]
    essay = state["essay"]

    word_count = state["metadata"]["word_count"]
    paragraph_count = state["metadata"]["paragraph_count"]

    score_map = {
        k: v.score for k, v in evaluations.items()
    }

    prompt = f"""
You are moderating scores assigned by examiners to ensure they are proportionate to a UPSC essay.

Typical UPSC essays are 900-1200 words with multiple developed paragraphs.

Essay metadata:
- Word count: {word_count}
- Paragraphs: {paragraph_count}

Essay:
{essay}

Current scores:
{score_map}

Task:
Adjust scores ONLY if they appear inflated relative to essay scale,
development, or completeness.

Guidelines:
- Short or underdeveloped responses should not receive high bands.
- Strong paragraph-level writing should not be mistaken for essay-level quality.
- Do NOT increase scores — only reduce inflated ones if necessary.
- Preserve relative differences between criteria when possible.

Return adjusted scores and a brief rationale.
"""

    result = calibration_model.invoke(prompt)

    # overwrite scores safely
    for item in result.adjusted_scores:
        if item.criterion not in evaluations.keys():
            continue  
        evaluations[item.criterion].score = item.score


    return {
        "evaluations": evaluations,
        "calibration_rationale": result.rationale
    }

def overall_evaluation(state: EssayState):

    evaluations = state["evaluations"]
    metadata = state["metadata"]

    # ALWAYS compute total here
    total_score = sum(e.score for e in evaluations.values())

    # Build dynamic evaluation summary
    evaluation_block = ""

    for criterion in CRITERIA:
        e = evaluations[criterion.key]

        evaluation_block += f"""
{criterion.name}:
Score: {e.score}/10
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

Total Score: {total_score} / 50

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
        "total_score": total_score
    }
