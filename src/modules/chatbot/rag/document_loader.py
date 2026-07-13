import os
import re
import logging
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class PolicyDocumentLoader:
    """
    Robust loader to parse and extract text and metadata from policy PDF files
    in theDataSet/Policy_Documents directory. Supports both PyMuPDF (fitz) and pypdf.
    """
    def __init__(self, directory_path: str = "DataSet/Policy_Documents"):
        self.directory_path = directory_path
        
    def load_all(self) -> List[Document]:
        """
        Loads all PDF files in the target directory and parses them into custom Documents.
        """
        documents = []
        if not os.path.exists(self.directory_path):
            logger.warning(f"Target directory {self.directory_path} does not exist.")
            return documents
            
        for file in os.listdir(self.directory_path):
            if file.lower().endswith(".pdf"):
                file_path = os.path.join(self.directory_path, file)
                try:
                    docs = self.load_file(file_path)
                    documents.extend(docs)
                except Exception as e:
                    logger.error(f"Failed to load and parse file {file_path}: {e}", exc_info=True)
                    
        return documents

    def load_file(self, file_path: str) -> List[Document]:
        """
        Loads a single PDF file and returns a list of LangChain Document objects (one per page).
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        filename = os.path.basename(file_path)
        doc_type = self._derive_document_type(filename)
        
        # Try PyMuPDF (fitz) first, then fallback to pypdf
        try:
            return self._load_with_pymupdf(file_path, filename, doc_type)
        except ImportError:
            logger.info("PyMuPDF not available or failed to import, falling back to pypdf.")
            return self._load_with_pypdf(file_path, filename, doc_type)
        except Exception as e:
            logger.warning(f"PyMuPDF load failed for {filename}, falling back to pypdf. Error: {e}")
            return self._load_with_pypdf(file_path, filename, doc_type)

    def _derive_document_type(self, filename: str) -> str:
        """
        Deduce the insurance policy document type from its filename.
        """
        fn_lower = filename.lower()
        if "health" in fn_lower:
            return "health_insurance"
        elif "motor" in fn_lower or "car" in fn_lower or "bike" in fn_lower:
            return "motor_insurance"
        elif "faq" in fn_lower:
            return "general_faq"
        else:
            return "policy_document"

    def _load_with_pymupdf(self, file_path: str, filename: str, doc_type: str) -> List[Document]:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        documents = []
        
        # Table of contents (TOC): list of lists: [level, title, page_no] (1-indexed page_no)
        toc = doc.get_toc()
        toc_map = {}  # page_no -> heading
        for entry in toc:
            level, title, page_no = entry[0], entry[1], entry[2]
            # Map lowest-level or first encountered heading to the page
            if page_no not in toc_map:
                toc_map[page_no] = title

        for page_idx in range(len(doc)):
            page_no = page_idx + 1
            page = doc[page_idx]
            text = page.get_text("text").strip()
            
            # Identify section heading
            section_heading = toc_map.get(page_no)
            if not section_heading:
                section_heading = self._heuristically_extract_section_heading(text)
                
            metadata = {
                "source": file_path,
                "filename": filename,
                "page": page_no,
                "document_type": doc_type,
                "section_heading": section_heading or "General Information"
            }
            documents.append(Document(page_content=text, metadata=metadata))
            
        doc.close()
        return documents

    def _load_with_pypdf(self, file_path: str, filename: str, doc_type: str) -> List[Document]:
        import pypdf
        documents = []
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page_idx in range(len(reader.pages)):
                page_no = page_idx + 1
                page = reader.pages[page_idx]
                text = page.extract_text().strip()
                
                section_heading = self._heuristically_extract_section_heading(text)
                
                metadata = {
                    "source": file_path,
                    "filename": filename,
                    "page": page_no,
                    "document_type": doc_type,
                    "section_heading": section_heading or "General Information"
                }
                documents.append(Document(page_content=text, metadata=metadata))
        return documents

    def _heuristically_extract_section_heading(self, text: str) -> Optional[str]:
        """
        Find potential headings inside page text if no PDF outlines/TOC exist.
        Searches for bold-like keywords: "SECTION X", "TABLE OF CONTENTS", or short capitalized lines.
        """
        if not text:
            return None
            
        # Look at the first 5 lines of text
        lines = [line.strip() for line in text.split("\n") if line.strip()][:5]
        for line in lines:
            # Pattern matching for headers like "1. Definitions", "SECTION I", "Policy Exclusions"
            if re.match(r'^(?:(?:SECTION|CHAPTER|PART|ARTICLE)\s+[IVXLCDM\d]+|[\d\.]+\s+[A-Za-z]+)', line, re.IGNORECASE):
                return line
            if len(line) < 60 and line.isupper() and not line.startswith("Page"):
                return line
                
        # If nothing matches, check if first line is short and uppercase/title cased
        if lines and len(lines[0]) < 50:
            return lines[0]
            
        return None
