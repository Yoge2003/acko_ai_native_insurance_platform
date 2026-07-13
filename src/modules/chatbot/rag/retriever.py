import logging
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from .vector_store import ChromaVectorStore

logger = logging.getLogger(__name__)

class PolicyRetriever:
    """
    RAG utility to search and retrieve relevant text chunks from the vector database.
    Supports similarity search, top-k configurations, and metadata filtering.
    """
    def __init__(self, vector_store: ChromaVectorStore):
        self.vector_store = vector_store

    def retrieve(
        self, 
        query: str, 
        k: int = 4, 
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Retrieves the top-k most similar policy document chunks matching the query.
        Optionally filters results by metadata properties (e.g. document_type, filename).
        """
        logger.info(f"Retrieving top {k} contexts for query: '{query}' (Filter: {filter})")
        return self.vector_store.similarity_search(query, k=k, filter=filter)

    def retrieve_by_document_type(
        self, 
        query: str, 
        document_type: str, 
        k: int = 4
    ) -> List[Document]:
        """
        Retrieving helper restricted to a specific policy type (e.g. 'health_insurance').
        """
        filter_dict = {"document_type": document_type}
        return self.retrieve(query, k=k, filter=filter_dict)

    def retrieve_by_filename(
        self, 
        query: str, 
        filename: str, 
        k: int = 4
    ) -> List[Document]:
        """
        Retrieving helper restricted to a specific PDF document.
        """
        filter_dict = {"filename": filename}
        return self.retrieve(query, k=k, filter=filter_dict)
