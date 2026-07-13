import os
import logging
from typing import List, Dict, Any, Optional
import chromadb
from langchain_core.documents import Document
from src.config.settings import settings
from .embedding_manager import EmbeddingManager

logger = logging.getLogger(__name__)

class LangChainChromaEmbeddingWrapper(chromadb.EmbeddingFunction):
    """
    Adapter modifying a LangChain Embedding model into a ChromaDB compatible EmbeddingFunction.
    """
    def __init__(self, langchain_embeddings):
        self.langchain_embeddings = langchain_embeddings

    def __call__(self, input: chromadb.Documents) -> chromadb.Embeddings:
        # Convert documents text blocks into vector lists
        return self.langchain_embeddings.embed_documents(input)


class ChromaVectorStore:
    """
    Native ChromaDB Wrapper handling vector store initialization,
    persistence, document indexing, and similarity queries.
    """
    def __init__(
        self, 
        persist_directory: Optional[str] = None, 
        collection_name: str = "policy_documents",
        embedding_manager: Optional[EmbeddingManager] = None
    ):
        self.persist_directory = persist_directory or settings.CHROMA_DB_PATH
        self.collection_name = collection_name
        
        # Initialize client persistence directory root
        os.makedirs(self.persist_directory, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # Setup embeddings
        self.emb_manager = embedding_manager or EmbeddingManager()
        self.embedding_function = LangChainChromaEmbeddingWrapper(
            self.emb_manager.get_embeddings()
        )
        
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function
        )
        logger.info(f"Initialized ChromaDB collection '{self.collection_name}' at '{self.persist_directory}'.")

    def add_documents(self, documents: List[Document]) -> List[str]:
        """
        Upserts a list of LangChain Document objects into ChromaDB.
        Generates unique IDs based on metadata 'chunk_id' if available.
        """
        if not documents:
            return []
            
        ids = []
        texts = []
        metadatas = []
        
        for idx, doc in enumerate(documents):
            chunk_id = doc.metadata.get("chunk_id") or f"chunk_auto_{idx}_{hash(doc.page_content)}"
            ids.append(chunk_id)
            texts.append(doc.page_content)
            
            # Sanitize metadata: Chroma only accepts str, int, float, bool as metadata values
            sanitized_meta = {}
            for k, v in doc.metadata.items():
                if isinstance(v, (str, int, float, bool)):
                    sanitized_meta[k] = v
                else:
                    sanitized_meta[k] = str(v)
            metadatas.append(sanitized_meta)
            
        self.collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )
        logger.info(f"Successfully upserted {len(documents)} document chunks into collection '{self.collection_name}'.")
        return ids

    def similarity_search(
        self, 
        query: str, 
        k: int = 4, 
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Executes a vector similarity query against stored chunks.
        Supports metadata filter arguments (passed to Chroma's where clause).
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=k,
            where=filter
        )
        
        documents = []
        if results and "documents" in results and len(results["documents"]) > 0:
            docs = results["documents"][0]
            metadatas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            ids = results["ids"][0] if "ids" in results else [None] * len(docs)
            
            for i in range(len(docs)):
                # Reconstruct document with ID enriched in metadata
                meta = metadatas[i].copy()
                if ids[i]:
                    meta["chunk_id"] = ids[i]
                documents.append(
                    Document(
                        page_content=docs[i],
                        metadata=meta
                    )
                )
                
        return documents

    def delete_documents(self, ids: List[str]) -> None:
        """
        Deletes documents matching the specified IDs from the collection.
        """
        if ids:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents from collection '{self.collection_name}'.")

    def delete_by_filename(self, filename: str) -> None:
        """
        Deletes all chunks associated with a specific file using metadata filters.
        """
        self.collection.delete(where={"filename": filename})
        logger.info(f"Cleared all entries mapped to filename '{filename}' in vector store.")

    def clear_all(self) -> None:
        """
        Wipes all documents from the active collection.
        """
        # Chroma collection.delete() with empty where isn't always supported, 
        # delete by querying empty/all or recreate collection.
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"Wiped and re-created collection '{self.collection_name}'.")
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}", exc_info=True)
