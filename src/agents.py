import os
import json
import time
from groq import Groq
from dotenv import load_dotenv

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