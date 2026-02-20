import json
import time
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from google.api_core.exceptions import ResourceExhausted
import streamlit as st
import os

if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    API_KEY = os.getenv("GEMINI_API_KEY")

MODEL_FALLBACKS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash-001",
    "gemini-2.0-flash-lite-001",
    "gemini-flash-lite-latest",
]

EVAL_PROMPT = PromptTemplate(
    input_variables=["student", "official", "rules"],
    template="""
You are an exam evaluation engine.

CRITICAL INSTRUCTIONS:
- Follow ONLY the evaluation rules provided by the user.
- Do NOT assume any marking scheme.
- If a rule is missing, do NOT apply it.

Evaluation Rules:
{rules}

Student Answers:
{student}

Official Answer Key:
{official}

Tasks:
1. Evaluate answers strictly per rules.
2. Count:
   - number of correct questions
   - number of incorrect questions
   - total marks obtained
   - total possible marks (as per rules)

Output STRICT JSON ONLY:

{{
  "total_questions": number,
  "correct_count": number,
  "incorrect_count": number,
  "marks_obtained": number,
  "total_marks": number
}}

NO explanations.
NO extra text.
"""
)

def parse_answers_robust(text: str):
    """
    Parses OCR text into {Q#: answer} dictionary robustly.
    Handles:
    - "Q1: A", "Q1 . A", "Q1 A", "Q1-A"
    - Extra spaces and line breaks
    - Multi-answer like "A,B,C" with spaces
    """
    answers = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        m = re.match(r"(Q\d+)[\s\.: -]*([\w, ]+)", line, re.I)
        if m:
            q = m.group(1).upper()
            ans = m.group(2).replace(" ", "")  
            if "," in ans:
                ans = sorted([x.strip().upper() for x in ans.split(",")])
            else:
                ans = ans.upper()
            answers[q] = ans
    return answers

def normalize_answer(ans):
    if isinstance(ans, str):
        ans = ans.strip().upper()
        if "," in ans:
            return sorted([x.strip() for x in ans.split(",")])
        return ans
    try:
        return float(ans)
    except:
        return ans

def normalize_answers_dict(answers_dict):
    normalized = {}
    for q, ans in answers_dict.items():
        normalized[q] = normalize_answer(ans)
    return normalized
def local_evaluate(student_answers: dict, official_answers: dict, rules_text: str):
    correct_count = 0
    incorrect_count = 0
    marks_obtained = 0
    total_marks = 0

    NEGATIVE = 0
    PARTIAL = False
    for line in rules_text.splitlines():
        line = line.lower()
        if "negative" in line:
            try:
                NEGATIVE = float(line.split()[-1])
            except:
                NEGATIVE = 0
        if "partial" in line:
            PARTIAL = True

    for q, correct_ans in official_answers.items():
        student_ans = student_answers.get(q, None)
        total_marks += 1

        if student_ans is None:
            incorrect_count += 1
            marks_obtained -= NEGATIVE
            continue

        if isinstance(correct_ans, list):
            if isinstance(student_ans, list):
                matches = set(correct_ans) & set(student_ans)
                if PARTIAL:
                    score = len(matches) / len(correct_ans)
                    marks_obtained += score
                    if score == 1:
                        correct_count += 1
                    else:
                        incorrect_count += 1
                else:
                    if set(student_ans) == set(correct_ans):
                        marks_obtained += 1
                        correct_count += 1
                    else:
                        incorrect_count += 1
                        marks_obtained -= NEGATIVE
            else:
                incorrect_count += 1
                marks_obtained -= NEGATIVE
        else:
            if student_ans == correct_ans:
                correct_count += 1
                marks_obtained += 1
            else:
                incorrect_count += 1
                marks_obtained -= NEGATIVE

    if marks_obtained < 0:
        marks_obtained = 0

    return {
        "total_questions": len(official_answers),
        "correct_count": correct_count,
        "incorrect_count": incorrect_count,
        "marks_obtained": round(marks_obtained, 2),
        "total_marks": total_marks
    }

def smart_evaluate(student_answers: dict, official_answers: dict, rules_text: str):
    student_answers = normalize_answers_dict(student_answers)
    official_answers = normalize_answers_dict(official_answers)
    last_error = None

    for model_name in MODEL_FALLBACKS:
        try:
            llm = ChatGoogleGenerativeAI(
                api_key=API_KEY,
                model=model_name,
                temperature=0
            )
            chain = EVAL_PROMPT | llm
            response = chain.invoke({
                "student": json.dumps(student_answers, indent=2),
                "official": json.dumps(official_answers, indent=2),
                "rules": rules_text
            })
            return json.loads(response.content)
        except Exception:
            last_error = True
            continue

    # Fallback to local evaluation if Gemini fails
    return local_evaluate(student_answers, official_answers, rules_text)
