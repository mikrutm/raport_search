import os
import streamlit as st
from PyPDF2 import PdfReader

def save_text_from_pdf(pdf_file, txt_folder):
    pdf_reader = PdfReader(pdf_file)
    text_content = []
    
    for page in pdf_reader.pages:
        text_content.append(page.extract_text())
    
    pdf_filename = pdf_file.name
    txt_filename = f"{os.path.splitext(pdf_filename)[0]}.txt"
    txt_path = os.path.join(txt_folder, txt_filename)
    
    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write('\n'.join(text_content))
    
    return txt_path

def get_txt_files(txt_folder):
    return [f for f in os.listdir(txt_folder) if f.endswith('.txt')]

# Konfiguracja Streamlit
st.title("PDF to Text Transcriber")

# Ustawienie katalogu wyjściowego
txt_folder = 'txt_catalog'
if not os.path.exists(txt_folder):
    os.makedirs(txt_folder)

# Pasek boczny z listą plików tekstowych
st.sidebar.title("Lista plików tekstowych")
txt_files = get_txt_files(txt_folder)

selected_txt_file = st.sidebar.selectbox("Wybierz plik tekstowy", txt_files)

if selected_txt_file:
    txt_path = os.path.join(txt_folder, selected_txt_file)
    st.sidebar.write(f"Wybrano plik: {selected_txt_file}")
    
    with open(txt_path, 'r', encoding='utf-8') as file:
        file_content = file.read()
        st.text_area("Zawartość pliku", file_content, height=400)

# Wczytaj plik PDF
uploaded_pdf = st.file_uploader("Wybierz plik PDF", type="pdf")

if uploaded_pdf is not None:
    # Przetwórz PDF i zapisz jako plik tekstowy
    txt_path = save_text_from_pdf(uploaded_pdf, txt_folder)
    
    st.success(f"Plik został przetworzony i zapisany jako: {txt_path}")

    # Wyświetl zawartość przetranskrybowanego tekstu
    with open(txt_path, 'r', encoding='utf-8') as file:
        st.text_area("Zawartość przetranskrybowanego pliku", file.read(), height=400)
