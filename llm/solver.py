from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from google.api_core.exceptions import ResourceExhausted
import time
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

prompt = PromptTemplate(
    input_variables=["exam", "questions"],
    template="""
Solve the following {exam} questions.

For EACH question use this format:

Question:
<Write the full question>

Solution (Brief):
<Short, clear explanation. Keep it concise. No long derivations.>

Ans: <Final Answer>

Rules:

1) MCQ:
   Ans: A) Option Text

2) MSQ:
   Ans: A) Text, C) Text
   (Sort letters alphabetically)

3) NAT:
   Ans: 30 m/s
   (Include unit if applicable)

Keep answers precise.
No unnecessary commentary.
Maintain clean formatting.

QUESTIONS:
{questions}

"""
)

def solve_questions(exam, questions):
    last_error = None

    for model_name in MODEL_FALLBACKS:
        try:
            llm = ChatGoogleGenerativeAI(
                api_key=API_KEY,
                model=model_name,
                temperature=0
            )

            chain = prompt | llm
            response = chain.invoke({
                "exam": exam,
                "questions": questions
            })

            print(f"✅ Used model: {model_name}")
            return response.content

        except ResourceExhausted:
            print(f"⚠️ Quota exhausted for {model_name}, switching model...")
            time.sleep(1)

        except Exception as e:
            print(f"⚠️ Error with {model_name}: {e}")
            time.sleep(1)

    raise RuntimeError("❌ All Gemini models exhausted")


# -------------------------------
# 🔹 Batching logic (20–30 Qs)
# -------------------------------
def batch_questions(questions, batch_size=10):
    for i in range(0, len(questions), batch_size):
        yield questions[i:i + batch_size]



def solve_exam(exam, questions, batch_size=10):
    """
    exam: str
    questions: list[str]
    """
    final_answers = []

    for batch_no, batch in enumerate(
        batch_questions(questions, batch_size), start=1
    ):
        print(f"\n🧠 Solving batch {batch_no} ({len(batch)} questions)")

        batch_text = "\n".join(batch)
        batch_answer = solve_questions(exam, batch_text)

        final_answers.append(batch_answer)

        time.sleep(1)  # RPM-safe

    return "\n".join(final_answers)


