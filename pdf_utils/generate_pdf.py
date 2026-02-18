from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def create_answer_pdf(text, output="answers.pdf"):
    c = canvas.Canvas(output, pagesize=A4)
    width, height = A4

    y = height - 40
    for line in text.split("\n"):
        c.drawString(40, y, line)
        y -= 15
        if y < 40:
            c.showPage()
            y = height - 40

    c.save()
