import os
from PyPDF2 import PdfReader

def pdf_to_text(pdf_path, txt_path):
    pdf_reader = PdfReader(pdf_path)
    text_content = []
    
    for page in pdf_reader.pages:
        text_content.append(page.extract_text())
    
    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write('\n'.join(text_content))

def process_pdfs(pdf_folder, txt_folder):
    if not os.path.exists(txt_folder):
        os.makedirs(txt_folder)
    
    for filename in os.listdir(pdf_folder):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(pdf_folder, filename)
            txt_filename = f"{os.path.splitext(filename)[0]}.txt"
            txt_path = os.path.join(txt_folder, txt_filename)
            pdf_to_text(pdf_path, txt_path)
            print(f"Przetworzono plik: {filename}")

# Przykładowe użycie
pdf_folder = 'pdf_catalog'
txt_folder = 'txt_catalog'

process_pdfs(pdf_folder, txt_folder)

