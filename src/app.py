# import streamlit as st
# import uuid
# from datetime import datetime 

# st.markdown(
#     """
#     <style>
#     .stApp {
#         border: 8px solid #2E7D32;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )


# st.title("AI Smart Bug Analyzer & Fix Advisor")
# st.write("Hello! I am waiting for you bug report to be submitted .")



# bug_report = st.text_area("Bug Report / Stack Trace", height=200)

# uploaded_file=st.file_uploader("Or upload a bug report file", type=["txt", "log"])


# if st.button("Submit"):

#     final_text = ""

#     if uploaded_file is not None:
#         final_text = uploaded_file.read().decode("utf-8")
#     elif bug_report.strip() != "":
#         final_text = bug_report.strip()
    

#     if final_text =="": 
#         st.warning("Please enter a bug report or upload a file before submitting.")
#     else:
#         bug_record = {
#             "bug_id":"BUG-"+str(uuid.uuid4())[:8],
#             "description":final_text,
#             "stack_trace":final_text,
#             "timestamp":datetime.now().isoformat(),
#             "source":"user_submission"
#         }

#         st.success("Bug report received")
#         st.write("Here is what you submitted")
#         st.json(bug_record)



# import streamlit as st
# import uuid
# from datetime import datetime
# import pickle
# import chromadb

# st.markdown(
#     """
#     <style>
#     .stApp {
#         border: 8px solid #2E7D32;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# st.title("AI Smart Bug Analyzer & Fix Advisor")
# st.write("Hello! I am waiting for you bug report to be submitted .")

# # Load vectorizer and Chroma collection once, cached across reruns
# import os

# @st.cache_resource
# def load_retrieval_components():
#     base_dir = os.path.dirname(os.path.abspath(__file__))
#     vectorizer_path = os.path.join(base_dir, "vectorizer.pkl")

#     with open(vectorizer_path, "rb") as f:
#         vectorizer = pickle.load(f)

#     client = chromadb.PersistentClient(path="C:/temp/chroma_db")
#     collection = client.get_collection(name="bug_knowledge_base")

#     return vectorizer, collection

# vectorizer, collection = load_retrieval_components()

# bug_report = st.text_area("Bug Report / Stack Trace", height=200, key="bug_report_input")

# uploaded_file = st.file_uploader("Or upload a bug report file", type=["txt", "log"], key="bug_file_uploader")

# if st.button("Submit", key="submit_button"):
#     final_text = ""

#     if uploaded_file is not None:
#         final_text = uploaded_file.read().decode("utf-8")
#     elif bug_report.strip() != "":
#         final_text = bug_report.strip()

#     if final_text == "":
#         st.warning("Please enter a bug report or upload a file before submitting.")
#     else:
#         bug_record = {
#             "bug_id": "BUG-" + str(uuid.uuid4())[:8],
#             "description": final_text,
#             "stack_trace": final_text,
#             "timestamp": datetime.now().isoformat(),
#             "source": "user_submission"
#         }

#         st.success("Bug report received")
#         st.write("Here is what you submitted")
#         st.json(bug_record)

#         # --- Retrieval: find similar past bugs ---
#         query_vector = vectorizer.transform([final_text]).toarray().tolist()
#         results = collection.query(
#             query_embeddings=query_vector,
#             n_results=5
#         )

#         st.subheader("Similar Past Bugs")

#         for i in range(len(results['ids'][0])):
#             meta = results['metadatas'][0][i]
#             st.write(f"**{i+1}. {meta['title']}**")
#             st.write(f"Severity: {meta['severity']} | Source: {meta['source_dataset']}")
#             st.write("---")


# import streamlit as st
# import uuid
# from datetime import datetime
# import pickle
# import numpy as np
# import pandas as pd
# import os
# from sklearn.metrics.pairwise import cosine_similarity

# st.markdown(
#     """
#     <style>
#     .stApp {
#         border: 8px solid #2E7D32;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# st.title("AI Smart Bug Analyzer & Fix Advisor")
# st.write("Hello! I am waiting for you bug report to be submitted .")

# @st.cache_resource
# def load_retrieval_components():
#     base_dir = os.path.dirname(os.path.abspath(__file__))

#     with open(os.path.join(base_dir, "vectorizer.pkl"), "rb") as f:
#         vectorizer = pickle.load(f)

#     embeddings = np.load(os.path.join(base_dir, "embeddings.npy"))
#     metadata = pd.read_csv(os.path.join(base_dir, "chunks_metadata.csv"))

#     return vectorizer, embeddings, metadata

# vectorizer, kb_embeddings, kb_metadata = load_retrieval_components()

# bug_report = st.text_area("Bug Report / Stack Trace", height=200, key="bug_report_input")
# uploaded_file = st.file_uploader("Or upload a bug report file", type=["txt", "log"], key="bug_file_uploader")

# if st.button("Submit", key="submit_button"):
#     final_text = ""

#     if uploaded_file is not None:
#         final_text = uploaded_file.read().decode("utf-8")
#     elif bug_report.strip() != "":
#         final_text = bug_report.strip()

#     if final_text == "":
#         st.warning("Please enter a bug report or upload a file before submitting.")
#     else:
#         bug_record = {
#             "bug_id": "BUG-" + str(uuid.uuid4())[:8],
#             "description": final_text,
#             "stack_trace": final_text,
#             "timestamp": datetime.now().isoformat(),
#             "source": "user_submission"
#         }

#         st.success("Bug report received")
#         st.write("Here is what you submitted")
#         st.json(bug_record)

#         # --- Retrieval: cosine similarity against saved embeddings ---
#         query_vector = vectorizer.transform([final_text]).toarray()
#         similarities = cosine_similarity(query_vector, kb_embeddings)[0]

#         top_indices = np.argsort(similarities)[::-1][:5]

#         st.subheader("Similar Past Bugs")

#         for rank, idx in enumerate(top_indices):
#             row = kb_metadata.iloc[idx]
#             st.write(f"**{rank+1}. {row['title']}**")
#             st.write(f"Severity: {row['severity']} | Source: {row['source_dataset']} | Similarity: {similarities[idx]:.2f}")
#             st.write("---")
# import os
# import json
# import time
# from groq import Groq
# from dotenv import load_dotenv

# # Load API key and create client
# _base_dir = os.path.dirname(os.path.abspath(__file__))
# _env_path = os.path.join(_base_dir, "..", ".env")
# load_dotenv(_env_path)
# api_key = os.getenv("GROQ_API_KEY")
# client = Groq(api_key=api_key)


# def call_llm_with_retry(system_prompt, user_message, max_retries=3):
#     for attempt in range(max_retries):
#         try:
#             response = client.chat.completions.create(
#                 model="llama-3.3-70b-versatile",
#                 messages=[
#                     {"role": "system", "content": system_prompt},
#                     {"role": "user", "content": user_message}
#                 ],
#                 temperature=0.2
#             )
#             return json.loads(response.choices[0].message.content)
#         except Exception as e:
#             if "rate_limit" in str(e).lower() or "429" in str(e):
#                 wait_time = (attempt + 1) * 3
#                 time.sleep(wait_time)
#             else:
#                 print(f"Non-rate-limit error: {e}")
#                 break
#     return None


# system_prompt = """You are a bug triage assistant. You are given the title, description, and stack trace of a submitted bug, and you classify it by severity, priority, and affected component, with confidence scoring and reasoning.

# IMPORTANT CALIBRATION: Most everyday bugs are Medium severity, not Critical or High. Reserve Critical/High for bugs that cause crashes, data loss, security issues, or completely block core functionality. Reserve Low for cosmetic issues, minor inconveniences, or feature requests. The MAJORITY of real-world bugs are routine Medium severity - do not over-classify ordinary bugs as urgent just because they mention words like "error" or "exception."

# Examples for calibration:
# - "App crashes on startup, no workaround" -> Critical
# - "Login fails for all users" -> Critical  
# - "Button text is misaligned by 2px" -> Low
# - "Feature request: add dark mode" -> Low
# - "Export function occasionally produces incorrect date format" -> Medium
# - "Search results are slow to load under heavy traffic" -> Medium

# Reply ONLY in valid JSON, with this exact structure:
# {"bug_id": "...", "severity": "Critical", "confidence": 0.85, "reasoning": "...", "priority": "...", "component": "Login"}

# Field definitions:
# - bug_id: if provided, use it; otherwise use "unknown"
# - severity: must be exactly one of Critical, High, Medium, Low - no other words
# - confidence: a score from 0 to 1 representing how confident you are in this classification
# - reasoning: a brief explanation of why you classified it this way
# - priority: how urgently this needs to be addressed - Immediate, High, Medium, or Low (related to but different from severity: severity is impact, priority is urgency)
# - component: which part/module of the software seems affected, inferred from the content (e.g. "Login", "Database", "UI/Rendering") - do not restrict to a fixed list

# If you encounter other severity-like words, map them using this table:
# blocker/critical -> Critical, major -> High, normal/unknown -> Medium, minor/trivial -> Low
# """

# log_analysis_system_prompt = """You are a Log Analysis Agent. Your job is to extract structured information from messy error text - stack traces, tracebacks, or compiler error messages, sometimes alongside the relevant code.

# Extract:
# - error_type: the SPECIFIC error/exception name as it would appear in real compiler/runtime output - NOT a generic category. For example, prefer "Template Mismatch" or "Dereferencing Void Pointer" over generic terms like "Compilation Error" or "Compilation Warning". Look for the specific technical term the error message itself uses, not a broad summary category.
# - failure_location: the exact file/line/position where the error occurred, taken directly from the trace
# - code_path: the chain of function/method calls leading to the failure. IMPORTANT: if the code being described contains double quote characters (e.g. from println!, print statements, or string literals), you MUST escape them as \\" so the JSON stays valid. Never include an unescaped " inside any field value.
# - confidence: a score from 0 to 1 representing how certain you are that you extracted this correctly. Vary this realistically - very clear, unambiguous traces should score 0.95-0.99, while vague, truncated, or ambiguous input should score lower (0.5-0.8). Do not default to 0.99 for everything.
# - reasoning: a brief, specific explanation of why the error occurred

# Reply ONLY in valid JSON with this exact structure. Every field value must be a properly escaped JSON string - double quotes inside any value must be written as \\":
# {"error_type": "...", "failure_location": "...", "code_path": "...", "confidence": 0.9, "reasoning": "..."}

# Examples:

# Input: Cell In[119], line 3
#     return payload_2
#     ^
# IndentationError: unindent does not match any outer indentation level

# Output: {"error_type": "IndentationError", "failure_location": "Cell In[119], line 3", "code_path": "return payload_2 executed directly within the current code block; indentation parsing failed before execution", "confidence": 0.99, "reasoning": "The 'return' statement has inconsistent indentation that does not align with the surrounding block, causing Python's parser to reject the code."}

# Input: /workspace/service_2.js:3
# console.log(session_2[5].id);
# TypeError: Cannot read properties of undefined (reading 'id')
#     at Object.<anonymous> (/workspace/service_2.js:3:15)

# Output: {"error_type": "TypeError", "failure_location": "/workspace/service_2.js:3:15", "code_path": "Top-level execution -> console.log(session_2[5].id)", "confidence": 0.99, "reasoning": "The expression 'session_2[5]' evaluated to undefined, so accessing its 'id' property caused a TypeError."}

# Input: parser_4.c: In function 'main':
# parser_4.c:3:15: error: invalid initializer / incompatible types when initializing type 'int' using type 'char *'
#     3 |     int val = str;

# Output: {"error_type": "Invalid Initializer (Incompatible Types)", "failure_location": "parser_4.c:3:15", "code_path": "main() -> variable initialization: int val = str", "confidence": 0.85, "reasoning": "An integer variable was initialized using a character pointer, which is an incompatible type conversion in C."}

# Input: session_2.cpp: In function 'int main()':
# session_2.cpp:5:17: error: no matching member function for call to 'insert'
#     5 |     ages.insert(10, "John");

# Output: {"error_type": "No Matching Member Function", "failure_location": "session_2.cpp:5:17", "code_path": "main() -> std::map::insert(10, \\"John\\")", "confidence": 0.95, "reasoning": "The std::map::insert() function was called with arguments that do not match any valid overload."}

# Input: Exception in thread "main" java.lang.NullPointerException: Cannot invoke "String.indexOf(String)" because "recordsList_2" is null
#     at MetricsEngine_2.updateCache_2(Api_2.java:110)

# Output: {"error_type": "NullPointerException", "failure_location": "Api_2.java:110", "code_path": "main thread -> MetricsEngine_2.updateCache_2() -> String.indexOf()", "confidence": 0.99, "reasoning": "The object 'recordsList_2' is null, so calling the 'indexOf()' method on it causes a NullPointerException."}

# Input: CssSyntaxError: grid_2.css:20:1: Unclosed block
#   18 |     background: #000;
#   19 |     opacity: 0.9;
# > 20 |
#     | ^
#   21 | .element-sibling_2 {

# Output: {"error_type": "PostCSS Parser Error: Unclosed Block", "failure_location": "grid_2.css:20:1", "code_path": "CSS parser -> grid_2.css -> unclosed declaration block before '.element-sibling_2'", "confidence": 0.99, "reasoning": "A CSS block was not properly closed with '}', causing the parser to detect an unclosed block before the next selector."}

# Input: Error: Stray end tag </span>.
# From line 95, column 15; to line 95, column 22
# item 1</p></span>\n</di

# Output: {"error_type": "W3C Validator Error: Stray End Tag", "failure_location": "Line 95, columns 15-22", "code_path": "HTML parser -> closing tags -> unexpected </span>", "confidence": 0.99, "reasoning": "The closing </span> tag does not match any currently open <span> element, resulting in a stray end tag."}

# Input: app_1.ts:63:1 - error TS2322: Type 'string' is not assignable to type 'number'.
# 63 weightsTensor_1 = "invalid_assign_1";
#   ~~~~~~~~~~~~~~~

# Output: {"error_type": "TypeScript Error: TS2322 (Type Assignment Error)", "failure_location": "app_1.ts:63:1", "code_path": "Top-level assignment -> weightsTensor_1 = \\"invalid_assign_1\\"", "confidence": 0.99, "reasoning": "A string value was assigned to a variable that is declared with the type 'number', violating TypeScript's type checking rules."}

# Input: panic: runtime error: index out of range [7] with length 3
# goroutine 1 [running]:
# main.main()
#     /go/src/app/main_2.go:96 +0x3d

# Output: {"error_type": "Go Runtime Panic: Index Out of Range", "failure_location": "/go/src/app/main_2.go:96", "code_path": "main.main() -> slice/array index access", "confidence": 0.99, "reasoning": "The program attempted to access index 7 of a slice or array that contains only 3 elements, causing a runtime panic."}
# """


# def triage_agent(title, description, stack_trace="Not available", bug_id="unknown"):
#     user_message = f"Title: {title}\nDescription: {description}\nStack Trace: {stack_trace}"
#     result = call_llm_with_retry(system_prompt, user_message)
#     if result is None:
#         result = {"severity": "Medium", "confidence": 0.0, "reasoning": "LLM call failed after retries", "priority": "Medium", "component": "Unknown"}
#     result['bug_id'] = bug_id
#     return result


# def log_analysis_agent(error_text, code_context=""):
#     if code_context:
#         user_message = f"Code:\n{code_context}\n\nError:\n{error_text}"
#     else:
#         user_message = f"Error:\n{error_text}"
#     result = call_llm_with_retry(log_analysis_system_prompt, user_message)
#     if result is None:
#         result = {
#             "error_type": "Unknown",
#             "failure_location": "Not determined",
#             "code_path": "Not determined",
#             "confidence": 0.0,
#             "reasoning": "LLM call failed after retries"
#         }
#     return result


# def run_orchestration(title, description, stack_trace, bug_id="unknown"):
#     triage_result = triage_agent(title, description, stack_trace, bug_id=bug_id)
#     log_result = log_analysis_agent(stack_trace)

#     combined_result = {
#         "bug_id": bug_id,
#         "triage": triage_result,
#         "log_analysis": log_result
#     }

#     return combined_result


# def build_simple_view(combined_result):
#     triage = combined_result["triage"]
#     log = combined_result["log_analysis"]

#     actual_result = {
#         "bug_id": combined_result["bug_id"],
#         "severity": triage["severity"],
#         "priority": triage["priority"],
#         "component": triage["component"],
#         "error_type": log["error_type"],
#         "failure_location": log["failure_location"],
#         "code_path": log["code_path"],
#         "confidence": log["confidence"],
#         "reasoning": log["reasoning"]
#     }

#     return actual_result



import streamlit as st
import uuid
from datetime import datetime
import numpy as np
import pandas as pd
import os
import sys
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Make sure agents.py (in the same folder) can be imported regardless of
# where Streamlit was launched from
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agents import run_orchestration, build_simple_view

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

# --- Figure out what text (if any) is currently submitted ---
final_text = ""
if uploaded_file is not None:
    final_text = uploaded_file.read().decode("utf-8")
elif bug_report.strip() != "":
    final_text = bug_report.strip()

# --- Auto-submit: keep track of the last text we already analyzed ---
if "last_analyzed_text" not in st.session_state:
    st.session_state.last_analyzed_text = ""
if "combined_result" not in st.session_state:
    st.session_state.combined_result = None
if "bug_record" not in st.session_state:
    st.session_state.bug_record = None

should_analyze = (final_text != "" and final_text != st.session_state.last_analyzed_text)

if final_text == "":
    st.info("Waiting for a bug report to be pasted or uploaded...")

elif should_analyze:
    st.session_state.last_analyzed_text = final_text

    bug_record = {
        "bug_id": "BUG-" + str(uuid.uuid4())[:8],
        "description": final_text,
        "stack_trace": final_text,
        "timestamp": datetime.now().isoformat(),
        "source": "user_submission"
    }
    st.session_state.bug_record = bug_record

    with st.spinner("Analyzing bug report..."):
        # --- Run both agents (Task 3: orchestration) ---
        combined_result = run_orchestration(
            title=final_text[:80],
            description=final_text,
            stack_trace=final_text,
            bug_id=bug_record["bug_id"]
        )
        st.session_state.combined_result = combined_result

# --- Display results (uses whatever was last analyzed, from session_state) ---
if st.session_state.combined_result is not None:
    bug_record = st.session_state.bug_record
    combined_result = st.session_state.combined_result
    simple_view = build_simple_view(combined_result)

    st.success("Bug report received and analyzed")

    st.subheader("Analysis Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Severity", simple_view["severity"])
    col2.metric("Priority", simple_view["priority"])
    col3.metric("Component", simple_view["component"])

    st.write(f"**Error Type:** {simple_view['error_type']}")
    st.write(f"**Failure Location:** {simple_view['failure_location']}")
    st.write(f"**Code Path:** {simple_view['code_path']}")
    st.write(f"**Confidence:** {simple_view['confidence']:.2f}")
    st.write(f"**Reasoning:** {simple_view['reasoning']}")

    # --- "Show full details" button - reveals both agents' complete raw output ---
    if st.button("Show full details (both agents)", key="show_full_details"):
        st.subheader("Full Combined Result")
        st.json(combined_result)

    st.divider()
    st.subheader("Submitted Bug Record")
    st.json(bug_record)

    # --- Retrieval: cosine similarity using real semantic embeddings ---
    query_vector = model.encode([bug_record["description"]], convert_to_numpy=True)
    similarities = cosine_similarity(query_vector, kb_embeddings)[0]

    top_indices = np.argsort(similarities)[::-1][:5]

    st.subheader("Similar Past Bugs")

    for rank, idx in enumerate(top_indices):
        row = kb_metadata.iloc[idx]
        st.write(f"**{rank+1}. {row['title']}**")
        st.write(f"Severity: {row['severity']} | Source: {row['source_dataset']} | Similarity: {similarities[idx]:.2f}")
        st.write("---")