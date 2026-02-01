import re
from criteria_registry import CRITERIA

def merge_dicts(a, b):
    return {**a, **b}

def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n")      # Windows → Unix
    text = re.sub(r"\n{3,}", "\n\n", text) # collapse large gaps
    return text.strip()

def extract_paragraphs(text: str) -> list[str]:
    paragraphs = re.split(r"\n+", text.strip())
    return [p.strip() for p in paragraphs if p.strip()]

def count_words(text: str) -> int:
        return len(re.findall(r"\b\w+\b", text))

def pretty_print(result: dict):

    print("\n" + "=" * 70)
    print("📝 UPSC ESSAY EVALUATION REPORT")
    print("=" * 70)

    # ---------- Essay ----------
    print("\n📄 ESSAY:\n")
    print(result["essay"])

    print("\n" + "-" * 70)
    print("📊 DIMENSION-WISE EVALUATION")
    print("-" * 70)

    evaluations = result["evaluations"]

    for i, criterion in enumerate(CRITERIA, start=1):

        eval_obj = evaluations[criterion.key]

        print(f"\n{i}️⃣ {criterion.name.upper()} ({eval_obj.score}/10)")

        # ---------- Strengths ----------
        if eval_obj.strengths:
            print("\n✅ Strengths:")
            for s in eval_obj.strengths:
                print(f"  • {s}")

        # ---------- Weaknesses ----------
        if eval_obj.weaknesses:
            print("\n⚠️ Weaknesses:")
            for w in eval_obj.weaknesses:
                print(f"  • {w}")

        # ---------- Feedback ----------
        print("\n🧾 Examiner Feedback:")
        print(f"  {eval_obj.feedback}")

        print("\n" + "-" * 70)

    # ---------- Overall ----------
    print("\n🧠 OVERALL ASSESSMENT")
    print("-" * 70)
    print(result["overall"])

    print("\n" + "=" * 70)
    print(f"🏁 TOTAL SCORE: {result['total_score']} / 50")
    print("=" * 70 + "\n")

    print(f"Word Count: {result['metadata']['word_count']}")
    print(f"Paragraph Count: {result['metadata']['paragraph_count']}")
    print(f"Average Paragraph Length: {result['metadata']['avg_paragraph_words']} words")
    
