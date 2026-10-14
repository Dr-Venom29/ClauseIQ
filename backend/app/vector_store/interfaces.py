from abc import ABC, abstractmethod

class IVectorStore(ABC):
    @abstractmethod
    def add_embeddings(self, embeddings: list, metadatas: list) -> None:
        pass

    @abstractmethod
    def search(self, query_embedding: list, k: int, user_id: str, document_id: str = None) -> list:
        pass

    @abstractmethod
    def delete_document_vectors(self, document_id: str) -> None:
        pass
