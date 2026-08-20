import streamlit as st
import sqlite3
from pathlib import Path
from datetime import datetime
import pandas as pd

# -------------------------------------------------------------
# 1. SET YOUR DATABASE SAVE LOCATION HERE
# -------------------------------------------------------------
DEV_DB_DIR = Path(__file__).resolve().parent / "data"
DEV_DB_DIR.mkdir(parents=True, exist_ok=True)  # Automatically creates folder if missing
DEV_DB_PATH = DEV_DB_DIR / "Developer_Submission.db"

# -------------------------------------------------------------
# 2. DATABASE INITIALIZATION FUNCTION
# -------------------------------------------------------------
def init_developer_db():
    conn = sqlite3.connect(DEV_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Developer_Submission (
            submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
            bug_id TEXT,
            project_name TEXT,
            reporter_name TEXT,
            developer_department TEXT,
            group_number TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

init_developer_db()

# -------------------------------------------------------------
# 3. STREAMLIT PAGE CONFIG & THEME CSS
# -------------------------------------------------------------
st.set_page_config(page_title="Metadata Experiment", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0F3040 !important; color: #f1f5f9 !important; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #0a2533 !important;
        border: 1px solid #1b4b61 !important;
        border-radius: 10px;
    }
    .badge-filter-box {
        background: rgba(56, 189, 248, 0.12);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.35);
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
        margin-bottom: 6px;
    }
    .stTextArea textarea, .stTextInput input, div[data-baseweb="select"] {
        background-color: #09202c !important;
        border: 1px solid #1b4b61 !important;
        color: #f1f5f9 !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧪 Test: Side-by-Side Metadata & Auto-DB Ingestion")

# -------------------------------------------------------------
# 4. SIDE-BY-SIDE INTAKE & METADATA GRID
# -------------------------------------------------------------
col_intake, col_meta = st.columns([1.6, 1.1])

with col_intake:
    with st.container(border=True):
        st.markdown('<span class="badge-filter-box">📝 Bug Report / Stack Trace</span>', unsafe_allow_html=True)
        bug_report = st.text_area(
            "Bug Report / Stack Trace",
            height=220,
            key="test_bug_report",
            placeholder="Paste code trace logs or runtime errors here...",
            label_visibility="collapsed"
        )
        
        st.markdown('<span class="badge-filter-box">🎯 Similar Bugs Retrieval Depth</span>', unsafe_allow_html=True)
        top_n = st.slider("Top N", min_value=3, max_value=15, value=5, key="test_top_n", label_visibility="collapsed")

with col_meta:
    with st.container(border=True):
        st.markdown("##### 📌 METADATA CONTEXT")
        
        st.caption("Project Name")
        project_name = st.text_input("Project Name", value="AI Smart Bug Analyzer", key="test_proj_name", label_visibility="collapsed")
        
        st.caption("Reporter Name *")
        reporter_name = st.text_input("Reporter Name", value="Developer", key="test_rep_name", label_visibility="collapsed")
        
        st.caption("Developer Department")
        dev_dept = st.selectbox(
            "Developer Department",
            ["Backend Core API", "Frontend UI", "Py coder", "DevOps / Infra", "QA & Testing", "Database / Data Eng"],
            key="test_dev_dept",
            label_visibility="collapsed"
        )
        
        st.caption("Group Number")
        group_num = st.selectbox(
            "Group Number",
            ["Group 1", "Group 2", "Group 3", "Group 4", "Group 5"],
            key="test_group_num",
            label_visibility="collapsed"
        )

# -------------------------------------------------------------
# 5. AUTOMATIC TRIGGER & DATABASE SAVE
# -------------------------------------------------------------
st.write("")
if st.button("🚀 Trigger Bug Analysis & Auto-Save DB"):
    if bug_report.strip() == "":
        st.warning("Please paste some text in the bug report box first.")
    else:
        generated_bug_id = f"BUG-{datetime.now().strftime('%H%M%S')}"
        now_ts = datetime.now().isoformat()
        
        # Save directly to the new SQLite database
        conn = sqlite3.connect(DEV_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Developer_Submission 
            (bug_id, project_name, reporter_name, developer_department, group_number, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (generated_bug_id, project_name, reporter_name, dev_dept, group_num, now_ts))
        conn.commit()
        conn.close()
        
        st.success(f"✅ Submission processed! Saved as **{generated_bug_id}** to `{DEV_DB_PATH}`")

# -------------------------------------------------------------
# 6. VERIFY SAVED DATA IN REAL TIME
# -------------------------------------------------------------
st.divider()
st.subheader("📊 Live Database Viewer (Developer_Submission.db)")

conn = sqlite3.connect(DEV_DB_PATH)
saved_df = pd.read_sql("SELECT * FROM Developer_Submission ORDER BY submission_id DESC", conn)
conn.close()

if not saved_df.empty:
    st.dataframe(saved_df, use_container_width=True)
else:
    st.info("No records in `Developer_Submission.db` yet. Click the button above to test saving.")