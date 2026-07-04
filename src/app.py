import streamlit as st

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
st.write("Hello! If you can see this, Streamlit is working.")



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
        st.success("Bug report received")
        st.write("Here is what you submitted")
        st.code(final_text)