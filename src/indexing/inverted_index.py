import pickle
import os
from collections import Counter


class InvertedIndex:
    def __init__(self):
        self.index = {}
        self.documents = {}
        self.collection_len = 0

    def build_index(self, processed_documents):
        """Bangun inverted index dengan menyimpan tf dan panjang dokumen."""
        self.index = {}
        self.documents = {}
        self.collection_len = 0

        for doc in processed_documents:
            doc_id = doc['id']
            tokens = doc['tokens']
            doc_len = len(tokens)
            self.collection_len += doc_len

            # simpan metadata + panjang dokumen
            self.documents[doc_id] = {
                **doc['metadata'],
                'doc_len': doc_len,
            }

            term_counts = Counter(tokens)

            for term, tf in term_counts.items():
                if term not in self.index:
                    self.index[term] = {
                        'cf': 0,
                        'postings': [],
                    }

                self.index[term]['cf'] += tf
                self.index[term]['postings'].append({
                    'doc_id': doc_id,
                    'tf': tf,
                })

        return self.index

    def save(self, filepath):
        """Save index and metadata to disk using pickle"""
        data = {
            'index': self.index,
            'documents': self.documents,
            'collection_len': self.collection_len,
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
            self.index = data.get('index', {})
            self.documents = data.get('documents', {})
            self.collection_len = data.get('collection_len', 0)
        return True

    def get_postings(self, term):
        """Ambil daftar posting untuk suatu term."""
        if term in self.index:
            return self.index[term]['postings']
        return []

    def get_collection_freq(self, term):
        """Frekuensi term di seluruh koleksi."""
        if term in self.index:
            return self.index[term]['cf']
        return 0

    def get_doc_len(self, doc_id):
        """Panjang dokumen (jumlah token)."""
        return self.documents.get(doc_id, {}).get('doc_len', 0)

    def get_collection_len(self):
        """Total token dalam koleksi."""
        return self.collection_len
