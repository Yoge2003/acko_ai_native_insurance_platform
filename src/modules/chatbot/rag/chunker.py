import logging
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class IntelligentChunker:
    """
    Splits policy documents into smaller, semantically cohesive chunks
    while preserving paragraph/sentence boundaries and metadata properties.
    """
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # Initialize LangChain's splitter
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            keep_separator=True
        )

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Splits a list of Documents into chunk Documents.
        Encodes unique chunk_id and chunk_index metadata properties.
        """
        chunked_docs = []
        for doc in documents:
            filename = doc.metadata.get("filename", "unknown_document")
            page_no = doc.metadata.get("page", 1)
            
            # Split the text
            chunks = self.splitter.split_text(doc.page_content)
            
            for idx, text_chunk in enumerate(chunks):
                # Form deterministic unique reference index
                chunk_id = f"{filename}_page{page_no}_chunk{idx}"
                
                # Copy parental metadata and enrich
                new_metadata = doc.metadata.copy()
                new_metadata.update({
                    "chunk_id": chunk_id,
                    "chunk_index": idx,
                    "chunk_size": len(text_chunk)
                })
                
                chunked_docs.append(
                    Document(
                        page_content=text_chunk,
                        metadata=new_metadata
                    )
                )
                
        logger.info(f"Split {len(documents)} parent documents into {len(chunked_docs)} semantic chunks.")
        return chunked_docs
