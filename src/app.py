import streamlit as st
import uuid
from datetime import datetime 

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
st.write("Hello! I am waiting for you bug report to be submitted .")



bug_report = st.text_area("Bug Report / Stack Trace", height=200)

uploaded_file=st.file_uploader("Or upload a bug report file", type=["txt", "log"])


if st.button("Submit"):

    final_text = ""

    if uploaded_file is not None:
        final_text = uploaded_file.read().decode("utf-8")
    elif bug_report.strip() != "":
        final_text = bug_report.strip()
    

    if final_text =="": 
        st.warning("Please enter a bug report or upload a file before submitting.")
    else:
        bug_record = {
            "bug_id":"BUG-"+str(uuid.uuid4())[:8],
            "description":final_text,
            "stack_trace":final_text,
            "timestamp":datetime.now().isoformat(),
            "source":"user_submission"
        }

        st.success("Bug report received")
        st.write("Here is what you submitted")
        st.json(bug_record)