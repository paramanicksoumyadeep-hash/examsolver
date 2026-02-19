import shutil
import streamlit as st
from ocr.pdf_to_text import extract_text_from_pdf
from llm.solver import solve_exam
from pdf_utils.generate_pdf import create_answer_pdf
from grading.evaluate import parse_answers_robust, smart_evaluate
import pytesseract

st.write("Tesseract path:", shutil.which("tesseract"))

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

st.set_page_config(page_title="AI Exam Solver & Evaluator", layout="centered")
st.title("📘 AI Exam Solver & Evaluator")

# ------------------ Session State ----------------
if "ai_answer_text" not in st.session_state:
    st.session_state.ai_answer_text = None

# ------------------ Helpers ----------------
def split_into_questions(raw_text: str):
    blocks = raw_text.split("\nQ")
    questions = []
    for i, block in enumerate(blocks):
        if block.strip():
            q = block if i == 0 else "Q" + block
            questions.append(q.strip())
    return questions

# ------------------ UI Inputs ----------------
exam = st.text_input("Enter Exam Name (GATE / JEE / NEET / Custom)")
question_pdf = st.file_uploader("Upload Question Paper PDF", type="pdf")

# ------------------ Solve Exam ----------------
if st.button("🚀 Solve Exam"):
    if question_pdf is None or not exam.strip():
        st.error("❌ Please upload PDF and enter exam name")
        st.stop()

    with open("temp_q.pdf", "wb") as f:
        f.write(question_pdf.read())

    with st.spinner("📄 Extracting questions..."):
        raw_text = extract_text_from_pdf("temp_q.pdf")
        question_list = split_into_questions(raw_text)

    if not question_list:
        st.error("❌ No questions detected")
        st.stop()

    st.info(f"📄 Detected {len(question_list)} questions")

    with st.spinner("🤖 Solving exam using AI..."):
        answers = solve_exam(exam=exam, questions=question_list, batch_size=25)

    create_answer_pdf(answers)
    st.session_state.ai_answer_text = extract_text_from_pdf("answers.pdf")

    st.success("✅ Answer PDF Generated!")
    with open("answers.pdf", "rb") as f:
        st.download_button("📄 Download AI Answers", f, "answers.pdf", "application/pdf")

# ------------------ Evaluation Section ----------------
st.header("📊 Evaluate Answers")
official_pdf = st.file_uploader("Upload Official Answer Key PDF", type="pdf")
st.subheader("📝 Evaluation Rules (MANDATORY)")
rules_text = st.text_area(
    "Enter marking & evaluation rules",
    height=220,
    placeholder="- MCQ: +1 for correct, -0.33 for incorrect\n- MSQ: +2 only if all correct, else 0\n- NAT: +2 exact match, no negative\n- Partial allowed if specified\n- Treat format mismatch as blank"
)

# ------------------ Evaluate ----------------
if st.button("🧮 Evaluate"):
    if official_pdf is None or st.session_state.ai_answer_text is None:
        st.error("❌ Upload official answer key and solve exam first")
        st.stop()

    if not rules_text.strip():
        st.error("❌ Evaluation rules required")
        st.stop()

    with open("temp_official.pdf", "wb") as f:
        f.write(official_pdf.read())

    with st.spinner("📄 Reading official answer key..."):
        off_text = extract_text_from_pdf("temp_official.pdf")

    ai_answers = parse_answers_robust(st.session_state.ai_answer_text)
    official_answers = parse_answers_robust(off_text)

    with st.spinner("🤖 Evaluating answers..."):
        result = smart_evaluate(ai_answers, official_answers, rules_text)

    st.success("✅ Evaluation Complete")

    col1, col2 = st.columns(2)
    col1.metric("Correct Questions", result["correct_count"])
    col2.metric("Incorrect Questions", result["incorrect_count"])
    st.metric("Final Score", f'{result["marks_obtained"]} / {result["total_marks"]}')
