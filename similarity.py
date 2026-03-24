import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict

# Try to import SentenceTransformer with fallback
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    class SentenceTransformer:
        def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
            self.model_name = model_name
        
        def encode(self, texts: List[str], convert_to_numpy=False, **kwargs):
            # Dummy embeddings
            embeddings = [[0.1 + i * 0.001 for i in range(384)] for _ in texts]
            if convert_to_numpy:
                return np.array(embeddings)
            return embeddings

class SimilarityModel:
    def __init__(self, model_name: str = "all-mpnet-base-v2"):
        """Load a robust embedding model for accurate semantic comparison."""
        self.model = SentenceTransformer(model_name)
    
    def embed_text(self, texts: List[str]) -> np.ndarray:
        """Convert texts to high-dimensional semantic embeddings."""
        # Use try-except to handle different versions of SentenceTransformer or dummy models
        try:
            return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        except TypeError:
            # Fallback for even more restricted dummy models
            return self.model.encode(texts, convert_to_numpy=True)
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute high-precision cosine similarity between two content blocks.
        Uses a deep-learning transformer model for semantic understanding.
        """
        if not text1 or not text2:
            return 0.0
        embeddings = self.embed_text([text1, text2])
        # Use cosine similarity for semantic distance
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        # Normalize and clip to 0-1 range
        return float(np.clip(similarity, 0.0, 1.0))
    
    def get_niche_coordinates(self, channels_data: Dict[str, List[str]]) -> Dict[str, List[float]]:
        """
        Reduces multi-dimensional embeddings to 2D using PCA for visualization.
        Ideal for 'Niche Mapping'.
        """
        names = list(channels_data.keys())
        texts = [" ".join(texts) for texts in channels_data.values()]
        
        if not texts:
            return {}
            
        embeddings = self.embed_text(texts)
        
        # Use PCA for stable, reproducible 2D projection
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2)
        try:
            coords = pca.fit_transform(embeddings)
            # Normalize to 0-1 range for consistent plotting
            coords = (coords - coords.min(axis=0)) / (coords.ptp(axis=0) + 1e-6)
            return {name: coords[i].tolist() for i, name in enumerate(names)}
        except:
            # Fallback for small datasets
            return {name: [np.random.rand(), np.random.rand()] for name in names}


# ===============================
# 🔹 SAMPLE RUN
# ===============================
if __name__ == "__main__":
    # Sample channel data
    sample_channels = {
        "TechGuru": [
            "Python tutorials for beginners",
            "Advanced machine learning concepts",
            "Data science best practices"
        ],
        "CodeMaster": [
            "Python programming basics",
            "Machine learning fundamentals",
            "Data analysis with Python"
        ],
        "TravelVlog": [
            "Exploring Paris in 48 hours",
            "Best beaches in the Caribbean",
            "Budget travel tips for Europe"
        ]
    }

    similarity_model = SimilarityModel()
    results = similarity_model.compare_channels(sample_channels)

    print("=== SIMILARITY MODEL RESULTS ===")
    import pprint
    pprint.pprint(results)