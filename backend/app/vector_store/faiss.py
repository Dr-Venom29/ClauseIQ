import faiss
import numpy as np
import pickle
from app.vector_store.interfaces import IVectorStore

class FAISSVectorStore(IVectorStore):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FAISSVectorStore, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, index_path="faiss_index.bin", metadata_path="faiss_metadata.pkl"):
        if getattr(self, "_initialized", False):
            return
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.index = None
        self.metadata = []
        self.load()
        self._initialized = True

    def add_embeddings(self, embeddings, metadatas: list):
        print("FAISS add_embeddings called")
        print("Embeddings count:", len(embeddings))
        embeddings_np = np.array(embeddings, dtype=np.float32)
        if self.index is None:
            d = embeddings_np.shape[1]
            self.index = faiss.IndexFlatL2(d)
        
        self.index.add(embeddings_np)
        self.metadata.extend(metadatas)
        self.save()
        print("FAISS saved")

    def search(self, query_embedding, k: int, user_id: str, document_id: str = None):
        print("FAISS total vectors:", self.index.ntotal if self.index else 0)
        if self.index is None or self.index.ntotal == 0:
            return []
            
        query_np = np.array([query_embedding], dtype=np.float32)
        # Search over the entire index to filter by user_id post-search safely
        search_k = self.index.ntotal
        D, I = self.index.search(query_np, search_k)
        results = []
        for i in range(len(I[0])):
            if I[0][i] != -1:
                meta = self.metadata[I[0][i]]
                if str(meta.get("user_id")) != str(user_id):
                    continue
                if document_id and str(meta.get("document_id")) != str(document_id):
                    continue
                results.append({
                    "score": float(D[0][i]),
                    "metadata": meta,
                    "content": meta.get("content", "")
                })
                if len(results) == k:
                    break
        return results

    def save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)

    def load(self):
        try:
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, "rb") as f:
                self.metadata = pickle.load(f)
        except (FileNotFoundError, RuntimeError):
            self.index = None
            self.metadata = []

    def delete_document_vectors(self, document_id: str) -> None:
        if self.index is None or self.index.ntotal == 0:
            return
            
        remaining_vectors = []
        remaining_metadata = []
        d = self.index.d
        
        for i in range(self.index.ntotal):
            meta = self.metadata[i]
            if str(meta.get("document_id")) == str(document_id):
                continue
                
            # Reconstruct the vector
            vec = self.index.reconstruct(i)
            remaining_vectors.append(vec)
            remaining_metadata.append(meta)
            
        if len(remaining_vectors) > 0:
            new_index = faiss.IndexFlatL2(d)
            new_index.add(np.array(remaining_vectors, dtype=np.float32))
            self.index = new_index
            self.metadata = remaining_metadata
        else:
            self.index = None
            self.metadata = []
            
        self.save()
