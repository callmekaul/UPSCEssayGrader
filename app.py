import streamlit as st
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

from build_graph import workflow
from schemas import EssayState
from utils import resolve_annotations, render_annotated_essay, get_criterion_color, CRITERION_COLORS


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="UPSC Essay Evaluator",
    page_icon="📝",
    layout="wide"
)

st.title("📝 UPSC Essay Evaluator")


# =====================================================
# SESSION STATE
# =====================================================

if "result" not in st.session_state:
    st.session_state.result = None

if "essay" not in st.session_state:
    st.session_state.essay = ""

if "topic" not in st.session_state:
    st.session_state.topic = ""

if "selected_criterion" not in st.session_state:
    st.session_state.selected_criterion = None


# =====================================================
# INPUT VIEW
# =====================================================

if st.session_state.result is None:

    topic = st.text_input("Essay Topic")

    essay = st.text_area(
        "Paste your essay",
        height=400
    )

    if st.button("Evaluate Essay"):

        if not topic or not essay:
            st.warning("Please provide both topic and essay.")
            st.stop()

        with st.spinner("Evaluating essay..."):

            initial_state: EssayState = {
                "topic": topic,
                "essay": essay,
                "overall": "",
            }

            result = workflow.invoke(initial_state)

        st.session_state.result = result
        st.session_state.topic = topic
        st.session_state.essay = essay

        st.rerun()


# =====================================================
# OUTPUT VIEW
# =====================================================

else:

    result = st.session_state.result

    # -------------------------------------------------
    # FINAL REPORT
    # -------------------------------------------------
    st.subheader("🧠 Final Examiner Report")
    
    st.info(result["overall"])

    st.divider()

    # =====================================================
    # TWO COLUMN LAYOUT
    # =====================================================

    essay_col, feedback_col = st.columns([1.5, 1])

    # -------------------------------------------------
    # LEFT — ESSAY WITH ANNOTATIONS
    # -------------------------------------------------

    with essay_col:

        st.subheader("Your Essay")

        essay_text = st.session_state.essay

        # Collect annotations from all evaluations
        raw_annotations = []
        for criterion_key, evaluation in result["evaluations"].items():
            if hasattr(evaluation, "annotations") and evaluation.annotations:
                for ann in evaluation.annotations:
                    raw_annotations.append({
                        "quote": ann.quote,
                        "type": criterion_key,
                        "severity": ann.severity,
                        "message": ann.issue,
                        "suggestions": [ann.suggestion]
                    })

        # Resolve two ways:
        # - non-overlapping (default, safe for combined view)
        # - allow_overlaps (for per-criterion deep view)
        
        resolved_nonoverlap = resolve_annotations(
            essay_text,
            raw_annotations,
            allow_overlaps=False
        )

        resolved_all = resolve_annotations(
            essay_text,
            raw_annotations,
            allow_overlaps=True
        )

        # If a criterion is selected, render only that criterion's annotations
        selected = st.session_state.get("selected_criterion")
        if selected:
            filtered_raw = [a for a in raw_annotations if a["type"] == selected]
            resolved_selected = resolve_annotations(
                essay_text,
                filtered_raw,
                allow_overlaps=True
            )

            st.caption(f"Viewing annotations for: {selected} — {len(resolved_selected)} / {len(filtered_raw)} resolved")

            annotated_html = render_annotated_essay(
                essay_text,
                resolved_selected
            )
        else:
            # Default combined view uses non-overlapping resolved annotations
            st.caption(
                f"Resolved {len(resolved_nonoverlap)} / {len(raw_annotations)} annotations (combined view)"
            )

            annotated_html = render_annotated_essay(
                essay_text,
                resolved_nonoverlap
            )

        st.markdown(
            f"""
            <div style='line-height:1.85;
                        font-size:17px;
                        padding-right:25px'>
                {annotated_html}
            </div>
            """,
            unsafe_allow_html=True
        )

    # -------------------------------------------------
    # RIGHT — FEEDBACK PANEL
    # -------------------------------------------------

    with feedback_col:

        st.subheader("Criterion Analysis")

        # Quick control: reset to combined view
        if st.button("Show all annotations", key="view_all"):
            st.session_state.selected_criterion = None
            st.rerun()

        for key, evaluation in result["evaluations"].items():

            name = key.replace("_", " ").title()

            rating = getattr(evaluation, "rating", None) or (evaluation.get("rating") if isinstance(evaluation, dict) else None)
            feedback = getattr(evaluation, "feedback", None) or (evaluation.get("feedback") if isinstance(evaluation, dict) else "")

            # Get criterion color
            color_scheme = get_criterion_color(key)
            color_hex = color_scheme["bg"]
            
            # Display criterion name with colored background
            st.markdown(
                f"""
                <div style='background-color:{color_hex};color:white;padding:8px 12px;border-radius:4px;margin-bottom:8px;'>
                    <strong style='font-size:16px;'>{name} — {rating}</strong>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.caption(feedback)

            # Button to view annotations for this criterion (per-criterion view)
            if st.button("View annotations", key=f"view_{key}"):
                st.session_state.selected_criterion = key
                st.rerun()

            st.divider()

        st.markdown("### ✅ Overall Strengths")

        for s in result["strengths"]:
            st.write(f"- {s}")

        st.markdown("### ⚠️ Overall Weaknesses")

        for w in result["weaknesses"]:
            st.write(f"- {w}")

    st.divider()

    if st.button("Evaluate Another Essay"):

        st.session_state.result = None
        st.session_state.topic = ""
        st.session_state.essay = ""

        st.rerun()
