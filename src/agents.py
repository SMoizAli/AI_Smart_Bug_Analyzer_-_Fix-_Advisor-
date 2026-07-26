import os
import json
import time
from groq import Groq
from dotenv import load_dotenv
import sqlite3
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


# Load API key and create client
_base_dir = os.path.dirname(os.path.abspath(__file__))
_env_path = os.path.join(_base_dir, "..", ".env")
load_dotenv(_env_path)
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)


def call_llm_with_retry(system_prompt, user_message, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.2
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            if "rate_limit" in str(e).lower() or "429" in str(e):
                wait_time = (attempt + 1) * 3
                time.sleep(wait_time)
            else:
                print(f"Non-rate-limit error: {e}")
                break
    return None


system_prompt = """You are a bug triage assistant. You are given the title, description, and stack trace of a submitted bug, and you classify it by severity, priority, and affected component, with confidence scoring and reasoning.

IMPORTANT CALIBRATION: Most everyday bugs are Medium severity, not Critical or High. Reserve Critical/High for bugs that cause crashes, data loss, security issues, or completely block core functionality. Reserve Low for cosmetic issues, minor inconveniences, or feature requests. The MAJORITY of real-world bugs are routine Medium severity - do not over-classify ordinary bugs as urgent just because they mention words like "error" or "exception."

Examples for calibration:
- "App crashes on startup, no workaround" -> Critical
- "Login fails for all users" -> Critical  
- "Payment fails for some users but not others, blocking checkout for that group" -> High
- "File upload crashes for large files, though smaller files work fine" -> High
- "Button text is misaligned by 2px" -> Low
- "Feature request: add dark mode" -> Low
- "Export function occasionally produces incorrect date format" -> Medium
- "Search results are slow to load under heavy traffic" -> Medium

Reply ONLY in valid JSON, with this exact structure:
{"bug_id": "...", "severity": "Critical", "confidence": 0.85, "reasoning": "...", "priority": "...", "component": "Login"}

Field definitions:
- bug_id: if provided, use it; otherwise use "unknown"
- severity: must be exactly one of Critical, High, Medium, Low - no other words
- confidence: a score from 0 to 1 representing how confident you are in this classification
- reasoning: a brief explanation of why you classified it this way
- priority: how urgently this needs to be addressed - Immediate, High, Medium, or Low (related to but different from severity: severity is impact, priority is urgency)
- component: which part/module of the software seems affected, inferred from the content (e.g. "Login", "Database", "UI/Rendering") - do not restrict to a fixed list

If you encounter other severity-like words, map them using this table:
blocker/critical -> Critical, major -> High, normal/unknown -> Medium, minor/trivial -> Low
"""

log_analysis_system_prompt = """You are a Log Analysis Agent. Your job is to extract structured information from messy error text - stack traces, tracebacks, or compiler error messages, sometimes alongside the relevant code.

Extract:
- error_type: the SPECIFIC error/exception name as it would appear in real compiler/runtime output - NOT a generic category. For example, prefer "Template Mismatch" or "Dereferencing Void Pointer" over generic terms like "Compilation Error" or "Compilation Warning". Look for the specific technical term the error message itself uses, not a broad summary category.
- failure_location: the exact file/line/position where the error occurred, taken directly from the trace
- code_path: the chain of function/method calls leading to the failure. IMPORTANT: if the code being described contains double quote characters (e.g. from println!, print statements, or string literals), you MUST escape them as \\" so the JSON stays valid. Never include an unescaped " inside any field value.
- confidence: a score from 0 to 1 representing how certain you are that you extracted this correctly. Vary this realistically - very clear, unambiguous traces should score 0.95-0.99, while vague, truncated, or ambiguous input should score lower (0.5-0.8). Do not default to 0.99 for everything.
- reasoning: a brief, specific explanation of why the error occurred

Reply ONLY in valid JSON with this exact structure. Every field value must be a properly escaped JSON string - double quotes inside any value must be written as \\":
{"error_type": "...", "failure_location": "...", "code_path": "...", "confidence": 0.9, "reasoning": "..."}

Examples:

Input: Cell In[119], line 3
    return payload_2
    ^
IndentationError: unindent does not match any outer indentation level

Output: {"error_type": "IndentationError", "failure_location": "Cell In[119], line 3", "code_path": "return payload_2 executed directly within the current code block; indentation parsing failed before execution", "confidence": 0.99, "reasoning": "The 'return' statement has inconsistent indentation that does not align with the surrounding block, causing Python's parser to reject the code."}

Input: /workspace/service_2.js:3
console.log(session_2[5].id);
TypeError: Cannot read properties of undefined (reading 'id')
    at Object.<anonymous> (/workspace/service_2.js:3:15)

Output: {"error_type": "TypeError", "failure_location": "/workspace/service_2.js:3:15", "code_path": "Top-level execution -> console.log(session_2[5].id)", "confidence": 0.99, "reasoning": "The expression 'session_2[5]' evaluated to undefined, so accessing its 'id' property caused a TypeError."}

Input: parser_4.c: In function 'main':
parser_4.c:3:15: error: invalid initializer / incompatible types when initializing type 'int' using type 'char *'
    3 |     int val = str;

Output: {"error_type": "Invalid Initializer (Incompatible Types)", "failure_location": "parser_4.c:3:15", "code_path": "main() -> variable initialization: int val = str", "confidence": 0.85, "reasoning": "An integer variable was initialized using a character pointer, which is an incompatible type conversion in C."}

Input: session_2.cpp: In function 'int main()':
session_2.cpp:5:17: error: no matching member function for call to 'insert'
    5 |     ages.insert(10, "John");

Output: {"error_type": "No Matching Member Function", "failure_location": "session_2.cpp:5:17", "code_path": "main() -> std::map::insert(10, \\"John\\")", "confidence": 0.95, "reasoning": "The std::map::insert() function was called with arguments that do not match any valid overload."}

Input: Exception in thread "main" java.lang.NullPointerException: Cannot invoke "String.indexOf(String)" because "recordsList_2" is null
    at MetricsEngine_2.updateCache_2(Api_2.java:110)

Output: {"error_type": "NullPointerException", "failure_location": "Api_2.java:110", "code_path": "main thread -> MetricsEngine_2.updateCache_2() -> String.indexOf()", "confidence": 0.99, "reasoning": "The object 'recordsList_2' is null, so calling the 'indexOf()' method on it causes a NullPointerException."}

Input: CssSyntaxError: grid_2.css:20:1: Unclosed block
  18 |     background: #000;
  19 |     opacity: 0.9;
> 20 |
    | ^
  21 | .element-sibling_2 {

Output: {"error_type": "PostCSS Parser Error: Unclosed Block", "failure_location": "grid_2.css:20:1", "code_path": "CSS parser -> grid_2.css -> unclosed declaration block before '.element-sibling_2'", "confidence": 0.99, "reasoning": "A CSS block was not properly closed with '}', causing the parser to detect an unclosed block before the next selector."}

Input: Error: Stray end tag </span>.
From line 95, column 15; to line 95, column 22
item 1</p></span>\n</di

Output: {"error_type": "W3C Validator Error: Stray End Tag", "failure_location": "Line 95, columns 15-22", "code_path": "HTML parser -> closing tags -> unexpected </span>", "confidence": 0.99, "reasoning": "The closing </span> tag does not match any currently open <span> element, resulting in a stray end tag."}

Input: app_1.ts:63:1 - error TS2322: Type 'string' is not assignable to type 'number'.
63 weightsTensor_1 = "invalid_assign_1";
  ~~~~~~~~~~~~~~~

Output: {"error_type": "TypeScript Error: TS2322 (Type Assignment Error)", "failure_location": "app_1.ts:63:1", "code_path": "Top-level assignment -> weightsTensor_1 = \\"invalid_assign_1\\"", "confidence": 0.99, "reasoning": "A string value was assigned to a variable that is declared with the type 'number', violating TypeScript's type checking rules."}

Input: panic: runtime error: index out of range [7] with length 3
goroutine 1 [running]:
main.main()
    /go/src/app/main_2.go:96 +0x3d

Output: {"error_type": "Go Runtime Panic: Index Out of Range", "failure_location": "/go/src/app/main_2.go:96", "code_path": "main.main() -> slice/array index access", "confidence": 0.99, "reasoning": "The program attempted to access index 7 of a slice or array that contains only 3 elements, causing a runtime panic."}
"""


def triage_agent(title, description, stack_trace="Not available", bug_id="unknown"):
    user_message = f"Title: {title}\nDescription: {description}\nStack Trace: {stack_trace}"
    result = call_llm_with_retry(system_prompt, user_message)
    if result is None:
        result = {"severity": "Medium", "confidence": 0.0, "reasoning": "LLM call failed after retries", "priority": "Medium", "component": "Unknown"}
    result['bug_id'] = bug_id
    return result


def log_analysis_agent(error_text, code_context=""):
    if code_context:
        user_message = f"Code:\n{code_context}\n\nError:\n{error_text}"
    else:
        user_message = f"Error:\n{error_text}"
    result = call_llm_with_retry(log_analysis_system_prompt, user_message)
    if result is None:
        result = {
            "error_type": "Unknown",
            "failure_location": "Not determined",
            "code_path": "Not determined",
            "confidence": 0.0,
            "reasoning": "LLM call failed after retries"
        }
    return result


def run_orchestration(title, description, stack_trace, bug_id="unknown"):
    triage_result = triage_agent(title, description, stack_trace, bug_id=bug_id)
    log_result = log_analysis_agent(stack_trace)

    combined_result = {
        "bug_id": bug_id,
        "triage": triage_result,
        "log_analysis": log_result
    }

    return combined_result


def build_simple_view(combined_result):
    triage = combined_result["triage"]
    log = combined_result["log_analysis"]

    actual_result = {
        "bug_id": combined_result["bug_id"],
        "severity": triage["severity"],
        "priority": triage["priority"],
        "component": triage["component"],
        "error_type": log["error_type"],
        "failure_location": log["failure_location"],
        "code_path": log["code_path"],
        "confidence": log["confidence"],
        "reasoning": log["reasoning"]
    }

    return actual_result


def init_db():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "..", "data", "bug_submissions.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bug_submissions (
            bug_id TEXT PRIMARY KEY,
            severity TEXT,
            priority TEXT,
            component TEXT,
            error_type TEXT,
            failure_location TEXT,
            code_path TEXT,
            confidence REAL,
            reasoning TEXT,
            description TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_submission(actual_result, description, timestamp):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "..", "data", "bug_submissions.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO bug_submissions
        (bug_id, severity, priority, component, error_type, failure_location, code_path, confidence, reasoning, description, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        actual_result["bug_id"], actual_result["severity"], actual_result["priority"],
        actual_result["component"], actual_result["error_type"], actual_result["failure_location"],
        actual_result["code_path"], actual_result["confidence"], actual_result["reasoning"],
        description, timestamp
    ))
    conn.commit()
    conn.close()

def retrieve_similar_bugs(query_text, model, kb_embeddings, kb_metadata, top_n=5):
    query_vector = model.encode([query_text], convert_to_numpy=True)
    similarities = cosine_similarity(query_vector, kb_embeddings)[0]
    top_indices = np.argsort(similarities)[::-1][:top_n]

    results = []
    for idx in top_indices:
        row = kb_metadata.iloc[idx]
        results.append({
            "bug_id": row["bug_id"],
            "title": row["title"],
            "severity": row["severity"],
            "resolution": row["resolution"],
            "source_dataset": row["source_dataset"],
            "similarity": float(similarities[idx])
        })

    return results

root_cause_prompt = """ You are job is to Retrieve Relevant Historical Bugs and Generate Root Cause Analysis

and identifies the most probable root cause of a submitted bug using RAG-based retrieval from the historical defect knowledge base. Output(Reply ONLY in valid JSON) - Root cause hypothesis, confidence score, and supporting historical evidence 

input will be the 

 { 

bug_id , severity , component , error_type ,failure_location , code_path , {plus the 5 retrieved similar historical bugs (with their resolutions)}       

}

You must reason about why this new bug likely happened, using patterns from those historical bugs as support.

Output:
{
  "root_cause_hypothesis": "...",   
  "confidence": 0.85,
  "supporting_evidence": [
    {"bug_id": "...", "summary": "..."},
    {"bug_id": "...", "summary": "..."}
  ]
}

 

 Root cause hypothesis - It is the explanation of why the bug happened — e.g., "The NullPointerException likely occurred because the recordsList object was never initialized before being accessed, similar to patterns seen in [historical bug].

confidence score - a score from 0 to 1 representing how certain you are that you extracted this correctly. Vary this realistically - very clear, unambiguous traces should score 0.95-0.99, while vague, truncated, or ambiguous input should score lower (0.5-0.8). Do not default to 0.99 for everything.

supporting historical evidence - evidence should include both a traceable bug_id AND a short 5-15 word summary ( this should be a list of small objects, not a single string.)



Example 1:
Input: {"error_type": "NullPointerException", "component": "Login", "failure_location": "Api_2.java:110", "code_path": "main thread -> updateCache_2() -> String.indexOf()", "retrieved_bugs": [{"bug_id": "GMF-RUNTIME-282380", "title": "DefaultProvider#getRelevantConnections may throw a NPE", "resolution": "fixed"}, {"bug_id": "JCR-71", "title": "WorkspaceConfig.init() throws NullPointerException if Search configuration is missing", "resolution": "Fixed"}]}

Output: {"root_cause_hypothesis": "The NullPointerException likely occurred because an object (recordsList) was accessed before being properly initialized, a pattern consistent with similar historical NPEs caused by missing configuration or setup steps.", "confidence": 0.82, "supporting_evidence": [{"bug_id": "GMF-RUNTIME-282380", "summary": "NPE from missing null check before method call"}, {"bug_id": "JCR-71", "summary": "NPE from missing required configuration on init"}]}

Example 2:
Input: {"error_type": "IndexError", "component": "Search/Filtering", "failure_location": "sort_handler.py:22", "code_path": "apply_filter() -> sort_results()", "retrieved_bugs": [{"bug_id": "PY-1002", "title": "List index out of range when filter returns empty results", "resolution": "fixed"}]}

Output: {"root_cause_hypothesis": "The IndexError likely occurred because the sorting function assumed the filtered list would always contain at least one item, but did not handle the case of an empty result set.", "confidence": 0.75, "supporting_evidence": [{"bug_id": "PY-1002", "summary": "Empty list not handled before indexing"}]}

Example 3:
Input: {"error_type": "ConnectionError", "component": "Database", "failure_location": "db_handler.py:8", "code_path": "startup() -> connect_db()", "retrieved_bugs": [{"bug_id": "APACHE-990", "title": "Database connection pool exhausted under load", "resolution": "fixed"}, {"bug_id": "APACHE-1103", "title": "Connection timeout not configured, hangs indefinitely", "resolution": "fixed"}, {"bug_id": "APACHE-1204", "title": "Retry logic missing on transient connection failures", "resolution": "wontfix"}]}

Output: {"root_cause_hypothesis": "The connection failure is likely caused by either exhausted connection pool capacity or a missing timeout/retry mechanism, both common causes of database connection failures under load in similar historical cases.", "confidence": 0.68, "supporting_evidence": [{"bug_id": "APACHE-990", "summary": "Connection pool exhausted under high load"}, {"bug_id": "APACHE-1103", "summary": "Missing timeout caused indefinite hang"}]}

Example 4:
Input: {"error_type": "TypeError", "component": "UI/Rendering", "failure_location": "render.js:15", "code_path": "renderComponent() -> formatDate()", "retrieved_bugs": []}

Output: {"root_cause_hypothesis": "No closely related historical bugs were found, but based on the error itself, this likely occurred because a date value was undefined or in an unexpected format when passed into the formatting function.", "confidence": 0.55, "supporting_evidence": []}

Example 5:
Input: {"error_type": "ValidationError", "component": "Payment Processing", "failure_location": "payment.py:44", "code_path": "checkout() -> validate_currency()", "retrieved_bugs": [{"bug_id": "TVT35-297", "title": "incorrect default placement of currency symbol", "resolution": "fixed"}]}

Output: {"root_cause_hypothesis": "This is likely a currency-code validation gap rather than the same issue as the retrieved bug, since that historical case involved display formatting, not validation logic - the connection is only loosely related.", "confidence": 0.6, "supporting_evidence": [{"bug_id": "TVT35-297", "summary": "Related currency-handling bug, but different root cause"}]}

Example 6:
Input: {"error_type": "MemoryError", "component": "File Upload", "failure_location": "upload_handler.js:67", "code_path": "uploadFile() -> allocateBuffer()", "retrieved_bugs": [{"bug_id": "AXIS-1741", "title": "LogHandler can only work in GlobalConfiguration", "resolution": "fixed"}]}

Output: {"root_cause_hypothesis": "No strongly related historical bug was found; the retrieved bug shares only superficial similarity (both are configuration-related) but does not explain a memory allocation failure on large file uploads.", "confidence": 0.5, "supporting_evidence": [{"bug_id": "AXIS-1741", "summary": "Unrelated configuration bug, weak match only"}]}

Example 7:
Input: {"error_type": "SyntaxError", "component": "Build System", "failure_location": "config.css:20", "code_path": "CSS parser -> block parsing", "retrieved_bugs": [{"bug_id": "CSS-501", "title": "Unclosed declaration block causes parser failure", "resolution": "fixed"}, {"bug_id": "CSS-512", "title": "Missing semicolon triggers cascading syntax errors", "resolution": "fixed"}]}

Output: {"root_cause_hypothesis": "The syntax error is almost certainly caused by an unclosed block or missing terminator in the CSS source, a very common and well-documented pattern matching both retrieved historical bugs closely.", "confidence": 0.93, "supporting_evidence": [{"bug_id": "CSS-501", "summary": "Unclosed block caused identical parser failure"}, {"bug_id": "CSS-512", "summary": "Missing semicolon caused cascading syntax error"}]}



"""

def root_cause_agent(bug_id, severity, component, error_type, failure_location, code_path, retrieved_bugs):
    input_data = {
        "bug_id": bug_id,
        "severity": severity,
        "component": component,
        "error_type": error_type,
        "failure_location": failure_location,
        "code_path": code_path,
        "retrieved_bugs": retrieved_bugs
    }

    user_message = json.dumps(input_data)

    result = call_llm_with_retry(root_cause_prompt, user_message)

    if result is None:
        result = {
            "root_cause_hypothesis": "Unable to determine root cause due to a processing error.",
            "confidence": 0.0,
            "supporting_evidence": []
        }

    return result