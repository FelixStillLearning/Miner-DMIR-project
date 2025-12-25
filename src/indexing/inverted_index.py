import json
import pickle
import os

class InvertedIndex:
    def __init__(self):
        self.index = {}
        self.documents = {}

    def build_index(self, processed_documents, tfidf_model):
        """
        Build inverted index from processed documents.
        processed_documents: list of dict {'id': int, 'tokens': [list], 'metadata': dict}
        tfidf_model: trained TFIDF instance
        """
        self.index = {}
        self.documents = {}
        

        for doc in processed_documents:
            self.documents[doc['id']] = doc['metadata']
            
            doc_tfidf = tfidf_model.transform(doc['tokens'])
            doc_tf = tfidf_model.calculate_tf(doc['tokens'])
            
            import math
            doc_norm = math.sqrt(sum(w**2 for w in doc_tfidf.values()))
            self.documents[doc['id']]['norm'] = doc_norm
            
            for term, score in doc_tfidf.items():
                if term not in self.index:
                    self.index[term] = {
                        'idf': tfidf_model.idf_scores.get(term, 0.0),
                        'postings': []
                    }
                
                self.index[term]['postings'].append({
                    'doc_id': doc['id'],
                    'tf': doc_tf.get(term, 0.0),
                    'tfidf': score
                })
        
        return self.index

    def save(self, filepath):
        """Save index and metadata to disk using pickle"""
        data = {
            'index': self.index,
            'documents': self.documents
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
            
    def load(self, filepath):
        """Load index and metadata from disk"""
        if not os.path.exists(filepath):
            return False
            
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.index = data['index']
            self.documents = data['documents']
        return True

    def get_postings(self, term):
        """Get posting list for a term"""
        if term in self.index:
            return self.index[term]['postings']
        return []
        
    def get_idf(self, term):
        """Get IDF score for a term"""
        if term in self.index:
            return self.index[term]['idf']
        return 0.0
