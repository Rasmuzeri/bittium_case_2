import os
import faiss
import numpy as np
import pickle
import time
from sentence_transformers import SentenceTransformer
import PyPDF2


class RAGSystem:
    def __init__(self, model_name="all-MiniLM-L12-v2", chunk_size=256,
                 overlap=50, index_path="rag_index"):
        self.model = SentenceTransformer(model_name)
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.index = None
        self.chunks = []
        self.chunk_to_file = {}
        self.indexed_files = set()  # Track which files have been indexed
        self.index_path = index_path
        self.data_path = f"{index_path}_data.pkl"

    def _chunk_with_overlap(self, text, file_path):
        words = text.split()
        chunks = [" ".join(words[i:i + self.chunk_size]) for i in
                  range(0, len(words), self.chunk_size - self.overlap)]
        for chunk in chunks:
            self.chunk_to_file[chunk] = file_path
        return chunks

    def _embed_chunks(self, chunks):
        return np.array([self.model.encode(chunk) for chunk in chunks],
                        dtype=np.float32)

    def add_text_data(self, text, file_path):
        new_chunks = self._chunk_with_overlap(text, file_path)
        new_embeddings = self._embed_chunks(new_chunks)
        if self.index is None:
            dimension = new_embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)

        self.index.add(new_embeddings)
        self.chunks.extend(new_chunks)
        self.indexed_files.add(file_path)  # Add to indexed files set

    def save_index(self):
        """Save the index and associated data to disk"""
        if self.index is None:
            print("No index to save")
            return False
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.index_path) if os.path.dirname(self.index_path) else '.', exist_ok=True)
        
        # Save the FAISS index
        faiss.write_index(self.index, self.index_path)
        
        # Save the chunks, chunk_to_file mapping, and the set of indexed files
        with open(self.data_path, 'wb') as f:
            pickle.dump((self.chunks, self.chunk_to_file, self.indexed_files), f)
            
        print(f"Index saved to {self.index_path} and {self.data_path}")
        return True

    def load_index(self):
        """Load the index and associated data from disk"""
        start_time = time.time()
        
        if not os.path.exists(self.index_path) or not os.path.exists(self.data_path):
            print("Index files not found, will create new index")
            return False
            
        try:
            # Load the FAISS index
            self.index = faiss.read_index(self.index_path)
            
            # Load the chunks, chunk_to_file mapping, and the set of indexed files
            with open(self.data_path, 'rb') as f:
                data = pickle.load(f)
                if len(data) == 3:  # New format with indexed_files
                    self.chunks, self.chunk_to_file, self.indexed_files = data
                else:  # Old format for backward compatibility
                    self.chunks, self.chunk_to_file = data
                    # Recreate indexed_files from chunk_to_file
                    self.indexed_files = set(self.chunk_to_file.values())
                
            elapsed_time = time.time() - start_time
            print(f"Index loaded from {self.index_path} in {elapsed_time:.2f} seconds")
            print(f"Index contains {self.index.ntotal} vectors from {len(self.indexed_files)} files")
            return True
        except Exception as e:
            print(f"Error loading index: {e}")
            self.index = None
            self.chunks = []
            self.chunk_to_file = {}
            self.indexed_files = set()
            return False

    def add_directory(self, base_path):
        start_time = time.time()
        
        # Try to load existing index first
        index_existed = self.load_index()
        
        # Get all files in the directory
        all_text_files = self.read_text_files(base_path)
        
        if index_existed:
            # Only process new files that aren't already in the index
            new_files = {path: text for path, text in all_text_files.items() 
                         if path not in self.indexed_files}
            
            if new_files:
                print(f"Found {len(new_files)} new files to add to the existing index")
                for file_path, text in new_files.items():
                    print(f"Adding new file: {file_path}")
                    self.add_text_data(text, file_path)
                    self.indexed_files.add(file_path)
                
                # Save the updated index
                self.save_index()
                print(f"Index updated with {len(new_files)} new files")
            else:
                print("No new files found to add to the index")
                
            elapsed_time = time.time() - start_time
            print(f"Index check/update completed in {elapsed_time:.2f} seconds")
        else:
            # If loading failed, build a new index
            print(f"Building new index from {base_path}...")
            for file_path, text in all_text_files.items():
                self.add_text_data(text, file_path)
                self.indexed_files.add(file_path)
                
            # Save the newly created index
            self.save_index()
            
            elapsed_time = time.time() - start_time
            print(f"New index built with {len(all_text_files)} files in {elapsed_time:.2f} seconds")

    def search(self, query, k=2):
        if self.index is None or self.index.ntotal == 0:
            return []

        query_embedding = self.model.encode(query).astype(np.float32).reshape(1, -1)
        distances, indices = self.index.search(query_embedding, k)

        results = [(self.chunks[idx], self.chunk_to_file[self.chunks[idx]]) for
                   idx in indices[0]]
        return results

    @staticmethod
    def read_text_files(base_path):
        text_data = {}
        for root, _, files in os.walk(base_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Handle text files
                if file.endswith(".txt"):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            text_data[file_path] = f.read()
                    except Exception as e:
                        print(f"Error reading text file {file_path}: {e}")
                # Handle PDF files
                elif file.endswith(".pdf"):
                    try:
                        text = RAGSystem.extract_text_from_pdf(file_path)
                        if text:
                            text_data[file_path] = text
                    except Exception as e:
                        print(f"Error reading PDF file {file_path}: {e}")
        return text_data
    
    @staticmethod
    def extract_text_from_pdf(file_path):
        """Extract text from a PDF file."""
        try:
            text = ""
            with open(file_path, "rb") as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error extracting text from PDF {file_path}: {e}")
            return ""

    def add_incremental_update(self, new_docs_path):
        """Add new documents to the existing index without rebuilding"""
        text_files = self.read_text_files(new_docs_path)
        for file_path, text in text_files.items():
            self.add_text_data(text, file_path)
        self.save_index()
