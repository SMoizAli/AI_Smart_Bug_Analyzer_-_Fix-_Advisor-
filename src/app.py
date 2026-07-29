import streamlit as st
import uuid
from datetime import datetime
import numpy as np
import pandas as pd
import os
import sys
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agents import (
    run_orchestration, build_simple_view, init_db, save_submission,
    retrieve_similar_bugs, root_cause_agent,
    duplicate_detection_agent, remediation_agent
)

init_db()

st.markdown(
    """
    <style>
    .stApp {
        border: 8px solid #2E7D32;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("AI Smart Bug Analyzer & Fix Advisor")
st.write("Paste your bug report or stack trace below - analysis runs automatically.")


@st.cache_resource
def load_retrieval_components():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = np.load(os.path.join(base_dir, "embeddings_real.npy"))
    metadata = pd.read_csv(os.path.join(base_dir, "chunks_metadata.csv"))
    return model, embeddings, metadata


model, kb_embeddings, kb_metadata = load_retrieval_components()

bug_report = st.text_area("Bug Report / Stack Trace", height=200, key="bug_report_input")
uploaded_file = st.file_uploader("Or upload a bug report file", type=["txt", "log"], key="bug_file_uploader")

top_n = st.slider(
    "Number of similar bugs to retrieve (used for Root Cause and Duplicate Detection)",
    min_value=3, max_value=15, value=5, key="top_n_slider"
)

final_text = ""
if uploaded_file is not None:
    final_text = uploaded_file.read().decode("utf-8")
elif bug_report.strip() != "":
    final_text = bug_report.strip()

if "last_analyzed_text" not in st.session_state:
    st.session_state.last_analyzed_text = ""
if "last_top_n" not in st.session_state:
    st.session_state.last_top_n = top_n
if "combined_result" not in st.session_state:
    st.session_state.combined_result = None
if "bug_record" not in st.session_state:
    st.session_state.bug_record = None
if "retrieved_bugs" not in st.session_state:
    st.session_state.retrieved_bugs = []
if "root_cause_result" not in st.session_state:
    st.session_state.root_cause_result = None
if "duplicate_result" not in st.session_state:
    st.session_state.duplicate_result = []
if "remediation_result" not in st.session_state:
    st.session_state.remediation_result = None

should_analyze = (
    final_text != "" and
    (final_text != st.session_state.last_analyzed_text or top_n != st.session_state.last_top_n)
)

if final_text == "":
    st.info("Waiting for a bug report to be pasted or uploaded...")

elif should_analyze:
    st.session_state.last_analyzed_text = final_text
    st.session_state.last_top_n = top_n

    bug_record = {
        "bug_id": "BUG-" + str(uuid.uuid4())[:8],
        "description": final_text,
        "stack_trace": final_text,
        "timestamp": datetime.now().isoformat(),
        "source": "user_submission"
    }
    st.session_state.bug_record = bug_record

    # --- Step 1: Triage + Log Analysis (save_submission deliberately NOT called yet) ---
    with st.spinner("Running Triage and Log Analysis..."):
        combined_result = run_orchestration(
            title=final_text[:80],
            description=final_text,
            stack_trace=final_text,
            bug_id=bug_record["bug_id"]
        )
        st.session_state.combined_result = combined_result

    triage_result = combined_result["triage"]
    log_result = combined_result["log_analysis"]

    # --- Step 2: Retrieve similar historical bugs (Milestone 1 KB) ---
    with st.spinner("Retrieving similar historical bugs..."):
        try:
            retrieved_bugs = retrieve_similar_bugs(
                final_text, model, kb_embeddings, kb_metadata, top_n=top_n
            )
        except Exception as e:
            retrieved_bugs = []
            st.session_state.retrieval_error = str(e)
        st.session_state.retrieved_bugs = retrieved_bugs

    # --- Step 3: Root Cause Agent ---
    with st.spinner("Analyzing root cause..."):
        try:
            root_cause_result = root_cause_agent(
                bug_id=bug_record["bug_id"],
                severity=triage_result["severity"],
                component=triage_result["component"],
                error_type=log_result["error_type"],
                failure_location=log_result["failure_location"],
                code_path=log_result["code_path"],
                retrieved_bugs=retrieved_bugs
            )
        except Exception as e:
            root_cause_result = {
                "root_cause_hypothesis": "Root cause analysis could not be completed due to a system error.",
                "confidence": 0.0,
                "supporting_evidence": [],
                "error": str(e)
            }
        st.session_state.root_cause_result = root_cause_result

    # --- Step 4: Duplicate Detection Agent (SQLite still does NOT contain this bug yet) ---
    with st.spinner("Checking for duplicate submissions..."):
        try:
            duplicate_result = duplicate_detection_agent(
                new_description=final_text,
                error_type=log_result["error_type"],
                component=triage_result["component"],
                reasoning=log_result["reasoning"],
                model=model,
                top_n=top_n
            )
        except Exception as e:
            duplicate_result = []
            st.session_state.duplicate_error = str(e)
        st.session_state.duplicate_result = duplicate_result

    # --- Step 5: Remediation Agent ---
    with st.spinner("Generating fix recommendation..."):
        try:
            remediation_result = remediation_agent(
                bug_id=bug_record["bug_id"],
                severity=triage_result["severity"],
                component=triage_result["component"],
                error_type=log_result["error_type"],
                failure_location=log_result["failure_location"],
                code_path=log_result["code_path"],
                description=final_text,
                root_cause=root_cause_result["root_cause_hypothesis"],
                historical_references=root_cause_result["supporting_evidence"],
                duplicate_bug=duplicate_result if duplicate_result else None
            )
        except Exception as e:
            remediation_result = {
                "recommended_fix": "A fix recommendation could not be generated due to a system error.",
                "fix_steps": [], "code_example": {}, "validation_steps": [],
                "prevention": "", "confidence": 0.0,
                "reasoning": "Remediation agent failed.", "references_used": [],
                "error": str(e)
            }
        st.session_state.remediation_result = remediation_result

    # --- Step 6: NOW save to SQLite — after duplicate detection, so this bug can't match itself ---
    with st.spinner("Saving submission..."):
        simple_view_for_db = build_simple_view(combined_result)
        save_submission(simple_view_for_db, bug_record["description"], bug_record["timestamp"])

# --- Display results (uses whatever was last analyzed, from session_state) ---
if st.session_state.combined_result is not None:
    bug_record = st.session_state.bug_record
    combined_result = st.session_state.combined_result
    simple_view = build_simple_view(combined_result)
    retrieved_bugs = st.session_state.retrieved_bugs
    root_cause_result = st.session_state.root_cause_result
    duplicate_result = st.session_state.duplicate_result
    remediation_result = st.session_state.remediation_result

    st.success("Bug report received and analyzed")

    st.subheader("Analysis Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Severity", simple_view["severity"])
    col2.metric("Priority", simple_view["priority"])
    col3.metric("Component", simple_view["component"])

    st.write(f"**Error Type:** {simple_view['error_type']}")
    st.write(f"**Failure Location:** {simple_view['failure_location']}")

    if root_cause_result:
        hyp = root_cause_result['root_cause_hypothesis']
        st.write(f"**Root Cause (summary):** {hyp[:150]}{'...' if len(hyp) > 150 else ''}")

    if duplicate_result:
        st.write(f"**Duplicates Found:** {len(duplicate_result)} similar past submission(s)")
    else:
        st.write("**Duplicates Found:** None — this appears to be a new issue")

    if remediation_result:
        fix = remediation_result['recommended_fix']
        st.write(f"**Recommended Fix (summary):** {fix[:150]}{'...' if len(fix) > 150 else ''}")

    if st.button("Show full details (all agents)", key="show_full_details"):
        st.subheader("Full Combined Result (Triage + Log Analysis)")
        st.json(combined_result)
        st.subheader("Full Root Cause Result")
        st.json(root_cause_result)
        st.subheader("Full Duplicate Detection Result")
        st.json(duplicate_result)
        st.subheader("Full Remediation Result")
        st.json(remediation_result)

    st.divider()

    st.subheader("Root Cause Analysis")
    if root_cause_result:
        confidence = root_cause_result.get("confidence", 0.0)
        st.write(f"**Hypothesis:** {root_cause_result['root_cause_hypothesis']}")
        st.write(f"**Confidence:** {confidence:.2f}")
        if confidence < 0.6:
            st.warning("Limited historical evidence available — this is a best-guess hypothesis, not a confirmed cause.")
        if root_cause_result.get("supporting_evidence"):
            st.write("**Supporting Evidence:**")
            for ev in root_cause_result["supporting_evidence"]:
                st.write(f"- `{ev['bug_id']}` — {ev['summary']}")
        else:
            st.write("No supporting historical evidence was found for this hypothesis.")

    st.divider()

    st.subheader("Duplicate Bugs")
    if duplicate_result:
        for d in duplicate_result:
            st.write(f"**`{d['bug_id']}`** — {d['label'].upper()} match ({d['similarity']*100:.1f}% similar)")
            st.write(d["explanation"])
            st.write("---")
    else:
        st.info("No similar past submissions found — this appears to be a new issue.")

    st.divider()

    st.subheader("Recommended Fix")
    if remediation_result:
        st.write(f"**{remediation_result['recommended_fix']}**")
        st.write(f"**Confidence:** {remediation_result.get('confidence', 0.0):.2f}")

        if remediation_result.get("fix_steps"):
            st.write("**Fix Steps:**")
            for i, step in enumerate(remediation_result["fix_steps"], 1):
                st.write(f"{i}. {step}")

        if remediation_result.get("code_example"):
            ce = remediation_result["code_example"]
            if ce.get("before") or ce.get("after"):
                col_before, col_after = st.columns(2)
                with col_before:
                    st.write("**Before:**")
                    st.code(ce.get("before", ""))
                with col_after:
                    st.write("**After:**")
                    st.code(ce.get("after", ""))

        if remediation_result.get("validation_steps"):
            st.write("**Validation Steps:**")
            for step in remediation_result["validation_steps"]:
                st.write(f"- {step}")

        if remediation_result.get("prevention"):
            st.write(f"**Prevention Tip:** {remediation_result['prevention']}")

        if remediation_result.get("reasoning"):
            st.write(f"**Reasoning:** {remediation_result['reasoning']}")

        if remediation_result.get("references_used"):
            st.write("**References Used:**")
            for ref in remediation_result["references_used"]:
                match_info = f" ({ref['match']}, {ref['similarity']*100:.0f}%)" if "match" in ref else ""
                st.write(f"- `{ref['bug_id']}`{match_info} — {ref.get('summary', '')}")

    st.divider()

    st.subheader("Submitted Bug Record")
    st.json(bug_record)

    st.subheader(f"Similar Past Bugs (Historical Knowledge Base, Top {top_n})")
    if retrieved_bugs:
        for rank, r in enumerate(retrieved_bugs, 1):
            st.write(f"**{rank}. {r['title']}**")
            st.write(f"Severity: {r['severity']} | Source: {r['source_dataset']} | Similarity: {r['similarity']:.2f}")
            st.write("---")
    else:
        st.info("No similar historical bugs were retrieved.")