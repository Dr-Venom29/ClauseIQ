from app.core.config import settings
from app.vector_store.faiss import FAISSVectorStore
from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings

class EmbeddingService:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-2",
            google_api_key=settings.GEMINI_API_KEY
        )
        self.vector_store = FAISSVectorStore()

    async def embed_single(self, text: str) -> List[float]:
        return await self.embeddings.aembed_query(text)

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return await self.embeddings.aembed_documents(texts)
