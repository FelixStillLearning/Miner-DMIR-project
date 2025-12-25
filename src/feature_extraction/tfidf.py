import math
from collections import defaultdict, Counter

class TFIDF:
    def __init__(self):
        self.idf_scores = {}
        self.corpus_size = 0

    def calculate_tf(self, tokens):
        tf_scores = {}
        total_tokens = len(tokens)
        if total_tokens == 0:
            return tf_scores
            
        token_counts = Counter(tokens)
        for token, count in token_counts.items():
            tf_scores[token] = count / total_tokens
            
        return tf_scores

    def calculate_idf(self, corpus_tokens):
        self.corpus_size = len(corpus_tokens)
        self.idf_scores = {}

        df_counts = defaultdict(int)
        for doc_tokens in corpus_tokens:
            unique_tokens = set(doc_tokens)
            for token in unique_tokens:
                df_counts[token] += 1
                
        for token, df in df_counts.items():
            self.idf_scores[token] = math.log10(self.corpus_size / df)
            
        return self.idf_scores

    def get_tfidf_weight(self, tf, token):
        idf = self.idf_scores.get(token, 0.0)
        return tf * idf

    def transform(self, tokens):
        tf_scores = self.calculate_tf(tokens)
        tfidf_scores = {}
        
        for token, tf in tf_scores.items():
            tfidf_scores[token] = self.get_tfidf_weight(tf, token)
            
        return tfidf_scores
