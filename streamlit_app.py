import os
import streamlit as st
from PyPDF2 import PdfReader
import streamlit as st
import pymongo
import glob
import pandas as pd 
import gridfs
from bson import ObjectId


@st.cache_resource
def init_connection():
    connection_string = st.secrets["mongo"]["connection_string"]
    return pymongo.MongoClient(connection_string)

client = init_connection()
db = client.rs

# Inicjalizacja GridFS
fs = gridfs.GridFS(db)

@st.cache_data(ttl=600)
def get_raports():
    raports = db['raports']   
    return pd.DataFrame(list(raports.find({})))

def get_text_files(directory):
    return glob.glob(os.path.join(directory, '*.txt'))

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def document_exists(file_name, collection):
    return collection.find_one({"name": file_name}) is not None

def insert_to_mongodb(file_path, content, db, collection_name):

    collection = db[collection_name]
    file_name = os.path.basename(file_path)    
    # Sprawdzenie, czy dokument już istnieje
    if document_exists(file_name, collection):
        print(f"Dokument {file_name} już istnieje w kolekcji.")
        return
    
    document = {
            "_id": ObjectId(),
        "name": file_name,
        "body": content
    }
    collection.insert_one(document)
    print(f"Dokument {file_name} został dodany do kolekcji.")

file_path = 'txt_catalog/'
# Nazwa kolekcji, do której chcesz dodać metadane pliku
collection_name = 'raports'

# Dodaj plik tekstowy do kolekcji
text_files = get_text_files(file_path)

for file_path in text_files:
    content = read_file(file_path)  
    insert_to_mongodb(file_path, content, db, collection_name)




def extract_date_from_filename(filename):
    try:
        # Wyodrębnienie części z datą
        date_str = filename.split(' ')[2].split('.')[0:3]
        print(date_str)
        date_str = '.'.join(date_str)
        return datetime.strptime(date_str, '%d.%m.%y')
    except (IndexError, ValueError):
        return None


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
        words = file.read().lower().split()
    
    results = []
    search_word = search_word.lower()
    word_count = len(words)
    
    for i, word in enumerate(words):
        if search_word == word:
            start = max(0, i - context_words)
            end = min(word_count, i + context_words + 1)
            context = ' '.join(words[start:end])
            results.append(context)
    
    return results

def highlight_word(context, search_word):
    search_word_lower = search_word.lower()
    highlighted = context.replace(search_word_lower, f'<span style="color:red">{search_word_lower}</span>')
    return highlighted

# Konfiguracja Streamlit
st.title("Przeszukiwanie raportów")

# Ustawienie katalogu wyjściowego
txt_folder = 'txt_catalog'
if not os.path.exists(txt_folder):
    os.makedirs(txt_folder)

# Pasek boczny z listą plików tekstowych

txt_files = get_txt_files(txt_folder)
filt_txt_files = []
for t in txt_files:
    if  None != extract_date_from_filename(t):
        filt_txt_files.append(t)

txt_files = sorted(filt_txt_files, key=extract_date_from_filename)
txt_files = txt_files[::-1]

# Wczytaj plik PDF
uploaded_pdf = st.file_uploader("Wybierz plik PDF", type="pdf",accept_multiple_files=True)

if uploaded_pdf is not None:
    # Przetwórz PDF i zapisz jako plik tekstowy
    txt_path = save_text_from_pdf(uploaded_pdf, txt_folder)
    
    st.success(f"Plik został przetworzony i zapisany jako: {txt_path}")

# Opcje wyszukiwania
st.sidebar.title("Wyszukiwanie w plikach tekstowych")
search_word = st.sidebar.text_input("Wpisz słowo do wyszukania")
context_words = st.sidebar.slider("Liczba słów w otoczeniu", 1, 40, 16)

if st.sidebar.button("Szukaj"):
    if search_word:
        all_results = {}
        for txt_file in txt_files:
            file_path = os.path.join(txt_folder, txt_file)
            results = search_word_in_file(file_path, search_word, context_words)
            if results:
                all_results[txt_file] = results
        
        st.title("Wyniki wyszukiwania")
        if all_results:
            all_results = dict(sorted(all_results.items(), key=lambda item: extract_date_from_filename(item[0]),reverse=True))
            for txt_file, contexts in all_results.items():
                st.write(f"**Plik: {txt_file}**")
                for context in contexts:
                    highlighted_context = highlight_word(context, search_word)
                    st.markdown(f"... {highlighted_context} ...", unsafe_allow_html=True)
        else:
            st.write("Nie znaleziono wyników.")
    else:
        st.write("Proszę wpisać słowo do wyszukania.")
st.sidebar.title("Lista plików tekstowych")
# Sortowanie przefiltrowanej listy plików według daty wyodrębnionej z nazw 
# Funkcja do wyodrębnienia daty z nazwy pliku


# Sortowanie przefiltrowanej listy plików według daty wyodrębnionej z nazw plików

with st.sidebar:

    for t in txt_files:
        st.text(t)  
