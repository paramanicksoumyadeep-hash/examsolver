from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from google.api_core.exceptions import ResourceExhausted
import time

API_KEY = "AIzaSyDgyfY0nWwCaUKmFVwtSbA2UPdRxwBV9tI"

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
Solve {exam} questions.

STRICT OUTPUT RULES (MANDATORY):

1. MCQ (single correct):
   - Output ONLY the option letter: A, B, C, or D
   - NEVER output the option value (e.g. 30, 36, 2097152)
   - If the correct answer does NOT exactly match any option,
     LEAVE THE ANSWER BLANK

2. MSQ (multiple correct):
   - Output option letters only
   - Format: A, C (comma + space)
   - Sort alphabetically
   - If unsure or partial → LEAVE BLANK

3. NAT / Integer / Decimal:
   - Output ONLY the numeric value
   - No units, no text

4. Negative marking applies:
   - If unsure, DO NOT GUESS
   - Blank answer is safer than wrong

5. Output format is FIXED:
   - One answer per line
   - Question number followed by colon

EXAMPLES:
Q1: A
Q2: A, C
Q3: 12
Q4:
Q5: 0.25

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
def batch_questions(questions, batch_size=25):
    for i in range(0, len(questions), batch_size):
        yield questions[i:i + batch_size]



def solve_exam(exam, questions, batch_size=25):
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


