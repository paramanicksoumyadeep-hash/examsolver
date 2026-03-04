# 📄 Exam Solver & Evaluator App

An intelligent **exam paper solver and checker** built using OCR and Large Language Models.  
The app takes scanned or digital exam papers as input, extracts questions, solves them automatically, evaluates answers, and returns results in **PDF format**.

🚀 **Live App:** https://examsolver.streamlit.app/

---

## 🔍 Overview

This application automates the complete pipeline of solving and checking exam papers:

1. **PDF → Image conversion**
2. **Image → Text extraction (OCR)**
3. **Question understanding & solving using LLM**
4. **Answer compilation & PDF generation**
5. **Interactive web interface**

It is designed for academic, research, and demonstration purposes where automated exam evaluation is required.

---

## 🧠 Tech Stack

- **App Framework:** :streamlit
- **PDF Processing:** PyMuPDF  
- **OCR Engine:** Tesseract-OCR  
- **LLM for Solving:** :contentReference[oaicite:1]{index=1} (Gemini-2.5-Flash)  
- **Output:** PDF  
- **Deployment:** Streamlit Community Cloud  

---

## ⚙️ Workflow

### 1️⃣ PDF to Image
- Uploaded exam PDFs are converted into images using **PyMuPDF**.

### 2️⃣ Image to Text (OCR)
- Images are processed with **Tesseract-OCR** to extract readable text.
- Works with both scanned and digital exam papers.

### 3️⃣ Question Solving
- Extracted questions are passed to **Gemini-2.5-Flash**.
- The model understands the context and generates answers automatically.

### 4️⃣ PDF Generation
- Generated answers are compiled into a clean, structured **PDF answer sheet**.
- Users can download the final PDF directly from the app.

---

## ✨ Features

- 📤 Upload scanned or digital exam PDFs  
- 🔎 OCR-based text extraction  
- 🤖 AI-powered question solving  
- 📑 Auto-generated answer PDFs  
- 🌐 Fully web-based interface  

---

## 🖥️ Local Installation

```bash
# Clone the repository
git clone https://github.com/your-username/exam-solver.git
cd exam-solver

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
