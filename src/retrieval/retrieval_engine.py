import math
from collections import defaultdict


class RetrievalEngine:
    def __init__(self, inverted_index, mu=2000):
        self.inverted_index = inverted_index
        self.mu = mu

    def _collection_prob(self, term):
        cf = self.inverted_index.get_collection_freq(term)
        collection_len = self.inverted_index.get_collection_len()
        if collection_len == 0:
            return 0.0
        # Jika term tidak ada di koleksi, berikan probabilitas minimum
        if cf == 0:
            return 1.0 / collection_len
        return cf / collection_len

    def search(self, query_terms, top_k=10):
        """Hitung skor Query Likelihood dengan smoothing Dirichlet."""
        scores = defaultdict(float)
        hits = defaultdict(int)

        doc_ids = list(self.inverted_index.documents.keys())
        doc_lens = {doc_id: self.inverted_index.get_doc_len(doc_id) for doc_id in doc_ids}

        for term, qtf in query_terms.items():
            p_collection = self._collection_prob(term)
            postings = {p['doc_id']: p['tf'] for p in self.inverted_index.get_postings(term)}

            for doc_id in doc_ids:
                tf = postings.get(doc_id, 0)
                doc_len = doc_lens.get(doc_id, 0)
                denom = doc_len + self.mu
                if denom == 0:
                    continue

                smoothed = (tf + self.mu * p_collection) / denom
                if smoothed > 0:
                    scores[doc_id] += qtf * math.log(smoothed)
                if tf > 0:
                    hits[doc_id] += qtf  # catat ada kecocokan term

        results = []
        for doc_id, score in scores.items():
            if hits[doc_id] == 0:
                continue  # sembunyikan dokumen tanpa kecocokan query
            results.append({
                'doc_id': doc_id,
                'score': score,
                'hits': hits[doc_id],
                'metadata': self.inverted_index.documents[doc_id],
            })

        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
