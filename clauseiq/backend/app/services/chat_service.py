from app.services.search_service import SearchService
from app.core.exceptions import QuotaExceededException
from app.services.llm_router import get_llm_router, LLMRouter

class ChatService:
    def __init__(self, db, router: LLMRouter | None = None):
        self.db = db
        self.search_service = SearchService()
        self.router = router if router is not None else get_llm_router()

    async def chat(self, query: str, user_id: str, document_id: str = None, conversation_id: str = None) -> dict:
        # 1. Retrieve relevant chunks
        search_results = await self.search_service.search(query, user_id=user_id, document_id=document_id, top_k=5)
        
        context_text = ""
        citations = []
        for i, res in enumerate(search_results):
            context_text += f"[Citation {i+1}] Page {res.page_number}, Section {res.section}: {res.content}\n\n"
            citations.append({
                "document_name": res.document_name,
                "page_number": res.page_number,
                "section": res.section
            })

        prompt = f"""
        You are an expert legal assistant. Answer the user's query based ONLY on the provided document context.
        If the answer is not in the context, explicitly state that you cannot find it in the document.
        Always reference the citation numbers (e.g., [Citation 1]) when providing facts.

        CONTEXT:
        {context_text}

        USER QUERY:
        {query}
        """

        try:
            answer = await self.router.generate_text(prompt, task="rag_chat", user_id=user_id)
        except QuotaExceededException as e:
            answer = e.message

        return {
            "response": answer,
            "citations": citations
        }
