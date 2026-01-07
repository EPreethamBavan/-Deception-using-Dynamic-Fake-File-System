from pypdf import PdfReader

reader = PdfReader("Research Proposal_ Deception using Dynamic Fake File System.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text() + "\n"

with open("extracted_text.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("Extraction complete.")
