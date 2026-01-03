from collections import Counter
from src.utils.utils import tokenizing
from src.preprocessing.stopword import remove_stopwords
from src.preprocessing.tala_stemmer import Stem_Tala_tokenizing
from src.utils.utils import bersihkan_text


class QueryProcessor:
    def preprocess_query(self, query_text):
        """
        menjalankan step2 preprocessing
        1. Case folding / Cleaning
        2. Tokenizing
        3. Stopword removal
        4. Stemming
        """
        clean_text = bersihkan_text(query_text)
        tokens = tokenizing(clean_text)
        tokens_no_stop = remove_stopwords(tokens)
        stemmed_tokens = Stem_Tala_tokenizing(tokens_no_stop)
        return stemmed_tokens

    def transform_query(self, query_text):
        """
        Mengubah kueri menjadi frekuensi term untuk LM ]
        """
        tokens = self.preprocess_query(query_text)
        term_freq = Counter(tokens)
        return term_freq, tokens
