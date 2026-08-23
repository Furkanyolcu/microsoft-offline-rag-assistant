from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_pdf(path, title, lines):
    c = canvas.Canvas(path, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, 750, title)
    c.setFont("Helvetica", 12)
    y = 720
    for line in lines:
        if y < 72:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 750
        c.drawString(72, y, line)
        y -= 20
    c.save()

# PDF 1
pdf1_lines = [
    "Global Maritime Law (Admiralty Law) is a body of laws that govern nautical issues and",
    "private maritime disputes.",
    "It consists of both domestic law on maritime activities, and private international law",
    "governing the relationships between private parties operating or using ocean-going ships.",
    "One of the key concepts is the 'General Average', which requires that if cargo is",
    "jettisoned in a voluntary sacrifice to save the ship, all parties to the sea venture",
    "must proportionally share the loss.",
    "Another important convention is the SOLAS (Safety of Life at Sea) convention,",
    "which ensures maritime safety."
]
create_pdf("data/sample_documents/maritime_law.pdf", "Global Maritime Law Overview", pdf1_lines)

# PDF 2
pdf2_lines = [
    "Artificial Intelligence in Healthcare is transforming the industry.",
    "The use of machine learning algorithms can help in diagnosing diseases,",
    "predicting patient outcomes, and personalizing treatment plans.",
    "For example, AI is heavily used in radiology to detect anomalies in X-rays",
    "and MRI scans faster than human doctors.",
    "Privacy and data security are major concerns, which is why local AI models",
    "are becoming more popular in hospitals to keep patient data secure.",
    "The integration of RAG (Retrieval-Augmented Generation) allows healthcare",
    "assistants to query massive medical databases safely."
]
create_pdf("data/sample_documents/ai_in_healthcare.pdf", "AI in Healthcare", pdf2_lines)

print("PDFs created successfully!")
