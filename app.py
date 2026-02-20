import streamlit as st
import pytesseract
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

from ocr.pdf_to_text import extract_text_from_pdf
from llm.solver import solve_exam

st.set_page_config(page_title="Exam Solver", layout="centered")

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

h1 {
    text-align: center;
    font-weight: 700;
}

.center-button {
    display: flex;
    justify-content: center;
    margin-top: 40px;
    margin-bottom: 20px;
}

.center-button div.stButton > button {
    width: 480px;
    height: 75px;
    font-size: 22px;
    font-weight: 600;
    border-radius: 18px;
    background: linear-gradient(90deg, #2563eb, #1e40af);
    color: white;
    border: none;
    transition: all 0.3s ease;
}

.center-button div.stButton > button:hover {
    transform: scale(1.06);
    background: linear-gradient(90deg, #1e40af, #1e3a8a);
}

.download-center {
    display: flex;
    justify-content: center;
    margin-top: 30px;
}
</style>
""", unsafe_allow_html=True)

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

def create_answer_pdf(answer_text, filename="answers.pdf"):

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    safe_style = ParagraphStyle(
        'SafeStyle',
        parent=styles['Normal'],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        wordWrap='CJK',
        spaceAfter=6,
    )

    elements = []

    for line in answer_text.split("\n"):

        if line.strip() == "":
            elements.append(Spacer(1, 0.15 * inch))
            continue

        safe_line = line.replace("&", "&amp;") \
                        .replace("<", "&lt;") \
                        .replace(">", "&gt;")

        elements.append(Paragraph(safe_line, safe_style))

    doc.build(elements)

exam = st.text_input("Enter Exam Name (GATE / JEE / NEET / Custom)")
question_pdf = st.file_uploader("Upload Question Paper PDF", type="pdf")

st.markdown("<div class='center-button'>", unsafe_allow_html=True)
solve_clicked = st.button("🚀 Solve Exam")
st.markdown("</div>", unsafe_allow_html=True)

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

    st.markdown("<div class='download-center'>", unsafe_allow_html=True)

    st.download_button(
        label="📄 Download Answer PDF",
        data=st.session_state.generated_pdf,
        file_name="answers.pdf",
        mime="application/pdf"
    )

    st.markdown("</div>", unsafe_allow_html=True)
