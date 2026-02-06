from collections import Counter
from pydoc import html
import re
from criteria_registry import CRITERIA

# Criterion color mapping for annotations and feedback panel
CRITERION_COLORS = {
    "content_depth": {"bg": "#1a5f7a", "underline": "#00bcd4", "light": "#e0f7fa"},           # Cyan
    "relevance_focus": {"bg": "#6a1b9a", "underline": "#e040fb", "light": "#f3e5f5"},         # Purple
    "structure_coherence": {"bg": "#1565c0", "underline": "#42a5f5", "light": "#e3f2fd"},     # Blue
    "multidimensionality": {"bg": "#0b5394", "underline": "#64b5f6", "light": "#f1f8e9"},     # Light Blue
    "originality_insight": {"bg": "#c62828", "underline": "#ef5350", "light": "#ffebee"},     # Red
    "examples_evidence": {"bg": "#2e7d32", "underline": "#66bb6a", "light": "#e8f5e9"},       # Green
    "language_clarity": {"bg": "#e65100", "underline": "#ff9800", "light": "#fff3e0"},        # Orange
    "argument_consistency": {"bg": "#00695c", "underline": "#26a69a", "light": "#e0f2f1"},    # Teal
    "conclusion_quality": {"bg": "#c2185b", "underline": "#ec407a", "light": "#fce4ec"},      # Pink
    "grammar": {"bg": "#8b0000", "underline": "#ff4d4d", "light": "#fff3e0"},                 # Dark Red
}

def get_criterion_color(criterion_key):
    """Get color for a criterion, fallback to neutral gray"""
    return CRITERION_COLORS.get(criterion_key, {"bg": "#444", "underline": "#aaa", "light": "#f5f5f5"})

def merge_dicts(a, b):
    return {**a, **b}

def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def extract_paragraphs(text: str) -> list[str]:
    paragraphs = re.split(r"\n+", text.strip())
    return [p.strip() for p in paragraphs if p.strip()]

def count_words(text: str) -> int:
        return len(re.findall(r"\b\w+\b", text))

def resolve_annotations(text, annotations, allow_overlaps: bool = False):

    """Resolve annotation quotes to character spans in `text`.

    If `allow_overlaps` is False (default) this function preserves the
    original behavior and skips annotations that overlap previously
    resolved spans. If True, all matching quotes are returned even when
    their spans overlap — useful for per-criterion views where we want
    to retain more annotations instead of discarding collisions.
    """

    resolved = []

    for ann in annotations:

        quote = ann.get("quote")

        if not quote:
            continue

        start = text.find(quote)

        if start == -1:
            continue  # discard hallucination safely

        end = start + len(quote)

        if not allow_overlaps:
            # Check for overlaps with already-resolved annotations
            has_overlap = False
            for existing in resolved:
                if not (end <= existing["start"] or start >= existing["end"]):
                    has_overlap = True
                    break

            if has_overlap:
                continue  # Skip overlapping annotations

        resolved.append({
            "start": start,
            "end": end,
            **ann
        })

    return resolved

def render_annotated_essay(text, annotations):
    """
    Clean, formatting-safe annotation renderer.
    No layout breakage. Dark-mode visible.
    """

    html_text = text

    annotations = sorted(
        annotations,
        key=lambda x: x["start"],
        reverse=True
    )

    for ann in annotations:

        start = ann["start"]
        end = ann["end"]

        snippet = html_text[start:end]

        if not snippet.strip():
            continue

        message = html.escape(str(ann.get("message", "")))
        suggestions_list = ann.get("suggestions", [])
        suggestions = html.escape(", ".join(str(s) for s in suggestions_list))

        tooltip = message
        if suggestions:
            tooltip += f" | Suggestions: {suggestions}"

        # Get criterion-specific colors
        color_scheme = get_criterion_color(ann["type"])
        bg = color_scheme["bg"]
        underline = color_scheme["underline"]
        
        safe_snippet = html.escape(snippet)
        

        span = (
            f'<span '
            f'style="'
            f'background-color:{bg};'
            f'color:white;'
            f'padding:1px 3px;'
            f'border-bottom:2px solid {underline};'
            f'border-radius:3px;'
            f'cursor:help;" '
            f'title="{tooltip}">'
            f'{safe_snippet}'
            f'</span>'
        )

        html_text = html_text[:start] + span + html_text[end:]

    return html_text.replace("\n", "<br>")

def pretty_print(result: dict):

    # FOR SEEING OUTPUT IN TERMINAL

    print("\n" + "=" * 80)
    print("📝 UPSC ESSAY EVALUATION REPORT")
    print("=" * 80)

    # =====================================================
    # METADATA
    # =====================================================

    meta = result.get("metadata", {})

    print("\n📊 ESSAY METADATA")
    print("-" * 80)

    print(f"Word Count        : {meta.get('word_count', 'N/A')}")
    print(f"Paragraphs        : {meta.get('paragraph_count', 'N/A')}")
    print(f"Avg Para Length   : {meta.get('avg_paragraph_words', 'N/A')}")

    # =====================================================
    # CRITERION RATINGS
    # =====================================================

    evaluations = result["evaluations"]

    print("\n📊 CRITERION ANALYSIS")
    print("-" * 80)

    for i, criterion in enumerate(CRITERIA, start=1):

        e = evaluations[criterion.key]

        print(f"{i}. {criterion.name:<30} → {e.rating}")
        print(f"   {e.feedback}\n")

    # =====================================================
    # GLOBAL STRENGTHS / WEAKNESSES
    # =====================================================

    strengths = result.get("strengths", [])
    weaknesses = result.get("weaknesses", [])

    print("\n✅ OVERALL STRENGTHS")
    print("-" * 80)

    if strengths:
        for s in strengths:
            print(f"• {s}")
    else:
        print("None detected.")

    print("\n⚠️ OVERALL WEAKNESSES")
    print("-" * 80)

    if weaknesses:
        for w in weaknesses:
            print(f"• {w}")
    else:
        print("None detected.")

    # =====================================================
    # FINAL ASSESSMENT
    # =====================================================

    print("\n🧠 FINAL EXAMINER REPORT")
    print("-" * 80)
    print(result.get("overall", "No overall feedback."))

    # =====================================================
    # ANNOTATION INTELLIGENCE
    # =====================================================

    annotations = result.get("annotations", [])
    essay = result.get("essay", "")

    print("\n🔎 ANNOTATION INTELLIGENCE")
    print("-" * 80)

    print(f"Total Annotations: {len(annotations)}")

    if essay:
        words = max(len(essay.split()), 1)
        density = len(annotations) / words * 1000
        print(f"Annotation Density: {density:.2f} per 1000 words")

    # ---------- Type Distribution ----------
    if annotations:

        types = Counter(a["type"] for a in annotations)

        print("\nAnnotation Types:")
        for t, count in types.items():
            print(f"• {t:<20} {count}")

    # =====================================================
    # HALLUCINATION CHECK
    # =====================================================

    unresolved = []

    for ann in annotations:
        if "quote" in ann and ann["quote"] not in essay:
            unresolved.append(ann["quote"])

    if annotations:
        resolution_rate = 1 - (len(unresolved) / len(annotations))

        print(f"\nQuote Resolution Rate: {resolution_rate:.2%}")

        if unresolved:
            print("\n⚠️ Possible hallucinated quotes:")
            for q in unresolved[:5]:
                print(f'• "{q}"')

    # =====================================================
    # SAMPLE ANNOTATIONS
    # =====================================================

    if annotations:

        print("\n🧩 SAMPLE ANNOTATIONS")
        print("-" * 80)

        for ann in annotations[:5]:

            print(f'\nQuote      : "{ann.get("quote", "")}"')
            print(f'Type       : {ann.get("type")}')
            print(f'Severity   : {ann.get("severity")}')
            print(f'Issue      : {ann.get("message")}')

            suggestions = ann.get("suggestions", [])
            if suggestions:
                print(f'Suggestion : {suggestions[0]}')

    print("\n" + "=" * 80)
    print("END OF REPORT")
    print("=" * 80 + "\n")
