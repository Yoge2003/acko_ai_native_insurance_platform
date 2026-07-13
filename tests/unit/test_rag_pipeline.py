import os
import shutil
import unittest
import tempfile
from unittest.mock import patch
from langchain_core.documents import Document
from src.modules.chatbot.rag.document_loader import PolicyDocumentLoader
from src.modules.chatbot.rag.chunker import IntelligentChunker
from src.modules.chatbot.rag.embedding_manager import EmbeddingManager, DeterministicMockEmbeddings
from src.modules.chatbot.rag.vector_store import ChromaVectorStore
from src.modules.chatbot.rag.index_manager import IndexManager
from src.modules.chatbot.rag.retriever import PolicyRetriever

class TestRAGPipelineSuite(unittest.TestCase):
    """
    Test suite verifying correctness, boundaries, incremental ingestion, 
    and retrieval logic of the RAG pipeline.
    """
    def setUp(self) -> None:
        # Create isolated workspace directory for test Chroma instances
        self.test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "tmp_test_chroma"))
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Instantiate embedder
        self.embedding_manager = EmbeddingManager(google_api_key="your_gemini_api_key_here")  # Forces Mock embeddings
        self.vector_store = ChromaVectorStore(
            persist_directory=self.test_dir, 
            collection_name="test_collection",
            embedding_manager=self.embedding_manager
        )
        self.retriever = PolicyRetriever(self.vector_store)

    def tearDown(self) -> None:
        # Clean up database resources and directories
        self.vector_store.clear_all()
        # Drop reference to close SQLite links within Chroma PersistentClient
        self.vector_store = None
        self.retriever = None
        
        # Force garbage collection to release file locks on Windows
        import gc
        gc.collect()
        
        # Cleanup temporary files
        if os.path.exists(self.test_dir):
            try:
                shutil.rmtree(self.test_dir)
            except Exception:
                pass

    def test_mock_embedding_determinism(self) -> None:
        """
        Verifies that DeterministicMockEmbeddings produces values consistent
        with cosine similarity (deterministic mapping).
        """
        embedder = DeterministicMockEmbeddings(dimension=128)
        text1 = "How to submit a claim request on health policy"
        text2 = "How to submit a claim request on health policy"
        text3 = "Completely different text related to motor vehicles"
        
        vec1 = embedder.embed_query(text1)
        vec2 = embedder.embed_query(text2)
        vec3 = embedder.embed_query(text3)
        
        self.assertEqual(len(vec1), 128)
        self.assertEqual(vec1, vec2)  # Deterministic mapping
        self.assertNotEqual(vec1, vec3)

    def test_document_loader_parsing_and_metadata(self) -> None:
        """
        Verifies loader handles real PDFs, parses fields, and maps insurance metadata.
        """
        loader = PolicyDocumentLoader()
        
        # Look for real PDFs in DataSet/Policy_Documents
        docs = loader.load_all()
        self.assertTrue(len(docs) > 0, "No PDFs found in default DataSet directory to test loading.")
        
        for doc in docs:
            self.assertIsNotNone(doc.page_content)
            self.assertIn("filename", doc.metadata)
            self.assertIn("page", doc.metadata)
            self.assertIn("document_type", doc.metadata)
            self.assertIn("section_heading", doc.metadata)
            self.assertIn("source", doc.metadata)
            
            # Types check
            self.assertTrue(isinstance(doc.metadata["page"], int))
            self.assertIn(doc.metadata["document_type"], ["health_insurance", "motor_insurance", "general_faq", "policy_document"])

    def test_chunk_creation_and_enrichment(self) -> None:
        """
        Verifies list splitting of pages, unique chunk_id formats, and inheritance checks.
        """
        parent_doc = Document(
            page_content="This is the first sentence. This is the second sentence. " * 20,
            metadata={
                "filename": "testpolicy.pdf",
                "page": 2,
                "document_type": "motor_insurance",
                "section_heading": "Exclusions"
            }
        )
        
        chunker = IntelligentChunker(chunk_size=150, chunk_overlap=20)
        chunks = chunker.split_documents([parent_doc])
        
        self.assertGreater(len(chunks), 1)
        for idx, chunk in enumerate(chunks):
            self.assertEqual(chunk.metadata["filename"], "testpolicy.pdf")
            self.assertEqual(chunk.metadata["page"], 2)
            self.assertEqual(chunk.metadata["chunk_index"], idx)
            self.assertEqual(chunk.metadata["chunk_id"], f"testpolicy.pdf_page2_chunk{idx}")
            self.assertTrue(len(chunk.page_content) <= 150)

    def test_vector_indexing_and_persistence(self) -> None:
        """
        Verifies indexing files correctly stores content in ChromaDB and returns IDs.
        """
        test_docs = [
            Document(page_content="Health policy is coverage for illness", metadata={"chunk_id": "c1", "filename": "f1.pdf", "page": 1}),
            Document(page_content="Motor policy covers car collisions", metadata={"chunk_id": "c2", "filename": "f1.pdf", "page": 2})
        ]
        
        ids = self.vector_store.add_documents(test_docs)
        self.assertEqual(ids, ["c1", "c2"])
        
        # Verify direct retrieval matches
        saved = self.vector_store.similarity_search("coverage for illness", k=1)
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0].page_content, "Health policy is coverage for illness")
        self.assertEqual(saved[0].metadata["chunk_id"], "c1")

    def test_duplicate_prevention_incremental_indexing(self) -> None:
        """
        Verifies that IndexManager prevents duplicates by skipping unmodified files
        and performs reindexing when forced.
        """
        # Create isolated dummy ingestion folder
        ingest_test_dir = os.path.join(self.test_dir, "test_ingest_source")
        os.makedirs(ingest_test_dir, exist_ok=True)
        
        # 1. Create a mock loader pointing here
        loader = PolicyDocumentLoader(directory_path=ingest_test_dir)
        chunker = IntelligentChunker(chunk_size=200, chunk_overlap=10)
        index_manager = IndexManager(self.vector_store, loader=loader, chunker=chunker)
        
        # Save a mock policy doc (Simulate PDF file)
        # Actually loading will try fitz/pypdf, which will fail for raw text files disguised as PDF.
        # So we mock load_file on PolicyDocumentLoader to bypass pdf binary reading.
        with patch.object(PolicyDocumentLoader, 'load_file') as mock_load:
            # Configure mocked loading return value
            mock_load.return_value = [
                Document(page_content="Sample terms definition page 1", metadata={"filename": "mockpolicy.pdf", "page": 1, "document_type": "motor_insurance"})
            ]
            
            # Create a physical file representing mockpolicy.pdf to hash
            dummy_pdf = os.path.join(ingest_test_dir, "mockpolicy.pdf")
            with open(dummy_pdf, "w") as f:
                f.write("Physical PDF file representation hash target structure contents.")
                
            # 2. Run first incremental ingestion
            summary_1 = index_manager.run_ingestion(force_reindex=False)
            self.assertEqual(summary_1["processed_files"], ["mockpolicy.pdf"])
            self.assertEqual(summary_1["skipped_files"], [])
            self.assertEqual(summary_1["total_chunks_added"], 1)
            
            # 3. Run second ingestion with no modifications
            summary_2 = index_manager.run_ingestion(force_reindex=False)
            self.assertEqual(summary_2["processed_files"], [])
            self.assertEqual(summary_2["skipped_files"], ["mockpolicy.pdf"])
            self.assertEqual(summary_2["total_chunks_added"], 0)
            
            # 4. Modify physical content mapping
            with open(dummy_pdf, "a") as f:
                f.write("Modification content changes bytes.")
                
            summary_3 = index_manager.run_ingestion(force_reindex=False)
            self.assertEqual(summary_3["processed_files"], ["mockpolicy.pdf"])
            self.assertEqual(summary_3["skipped_files"], [])
            self.assertEqual(summary_3["total_chunks_added"], 1)
            
            # 5. Forced reindex check
            summary_4 = index_manager.run_ingestion(force_reindex=True)
            self.assertEqual(summary_4["processed_files"], ["mockpolicy.pdf"])
            self.assertEqual(summary_4["skipped_files"], [])
            self.assertEqual(summary_4["total_chunks_added"], 1)

    def test_retrieval_correctness_and_filtering(self) -> None:
        """
        Verifies retrieval matches search queries, respects k caps, 
        and correctly applies metadata filters (e.g. document type).
        """
        test_docs = [
            Document(
                page_content="Under health policy cover, hospital stay costs are covered.", 
                metadata={"chunk_id": "h1", "filename": "health.pdf", "page": 1, "document_type": "health_insurance"}
            ),
            Document(
                page_content="Under motor policy, car mechanical wear and tear is excluded.", 
                metadata={"chunk_id": "m1", "filename": "motor.pdf", "page": 3, "document_type": "motor_insurance"}
            )
        ]
        self.vector_store.add_documents(test_docs)
        
        # 1. Similarity query match
        res = self.retriever.retrieve("hospital stay costs", k=1)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].metadata["chunk_id"], "h1")
        
        # 2. Top-k restriction check
        res_k = self.retriever.retrieve("policy document details", k=2)
        self.assertEqual(len(res_k), 2)
        
        # 3. Filtering check: restriction on motor_insurance
        res_filtered = self.retriever.retrieve("hospital costs", filter={"document_type": "motor_insurance"})
        self.assertEqual(len(res_filtered), 1)
        self.assertEqual(res_filtered[0].metadata["chunk_id"], "m1")  # Matches due to keyword query but filtered to motor
        
        # 4. Filter check by filename
        res_file = self.retriever.retrieve_by_filename("policy", filename="health.pdf")
        self.assertEqual(len(res_file), 1)
        self.assertEqual(res_file[0].metadata["chunk_id"], "h1")
