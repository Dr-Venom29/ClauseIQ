from app.services.embedding_service import EmbeddingService
from app.schemas.search import SearchResultItem
from typing import List

class SearchService:
    def __init__(self):
        self.embedding_service = EmbeddingService()

    async def search(self, query: str, user_id: str, document_id: str = None, top_k: int = 5) -> List[SearchResultItem]:
        print("================================")
        print("QUERY:", query)
        print("DOCUMENT ID:", document_id)
        
        # 1. FAISS Semantic Search
        query_embedding = await self.embedding_service.embed_single(query)
        semantic_results = self.embedding_service.vector_store.search(
            query_embedding=query_embedding, 
            k=top_k * 2,
            user_id=user_id,
            document_id=document_id
        )

        query_tokens = set(query.lower().split())
        if not query_tokens:
            semantic_results = semantic_results[:top_k]
        else:
            # 2. Reranking (0.7 Semantic + 0.3 Keyword)
            reranked = []
            for res in semantic_results:
                content = res.get('content', '')
                chunk_tokens = set(content.lower().split())
                keyword_score = len(query_tokens & chunk_tokens) / len(query_tokens) if query_tokens else 0
                
                dist = res.get('score', 0)
                semantic_score = max(0, 1 - (dist / 2.0))
                
                final_score = (0.7 * semantic_score) + (0.3 * keyword_score)
                
                metadata = res.get('metadata', {})
                reranked.append({
                    "final_score": final_score,
                    "metadata": metadata,
                    "content": content
                })

            reranked.sort(key=lambda x: x["final_score"], reverse=True)
            semantic_results = reranked[:top_k]
        
        search_results = []
        for result in semantic_results:
            metadata = result['metadata']
            search_results.append(
                SearchResultItem(
                    document_name=metadata.get('document_name', ''),
                    page_number=metadata.get('page', 0),
                    section=metadata.get('section'),
                    content=result['content'],
                    score=result.get('final_score', result.get('score', 0))
                )
            )
        return search_results
