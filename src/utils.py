import docx
import pyPDF2
import string
import re 

def baca_txt(path_file):
    with open(path_file, 'r', encoding='utf-8') as file:
        return file.read()
    
def baca_docx(path_file):
    doc = docx.document(path_file)
    text = []
    for pars in doc.paragraphs:
        text.append(pars.text)
    return '\n'.join(text)

def baca_pdf(path_file):
    text = "" 
    with open(path_file, 'rb') as file:
        reader = pyPDF2.pdfReader(file)
        for page in reader.page:
            text += page.extract_text() + "\n"
    return text

def clean_text(text):
    text = str(text) 
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'[""''…—–-]', '', text)
    text = re.sub(r'\d+', '', text)
    text = ' '.join(text.split())
    return text 


