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

def search_word_in_file(file_path, search_word, context_words=3):
    with open(file_path, 'r', encoding='utf-8') as file:
        words = file.read().split()
    
    results = []
    search_word = search_word.lower()
    word_count = len(words)
    
    for i, word in enumerate(words):
        if search_word in word.lower():
            start = max(0, i - context_words)
            end = min(word_count, i + context_words + 1)
            context = ' '.join(words[start:end])
            results.append(context)
    
    return results

# Konfiguracja Streamlit
st.title("PDF to Text Transcriber and Search")

# Ustawienie katalogu wyjściowego
txt_folder = 'txt_catalog'
if not os.path.exists(txt_folder):
    os.makedirs(txt_folder)

# Pasek boczny z listą plików tekstowych
st.sidebar.title("Lista plików tekstowych")
txt_files = get_txt_files(txt_folder)

# Wczytaj plik PDF
uploaded_pdf = st.file_uploader("Wybierz plik PDF", type="pdf")

if uploaded_pdf is not None:
    # Przetwórz PDF i zapisz jako plik tekstowy
    txt_path = save_text_from_pdf(uploaded_pdf, txt_folder)
    
    st.success(f"Plik został przetworzony i zapisany jako: {txt_path}")

# Opcje wyszukiwania
st.sidebar.title("Wyszukiwanie w plikach tekstowych")
search_word = st.sidebar.text_input("Wpisz słowo do wyszukania")
context_words = st.sidebar.slider("Liczba słów w otoczeniu", 1, 10, 3)

if st.sidebar.button("Szukaj"):
    if search_word:
        all_results = {}
        for txt_file in txt_files:
            file_path = os.path.join(txt_folder, txt_file)
            results = search_word_in_file(file_path, search_word, context_words)
            if results:
                all_results[txt_file] = results
        
        st.sidebar.title("Wyniki wyszukiwania")
        if all_results:
            for txt_file, contexts in all_results.items():
                st.sidebar.write(f"Plik: {txt_file}")
                for context in contexts:
                    st.sidebar.write(f"... {context} ...")
        else:
            st.sidebar.write("Nie znaleziono wyników.")
    else:
        st.sidebar.write("Proszę wpisać słowo do wyszukania.")
