import faiss
import pickle
import numpy as np
import os

# Lazy-loaded sentence transformer model
_model = None

def get_model():
    """Get or create sentence transformer model (lazy initialization)."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        # Use a lightweight but effective model
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

# Configuration
FAISS_BASE_PATH = "faiss_store"
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 output dimension


def get_user_paths(user_id: int) -> tuple[str, str]:
    """
    Get FAISS index and chunks paths for a specific user.
    """
    user_dir = os.path.join(FAISS_BASE_PATH, f"user_{user_id}")
    os.makedirs(user_dir, exist_ok=True)
    index_path = os.path.join(user_dir, "store.index")
    chunks_path = os.path.join(user_dir, "chunks.pkl")
    return index_path, chunks_path


def chunk_text(text: str, source_name: str, chunk_size: int = 600, overlap: int = 100) -> list[dict]:
    """
    Split text into overlapping chunks.
    """
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i+chunk_size])
        if chunk.strip():
            chunks.append({
                "text": chunk,
                "source": source_name
            })
        i += chunk_size - overlap
    return chunks


def get_embedding(text: str) -> np.ndarray:
    """
    Get embedding vector for text using sentence-transformers.
    """
    model = get_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return np.array(embedding, dtype="float32")


def build_index(all_chunks: list[dict], user_id: int) -> tuple:
    """
    Build FAISS index from chunks for a specific user.
    """
    index_path, chunks_path = get_user_paths(user_id)
    
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    
    dim = EMBEDDING_DIM
    index = faiss.IndexFlatIP(dim)
    vectors = []
    
    print(f"Building index with {len(all_chunks)} chunks...")
    
    for chunk in all_chunks:
        emb = get_embedding(chunk["text"])
        # Already normalized by sentence-transformers
        vectors.append(emb)
    
    matrix = np.stack(vectors)
    index.add(matrix)
    
    faiss.write_index(index, index_path)
    with open(chunks_path, "wb") as f:
        pickle.dump(all_chunks, f)
    
    return index, all_chunks


def load_index(user_id: int) -> tuple:
    """
    Load FAISS index and chunks for a specific user.
    """
    index_path, chunks_path = get_user_paths(user_id)
    
    if not os.path.exists(index_path) or not os.path.exists(chunks_path):
        raise FileNotFoundError(f"No index found for user {user_id}. Please build the knowledge base first.")
    
    index = faiss.read_index(index_path)
    with open(chunks_path, "rb") as f:
        chunks = pickle.load(f)
    
    return index, chunks


def index_exists(user_id: int) -> bool:
    """
    Check if FAISS index exists for a user.
    """
    index_path, chunks_path = get_user_paths(user_id)
    return os.path.exists(index_path) and os.path.exists(chunks_path)


def retrieve(question: str, index, chunks, top_k: int = 3, threshold: float = 0.35) -> list[dict]:
    """
    Retrieve relevant chunks from the index for a given question.
    """
    emb = get_embedding(question)
    emb = emb.reshape(1, -1)
    
    scores, indices = index.search(emb, top_k)
    
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if score >= threshold and idx < len(chunks):
            results.append({
                "text": chunks[idx]["text"],
                "source": chunks[idx]["source"],
                "score": float(score)
            })
    
    return results


def delete_user_index(user_id: int) -> bool:
    """
    Delete FAISS index and chunks for a specific user.
    """
    index_path, chunks_path = get_user_paths(user_id)
    
    deleted = False
    if os.path.exists(index_path):
        os.remove(index_path)
        deleted = True
    if os.path.exists(chunks_path):
        os.remove(chunks_path)
        deleted = True
    
    return deleted
