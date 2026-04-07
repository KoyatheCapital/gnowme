from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.vector_stores.postgres import PGVectorStore
from sqlalchemy import make_url
from config import Config

# Try Mistral embeddings, fall back to a lightweight stub for local dev
try:
    from llama_index.embeddings.mistralai import MistralAIEmbedding
    from mistralai.client import Mistral as _M  # verify import works
    Settings.embed_model = MistralAIEmbedding(
        model_name="mistral-embed",
        api_key=Config.MISTRAL_API_KEY,
    )
    EMBED_DIM = 1024
except Exception:
    # Local dev fallback — embeddings will use a simple mock
    from llama_index.core.embeddings import BaseEmbedding
    from typing import List

    class _StubEmbed(BaseEmbedding):
        def _get_query_embedding(self, query: str) -> List[float]:
            return [0.0] * 384
        def _get_text_embedding(self, text: str) -> List[float]:
            return [0.0] * 384
        async def _aget_query_embedding(self, query: str) -> List[float]:
            return [0.0] * 384
        async def _aget_text_embedding(self, text: str) -> List[float]:
            return [0.0] * 384

    Settings.embed_model = _StubEmbed()
    EMBED_DIM = 384


class UserRAG:
    def __init__(self, user_id: str):
        url = make_url(Config.DATABASE_URL)
        self.vector_store = PGVectorStore.from_params(
            database=url.database or "gnowme_db",
            host=url.host,
            password=url.password,
            port=url.port or 5432,
            user=url.username or "postgres",
            table_name=f"gnowme_user_{user_id}_knowledge",
            embed_dim=EMBED_DIM,
        )
        self.index = VectorStoreIndex.from_vector_store(self.vector_store)

    def add_book(self, folder_path: str):
        """Add book content (PDF, txt, or folder of files)"""
        documents = SimpleDirectoryReader(folder_path).load_data()
        self.index.insert_nodes(documents)

    def query(self, query_str: str, top_k: int = 3):
        """Query the user's personal book consciousness store"""
        engine = self.index.as_query_engine(similarity_top_k=top_k)
        response = engine.query(query_str)
        return response.response if hasattr(response, "response") else str(response)
