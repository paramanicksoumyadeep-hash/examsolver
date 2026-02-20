import streamlit as st
import shutil
import pytesseract
import base64

from ocr.pdf_to_text import extract_text_from_pdf
from llm.solver import solve_exam
from pdf_utils.generate_pdf import create_answer_pdf

st.set_page_config(page_title="Exam Solver", layout="centered")

st.write("Tesseract path:", shutil.which("tesseract"))
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

st.title("📘 Exam Solver")

if "generated_pdf" not in st.session_state:
    st.session_state.generated_pdf = None

def split_into_questions(raw_text: str):
    blocks = raw_text.split("\nQ")
    questions = []
    for i, block in enumerate(blocks):
        if block.strip():
            q = block if i == 0 else "Q" + block
            questions.append(q.strip())
    return questions

exam = st.text_input("Enter Exam Name (GATE / JEE / NEET / Custom)")
question_pdf = st.file_uploader("Upload Question Paper PDF", type="pdf")

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

    with st.spinner("🤖 Solving exam..."):
        answers = solve_exam(exam=exam, questions=question_list, batch_size=8)

    create_answer_pdf(answers)

    with open("answers.pdf", "rb") as f:
        pdf_bytes = f.read()

    st.session_state.generated_pdf = pdf_bytes
    st.success("✅ Answer PDF Generated!")

if st.session_state.generated_pdf:

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.download_button(
            label="📄 Download Answer PDF",
            data=st.session_state.generated_pdf,
            file_name="answers.pdf",
            mime="application/pdf"
        )

    st.markdown("---")

    base64_pdf = base64.b64encode(st.session_state.generated_pdf).decode("utf-8")

    pdf_display = f"""
    <iframe
        src="data:application/pdf;base64,{base64_pdf}"
        width="100%"
        height="700px"
        style="border:1px solid #ccc;">
    </iframe>
    """

    st.markdown(pdf_display, unsafe_allow_html=True)
