import docx
import PyPDF2
import nltk # Library nltk
import string # Library string
import re # Library regex
from nltk.tokenize import word_tokenize 


def read_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text