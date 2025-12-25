from collections import defaultdict
from src.retrieval.similarity import calculate_cosine_similarity

class RetrievalEngine:
    def __init__(self, inverted_index, tfidf_model):
        self.inverted_index = inverted_index
        self.tfidf_model = tfidf_model
    
    def search(self, query_vector, top_k=10):
        scores = defaultdict(float)
        doc_vectors = defaultdict(dict)
        
        query_terms = list(query_vector.keys())
        
        for term, query_weight in query_vector.items():
            postings = self.inverted_index.get_postings(term)
            
            for posting in postings:
                doc_id = posting['doc_id']
                doc_weight = posting['tfidf']
                
                doc_vectors[doc_id][term] = doc_weight

        results = []
        for doc_id, doc_vec in doc_vectors.items():
            
            doc_norm = self.inverted_index.documents[doc_id].get('norm', None)
            
            score = calculate_cosine_similarity(query_vector, doc_vec, norm2=doc_norm)
            if score > 0:
                results.append({
                    'doc_id': doc_id, 
                    'score': score,
                    'metadata': self.inverted_index.documents[doc_id]
                })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:top_k]
