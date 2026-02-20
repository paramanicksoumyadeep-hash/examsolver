import streamlit as st
import pytesseract

from ocr.pdf_to_text import extract_text_from_pdf
from llm.solver import solve_exam
from pdf_utils.generate_pdf import create_answer_pdf

st.set_page_config(page_title="Exam Solver", layout="centered")

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

st.markdown("""
<style>
.main {
    background-color: #f7f9fc;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
.big-button button {
    width: 100%;
    height: 60px;
    font-size: 20px;
    font-weight: 600;
    border-radius: 12px;
    background-color: #2563eb;
    color: white;
    transition: 0.3s ease;
}
.big-button button:hover {
    background-color: #1e40af;
    transform: scale(1.03);
}
.card {
    padding: 2rem;
    border-radius: 16px;
    background-color: white;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.08);
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>📘 Exam Solver</h1>", unsafe_allow_html=True)

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

st.markdown("<div class='card'>", unsafe_allow_html=True)

exam = st.text_input("Enter Exam Name (GATE / JEE / NEET / Custom)")
question_pdf = st.file_uploader("Upload Question Paper PDF", type="pdf")

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    solve_clicked = st.button("🚀 Solve Exam", key="solve", help="Start solving exam")

if solve_clicked:

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
        st.session_state.generated_pdf = f.read()

    st.success("✅ Answer PDF Generated!")

if st.session_state.generated_pdf:

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.download_button(
            label="📄 Download Answer PDF",
            data=st.session_state.generated_pdf,
            file_name="answers.pdf",
            mime="application/pdf"
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📄 Preview")

    try:
        st.pdf(st.session_state.generated_pdf)
    except:
        st.info("Preview not supported in this browser. Please download the PDF.")
