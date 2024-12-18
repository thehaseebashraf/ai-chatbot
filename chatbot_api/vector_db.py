import os
import fitz
import re
from sentence_transformers import SentenceTransformer
import torch
from qdrant_client import QdrantClient, models
from qdrant_client.models import VectorParams, Distance
from django.conf import settings

class VectorDBService:
    _instance = None
    _is_initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorDBService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._is_initialized:
            self.client = QdrantClient(
                url="https://0226cf72-a7d5-4bf6-be5f-7f78f89f6733.europe-west3-0.gcp.cloud.qdrant.io:6333",
                api_key="_2Pmz-cQGsZCcgw5EW8YAjH31vh5XHlvSSCp7mF6scPMOJSsLXNm3g",
            )
            self.collection_name = "qa_index"
            self.embedding_model = None
            VectorDBService._is_initialized = True

    # @classmethod
    # def initialize_singleton(cls):
    #     """Initialize the singleton instance and vector DB"""
    #     instance = cls()
    #     instance.initialize_vector_db()
    #     return instance

    @staticmethod
    def clean_text(text):
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def initialize_embedding_model(self):
        if self.embedding_model is None:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            model_name = "BAAI/bge-small-en-v1.5"
            self.embedding_model = SentenceTransformer(model_name, device=device)

    def search(self, text: str, top_k: int):
        self.initialize_embedding_model()
        
        collections = self.client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        if self.collection_name not in collection_names:
            raise ValueError("No embeddings found. Please upload a document first.")
        
        query_embedding = self.embedding_model.encode(text).tolist()

        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=None,
            limit=top_k
        )
        return search_result

    def clear_existing_embeddings(self):
        """Clear all existing embeddings from the collection"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[],  # Empty filter means delete all
                    )
                )
            )
        except Exception as e:
            print(f"Error clearing embeddings: {str(e)}")

    def initialize_vector_db(self, pdf_path):
        # Initialize embedding model
        self.initialize_embedding_model()

        if pdf_path is None:
            raise ValueError("PDF path is required")
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at {pdf_path}")

        # Clear existing embeddings before adding new ones
        self.clear_existing_embeddings()

        # Read the PDF
        doc = fitz.open(pdf_path)
        entire_text = ""

        for page in doc:
            page_text = page.get_text()
            cleaned_page_text = self.clean_text(page_text)
            entire_text += cleaned_page_text + " "

        doc.close()

        # Split text into chunks
        text_splitter = CustomTextSplitter(chunk_size=500, chunk_overlap=50)
        text_chunks = text_splitter.split_text(entire_text)

        # Generate embeddings
        embeddings = self.embedding_model.encode(text_chunks, show_progress_bar=True)

        # Reset collection
        try:
            self.client.delete_collection(self.collection_name)
        except:
            pass  # Collection might not exist yet

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )

        # Upload to Qdrant
        ids = list(range(len(text_chunks)))
        payload = [{"source": "local_pdf", "content": text} for text in text_chunks]

        self.client.upload_collection(
            collection_name=self.collection_name,
            vectors=embeddings,
            payload=payload,
            ids=ids,
            batch_size=256,
        )

        print(f"Vector database initialized with {len(text_chunks)} chunks")


class CustomTextSplitter:
    def __init__(self, chunk_size=500, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text):
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size

            if end < len(text):
                next_period = text.find('.', end - self.chunk_size // 2)
                if next_period != -1 and next_period < end + self.chunk_size // 2:
                    end = next_period + 1
                else:
                    while end > start and not text[end].isspace():
                        end -= 1
                    if end == start:
                        end = start + self.chunk_size

            chunk = text[start:end].strip()
            chunks.append(chunk)
            start = end - self.chunk_overlap

        return chunks 