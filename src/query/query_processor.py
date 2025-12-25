from src.preprocessing.tokenizing import tokenizing
from src.preprocessing.stopword import remove_stopwords
from src.preprocessing.tala_stemmer import Stem_Tala_tokenizing
from src.utils.utils import bersihkan_text

class QueryProcessor:
    def __init__(self, tfidf_model):
        self.tfidf_model = tfidf_model

    def preprocess_query(self, query_text):
        """
        menjalankan step2 preprocessing
        1. Case folding / Cleaning
        2. Tokenizing
        3. Stopword removal
        4. Stemming
        """
        # 1. Cleaning
        clean_text = bersihkan_text(query_text)
        
        # 2. Tokenizing
        tokens = tokenizing(clean_text)
        
        # 3. Stopword removal
        tokens_no_stop = remove_stopwords(tokens)
        
        # 4. Stemming
        stemmed_tokens = Stem_Tala_tokenizing(tokens_no_stop)
        
        return stemmed_tokens

    def transform_query(self, query_text):
        """
        mengubah kueri menjadi vektor tf-idf
        """
        tokens = self.preprocess_query(query_text)
        
        vector = self.tfidf_model.transform(tokens)
        
        return vector, tokens
