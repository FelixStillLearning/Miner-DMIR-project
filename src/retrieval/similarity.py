import math

def calculate_cosine_similarity(vec1, vec2, norm1=None, norm2=None):
    dot_product = 0.0
    for term, weight in vec1.items():
        if term in vec2:
            dot_product += weight * vec2[term]
    if norm1 is None:
        norm1 = math.sqrt(sum(w**2 for w in vec1.values()))
    
    if norm2 is None:
        norm2 = math.sqrt(sum(w**2 for w in vec2.values()))
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
        
    return dot_product / (norm1 * norm2)
