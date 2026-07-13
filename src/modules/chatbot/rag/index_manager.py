import os
import json
import hashlib
import logging
from typing import List, Dict, Any, Optional
from src.config.settings import settings
from .document_loader import PolicyDocumentLoader
from .chunker import IntelligentChunker
from .vector_store import ChromaVectorStore

logger = logging.getLogger(__name__)

class IndexManager:
    """
    Orchestrates the ingestion pipeline: Loader -> Chunker -> VectorStore.
    Maintains a hash-based registry of indexed files to enable incremental indexing
    and handles complete re-indexing operations.
    """
    def __init__(
        self,
        vector_store: ChromaVectorStore,
        loader: Optional[PolicyDocumentLoader] = None,
        chunker: Optional[IntelligentChunker] = None
    ):
        self.vector_store = vector_store
        self.loader = loader or PolicyDocumentLoader()
        self.chunker = chunker or IntelligentChunker()
        
        # State tracking file path
        self.registry_path = os.path.join(self.vector_store.persist_directory, "index_registry.json")

    def run_ingestion(self, force_reindex: bool = False) -> Dict[str, Any]:
        """
        Executes the ingestion pipeline. Runs incrementally by default.
        Wipes the database and registry if force_reindex is True.
        """
        if force_reindex:
            logger.info("Force reindex requested. Clearing vector store and registry...")
            self.vector_store.clear_all()
            self._save_registry({})
            
        registry = self._load_registry()
        
        # Scan source directory for files
        source_dir = self.loader.directory_path
        if not os.path.exists(source_dir):
            logger.error(f"Source directory '{source_dir}' does not exist. Aborting ingestion.")
            return {
                "status": "error",
                "message": f"Source directory '{source_dir}' does not exist.",
                "processed_files": [],
                "skipped_files": [],
                "total_chunks_added": 0
            }
            
        processed_files = []
        skipped_files = []
        total_chunks = 0
        
        # Retrieve all candidate PDFs
        pdf_files = [f for f in os.listdir(source_dir) if f.lower().endswith(".pdf")]
        logger.info(f"Scanning '{source_dir}' found {len(pdf_files)} PDF files to process.")
        
        new_registry = registry.copy()
        
        for file in pdf_files:
            file_path = os.path.join(source_dir, file)
            current_hash = self._compute_file_hash(file_path)
            
            # Check for duplicate prevention
            if not force_reindex and registry.get(file) == current_hash:
                logger.info(f"Incremental Ingestion: File '{file}' already indexed and unchanged. Skipping.")
                skipped_files.append(file)
                continue
                
            logger.info(f"Ingesting file: '{file}' (New or Modified).")
            
            # 1. Clean existing records for this file to prevent partial chunk duplicates
            if file in registry:
                logger.info(f"Removing old vector database records for '{file}' before overwrite.")
                self.vector_store.delete_by_filename(file)
                
            # 2. Extract Document pages
            pages = self.loader.load_file(file_path)
            if not pages:
                logger.warning(f"File '{file}' returned empty content. Skipping registration.")
                continue
                
            # 3. Create semantic chunks
            chunks = self.chunker.split_documents(pages)
            if not chunks:
                logger.warning(f"No text chunks generated for file '{file}'.")
                continue
                
            # 4. Insert into ChromaDB
            self.vector_store.add_documents(chunks)
            
            # 5. Record state
            new_registry[file] = current_hash
            processed_files.append(file)
            total_chunks += len(chunks)
            
        # Persist registry updates
        self._save_registry(new_registry)
        
        summary = {
            "status": "success",
            "processed_files": processed_files,
            "skipped_files": skipped_files,
            "total_chunks_added": total_chunks
        }
        logger.info(f"Ingestion completed: {summary}")
        return summary

    def _compute_file_hash(self, filepath: str) -> str:
        """
        Computes the SHA256 checksum of a file.
        """
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256.update(byte_block)
        return sha256.hexdigest()

    def _load_registry(self) -> Dict[str, str]:
        """
        Loads the json status registry from disk.
        """
        if not os.path.exists(self.registry_path):
            return {}
        try:
            with open(self.registry_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read index registry database: {e}. Returning empty.")
            return {}

    def _save_registry(self, registry: Dict[str, str]) -> None:
        """
        Writes the json status registry to disk.
        """
        try:
            with open(self.registry_path, "w", encoding="utf-8") as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to persist index registry database: {e}")
