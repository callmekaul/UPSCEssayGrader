import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from build_graph import workflow
from schemas import EssayState


# ---------- Page Config ----------
st.set_page_config(
    page_title="UPSC Essay Evaluator",
    page_icon="📝",
    layout="wide"
)

st.title("📝 UPSC Essay Evaluator")


# ---------- Inputs ----------
topic = st.text_input("Essay Topic")

essay = st.text_area(
    "Paste your essay",
    height=400
)


# ---------- Evaluate Button ----------
if st.button("Evaluate Essay"):

    if not topic or not essay:
        st.warning("Please provide both topic and essay.")
        st.stop()

    with st.spinner("Evaluating essay..."):

        initial_state: EssayState = {
            "topic": topic,
            "essay": essay
        }

        result = workflow.invoke(initial_state)


    # ---------- Display Results ----------
    st.success(f"Total Score: {result['total_score']} / 50")

    st.divider()

    for key, evaluation in result["evaluations"].items():

        with st.expander(f"{key.replace('_',' ').title()} — {evaluation.score}/10"):

            st.markdown("**Strengths**")
            for s in evaluation.strengths:
                st.write(f"✅ {s}")

            st.markdown("**Weaknesses**")
            for w in evaluation.weaknesses:
                st.write(f"⚠️ {w}")

            st.markdown("**Examiner Feedback**")
            st.write(evaluation.feedback)

    st.divider()

    st.subheader("Overall Assessment")
    st.write(result["overall"])