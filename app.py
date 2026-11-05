"""Streamlit UI for the Hybrid Grammar Correction System.  Run:  streamlit run app.py"""
import streamlit as st

from grammar.pipeline import HybridGrammarCorrector

st.set_page_config(page_title="Hybrid Grammar Correction", page_icon="📝", layout="centered")
st.title("📝 Hybrid Grammar Correction")
st.caption("Formal Language Theory (DFA · FSA · CFG) + T5 Transformer")


@st.cache_resource
def get_model():
    return HybridGrammarCorrector()


text = st.text_area("Enter a sentence", "he go to school yesterday")
if st.button("Check grammar", type="primary") and text.strip():
    with st.spinner("Analysing..."):
        result = get_model().check(text)

    st.subheader("Step-by-step analysis")
    labels = {"DFA": "Format (DFA)", "FSA": "Morphology (FSA)", "CFG": "Syntax (CFG)"}
    for layer, errs in result["errors"].items():
        with st.expander(f"{'❌' if errs else '✅'} {labels[layer]} — {len(errs)} issue(s)",
                         expanded=bool(errs)):
            if not errs:
                st.write("No issues found.")
            for e in errs:
                line = f"**{e['error']}**"
                if e.get("suggestion"):
                    line += f" → suggestion: `{e['suggestion']}`"
                st.markdown(line)
                if e.get("detail"):
                    st.caption(f"POS sequence: {e['detail']}")

    st.subheader("Transformer correction")
    st.success(result["corrected"])
