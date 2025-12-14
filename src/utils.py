import docx
import PyPDF2
import string
import re 

def baca_txt(path_file):
    with open(path_file, 'r', encoding='utf-8') as file:
        return file.read()
    
def baca_docx(path_file):
    doc = docx.Document(path_file)
    text = []
    for pars in doc.paragraphs:
        text.append(pars.text)
    return '\n'.join(text)

def baca_pdf(path_file):
    text = "" 
    with open(path_file, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def bersihkan_text(text):
    if not text:
        return ""
    text = str(text) 
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'[""''…—–-]', '', text)
    text = re.sub(r'\d+', '', text)
    text = ' '.join(text.split())
    return text 


