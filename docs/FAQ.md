

### 1. 🧠 Knowledge Base Tab

* **What is the Knowledge Base Tab:**
The Knowledge Base (KB) repository view provides visibility into the historical, indexed bug solutions and vector embeddings dataset (`knowledge_base_with_severity.csv` and `embeddings_real.npy`) that the system uses to search for similar past defects.


* **What are Added ROWS:**
These represent verified defect solutions. When a developer reviews a recommended fix and clicks **"✅ Fix Worked"**, the platform executes `add_resolved_bug_to_kb(...)`, appends the new fix into the vector repository/database, and marks its status as `resolved_added_to_kb`.


* **Is it Dynamic or Static:**
It is a **hybrid (Dynamic on top of Static)** dataset. The base file contains static historical records (e.g., ~29,161 indexed defects), but it dynamically expands whenever developers verify new working fixes through the app.


* **Why Top Component in Analytics vs. Knowledge Base is Different:**
* **Analytics Dashboard:** Analyzes live incoming tickets submitted to `bug_submissions.db` by your active team.


* **Knowledge Base Dashboard:** Analyzes the broader historical training dataset loaded from `knowledge_base_with_severity.csv`.


* Because the historical dataset reflects past multi-year records across all modules while the analytics dashboard tracks recent user submissions, their dominant components frequently differ.





---

### 2. 🏠 Telemetry Dashboard

* **What is the Telemetry Dashboard:**
The centralized command center that provides real-time monitoring of ingested bug tickets, severity counts, resolution statuses, and manual reminder controls.


* **Is it Static or Dynamic:**
It is **100% Dynamic**. Every time a user submits a bug or verifies an outcome, the telemetry feed queries SQLite and recalculates metrics instantly on page load.


* **What Database Does it Store / Query:**
* `bug_submissions.db` (stores tickets, statuses, severity, root cause hypotheses, and recommended fixes).


* `Developer_Submission.db` (stores metadata context like reporter name, project name, and department).


* `auth_users.db` (stores registered credentials and login activity).




* **What are Critical Bugs and Top Contributor:**
* **Critical Bugs:** A count of tickets where the classified `severity` is marked as `critical`, `blocker`, or `fatal`.


* **Top Contributor:** The developer or user email that has logged the highest number of defect submissions in `Developer_Submission.db`.





---

### 3. 📚 User Guide vs. 3️⃣ About The App

* **User Guide (`docs/User_guide.md`):**
* An operational, step-by-step instructional manual for end-users.


* It shows *how* to paste stack traces, adjust similarity depth sliders, interpret confidence scores, and confirm fix outcomes.




* **About The App (`README.md`):**
* A high-level technical and architectural overview of the project.


* It explains project objectives, tech stack (Streamlit, SentenceTransformers, SQLite, Resend API), system topology, and deployment setups.




* **How They Differ:**
* **User Guide** = User actions and workflows (*"How do I submit a bug?"*).


* **About The App** = Technical documentation and system purpose (*"What technologies power this platform?"*).





---

### 4. Output Display: Summary vs. Full Details

* **Summary View:**
Provides concise metric cards (Severity, Priority, Component) and condensed previews of the root cause and fix for fast reading.


* **Full Details (JSON View):**
Reveals raw intermediate agent telemetry when expanding **"Show full details (all agents)"**, allowing engineers to inspect full JSON payloads, code diff blocks (`before`/`after`), confidence distributions, and reference citations.



---

### 5. Multi-Agent Orchestration & Resilient Fallback Architecture

* **What is Multi-Agent Orchestration:**
A pipelined architecture where specialized autonomous modules divide complex diagnostic tasks into distinct steps:


1. **Triage Agent:** Determines severity, priority, and component.


2. **Log Analysis Agent:** Extracts failure locations and error categories.


3. **Retrieval Agent:** Queries semantic vector embeddings (`SentenceTransformer`) for similar historical solutions.


4. **Root Cause Agent:** Synthesizes error patterns and evidence into an explanatory hypothesis.


5. **Duplicate Detection Agent:** Identifies duplicate tickets to prevent redundant engineering work.


6. **Remediation Agent:** Synthesizes all gathered intelligence to produce an actionable code fix and validation steps.




* **How the Remediation Agent Works if Other Agents Fail:**
The platform uses **defensive graceful degradation** with isolated `try...except` safety blocks around every agent call:


* **If Retrieval Fails:** Passes an empty historical list (`retrieved_bugs = []`).


* **If Root Cause Fails:** Populates a fallback hypothesis with `confidence: 0.0`.


* **If Duplicate Detection Fails:** Falls back to `duplicate_bug = None`.


* **Remediation Agent Behavior:** Operates purely on the available raw stack trace and triage metadata if upstream agents fail. If remediation itself encounters an exception, it generates a structured fallback response (`confidence: 0.0`, error reason recorded) rather than allowing the application to crash.

## Groq graphs — can you run 3-7 bugs today?

Looking at your screenshots: the `openai/gpt-oss-120b` Total Tokens chart shows a **rate limit ceiling at 240K**, and the tooltips show usage at specific moments (12.1K-43.8K tokens, "6% consumed," "23% consumed" at different points) — meaning you're nowhere near the ceiling. Requests chart shows a limit around 900, with actual usage in the tens. **Yes — this comfortably supports 3-7 bug submissions today.** Each bug is roughly 4 LLM calls, likely a few thousand tokens total per bug — even 7 bugs would use a small fraction of your 240K headroom. This is a much higher ceiling than the old Llama model's 100K/day hard cap that caused your earlier problem.

---

## SUBMIT TAB

**1. What it is:** The "Submit Bug" page — user pastes or uploads a bug report/stack trace, and the pipeline runs automatically once text is present (no submit button needed).

**2. Submission options — two:** paste text directly into the text area, **or** upload a `.txt`/`.log` file.

**3. Sequential, not parallel.** Confirmed throughout — Triage+Log Analysis run together via `run_orchestration()`, then Retrieval, then Root Cause, then Duplicate Detection, then Remediation, each step waiting on the previous one's output.

**4. Input per agent:**
- Triage: title, description, stack_trace, bug_id
- Log Analysis: stack_trace (+ optional code_context)
- Root Cause: severity, component, error_type, failure_location, code_path, plus the top-N retrieved historical bugs
- Duplicate Detection: new bug's description, error_type, component, reasoning — compared only against your own live SQLite submissions, not the historical KB
- Remediation: everything upstream — severity, root cause, duplicate match, historical references

**5. If an agent fails:** each call is wrapped in try/except in `app.py`. On failure, it substitutes a fallback (e.g. `"Unable to determine root cause due to a processing error"`, confidence 0.0) and the pipeline **continues** rather than crashing the whole page — fault isolation per agent.

**6. Retrieval — dynamic computation over a mostly-static base.** Every submission triggers a fresh cosine-similarity search across the current embeddings file at that moment. The KB itself doesn't change except when the growth mechanism appends a new confirmed-fix entry — so the *search* is always live/dynamic, but the *underlying data* only grows on confirmed fixes, it isn't recomputed or refreshed on a schedule.

**7. RAG = Retrieval-Augmented Generation.** Your bug's text is embedded, compared via cosine similarity against ~56,862+ historical bugs, and the top matches are handed to the Root Cause Agent as grounding evidence — so its hypothesis is anchored in real precedent, not just the LLM's raw parametric knowledge.

**8. Exception handling for each agent + retrieval:** every individual agent function and `retrieve_similar_bugs()` has its own try/except in `app.py`, each producing a safe fallback value (empty list for retrieval, fallback dict for agents) rather than raising an unhandled error.

**9. Analysis Summary vs. Full Details:** Summary = the compact top view (severity/priority/component metrics + one-line summaries). Full Details = a button revealing the raw JSON output of all 4 agent calls — for technical/audit-level inspection.

**10. Why shown twice:** they serve different audiences — Summary for a quick human scan, Full Details for verification/debugging. Not redundant, two depths of the same result.

**11. Supporting evidence / confidence / reasoning:**
- Supporting evidence = list of `{bug_id, summary}` historical bugs the Root Cause/Remediation agents cite.
- Confidence = a 0-1 self-reported score the LLM is instructed to vary realistically (not defaulted high) — **except** in Duplicate Detection, where the similarity score is a real, deterministic cosine-similarity calculation, not an LLM guess.
- Reasoning = free-text explanation the LLM generates for its own decision.

**12. Timing — honest gap here.** We never formally benchmarked exact per-agent latency in this conversation. What we know: each agent is one LLM API call, so total pipeline time is the sum of ~4-5 sequential Groq calls — typically seconds each. I don't have a verified precise number to state as fact; if asked, it's safer to say "typically well under a minute, since we never measured and disclosed an exact benchmark" rather than quote a number we didn't actually test.

---

## ANALYTICS DASHBOARD

**1. What it is vs. "telemetry":** it's the Defect Pattern Analytics dashboard — tracks *bug content patterns* (severity/component/root-cause trends across submissions). A "telemetry dashboard" usually means *system health* (uptime, latency, error rates of the app itself) — **we never built that**; worth being clear this dashboard is about bug data, not infrastructure monitoring.

**2. Grouping:** severity (raw), component (normalized via a manually-reviewed merge map), and root cause (via `AgglomerativeClustering` on `reasoning` text embeddings, threshold 0.35, derived empirically from the real similarity distribution). The daily bar graph = Submission Activity, counting bugs by calendar date.

**3. Chart types:** Plotly pie charts for severity and component (proportional/categorical breakdowns), Plotly bar chart for submission activity (time-series counts) — pie for "share of whole," bar for "count over time."

**4. "Verified / Pending Review / Not Fix status in frequent fixes"** — **this doesn't match anything we built**, and I don't want to invent an answer. Our real status values are `pending_review` (default), `resolved_added_to_kb`, `resolved_kb_append_failed`, `unresolved` — tied to the Confirm Fix Outcome buttons, not a separate "frequent fixes" feature. If your mentor asks this exact phrasing, I'd clarify what they mean before answering, since it may be describing something not present in the actual app.

---

## ASK (mentor Q&A prep)

**1. Sequential** (repeat of above). "Pending review" = `pending_review`, the default status every bug gets until the user clicks Fix Worked/Didn't Work.

**2. "No error in root cause group"** — I'm not confident what this refers to; it doesn't map cleanly to a documented feature. Possibly confused with the `"Unclassified (Log Analysis extraction failed)"` relabeling of Unknown clusters — I'd ask for clarification rather than guess.

**3. Model migration:** from **`llama-3.3-70b-versatile`** to **`openai/gpt-oss-120b`**, because Groq announced the former's decommission (~Aug 16, 2026) with roughly one day's notice. **Tested:** made an isolated call with a strict JSON system prompt before switching, confirmed the response came back as clean JSON with no extra reasoning text wrapped around it — then verified with a real bug through the full app. **Why this model:** it was Groq's officially stated recommended replacement (alongside Qwen3.6-27B, which we did not switch to).

**4. Agent failure handling** — same fault-isolation answer as above.

**5. Severity decision:** the Triage Agent, via LLM judgment guided by explicit calibration examples in its prompt (e.g., "most bugs are Medium, not Critical") — not a rule-based formula, a prompted classification.

**6. Techniques/libraries:** Python, Streamlit, Groq API, sentence-transformers (`all-MiniLM-L6-v2`), scikit-learn (cosine similarity, AgglomerativeClustering), pandas, NumPy, SQLite3, Plotly, python-dotenv, Git/GitHub with Git LFS, deployed on Streamlit Community Cloud.

**7. Severity vs. Priority:** per your own Triage prompt's definition — **severity = impact** (how bad the effect is), **priority = urgency** (how fast it needs addressing). Related but distinct; a bug can be severe but not urgent, or urgent but not severe.


