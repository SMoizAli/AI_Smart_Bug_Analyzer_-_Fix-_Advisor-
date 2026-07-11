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

import streamlit as st
import uuid
from datetime import datetime
import numpy as np
import pandas as pd
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

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

if st.button("Submit", key="submit_button"):
    final_text = ""

    if uploaded_file is not None:
        final_text = uploaded_file.read().decode("utf-8")
    elif bug_report.strip() != "":
        final_text = bug_report.strip()

    if final_text == "":
        st.warning("Please enter a bug report or upload a file before submitting.")
    else:
        bug_record = {
            "bug_id": "BUG-" + str(uuid.uuid4())[:8],
            "description": final_text,
            "stack_trace": final_text,
            "timestamp": datetime.now().isoformat(),
            "source": "user_submission"
        }

        st.success("Bug report received")
        st.write("Here is what you submitted")
        st.json(bug_record)

        # --- Retrieval: cosine similarity using real semantic embeddings ---
        query_vector = model.encode([final_text], convert_to_numpy=True)
        similarities = cosine_similarity(query_vector, kb_embeddings)[0]

        top_indices = np.argsort(similarities)[::-1][:5]

        st.subheader("Similar Past Bugs")

        for rank, idx in enumerate(top_indices):
            row = kb_metadata.iloc[idx]
            st.write(f"**{rank+1}. {row['title']}**")
            st.write(f"Severity: {row['severity']} | Source: {row['source_dataset']} | Similarity: {similarities[idx]:.2f}")
            st.write("---")