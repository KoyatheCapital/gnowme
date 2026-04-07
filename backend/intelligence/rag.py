from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.mistralai import MistralAIEmbedding
from llama_index.vector_stores.postgres import PGVectorStore
from sqlalchemy import make_url
from config import Config

# Use Mistral embeddings — no OpenAI key required
Settings.embed_model = MistralAIEmbedding(
    model_name="mistral-embed",
    api_key=Config.MISTRAL_API_KEY,
)

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
            embed_dim=1024,  # mistral-embed dimension
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
