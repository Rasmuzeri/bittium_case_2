import os
import faiss
import numpy as np
import pickle
import time
from sentence_transformers import SentenceTransformer


class RAGSystem:
    def __init__(self, model_name="all-MiniLM-L12-v2", chunk_size=256,
                 overlap=50, index_path="rag_index"):
        self.model = SentenceTransformer(model_name)
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.index = None
        self.chunks = []
        self.chunk_to_file = {}
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

    def save_index(self):
        """Save the index and associated data to disk"""
        if self.index is None:
            print("No index to save")
            return False
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.index_path) if os.path.dirname(self.index_path) else '.', exist_ok=True)
        
        # Save the FAISS index
        faiss.write_index(self.index, self.index_path)
        
        # Save the chunks and chunk_to_file mapping
        with open(self.data_path, 'wb') as f:
            pickle.dump((self.chunks, self.chunk_to_file), f)
            
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
            
            # Load the chunks and chunk_to_file mapping
            with open(self.data_path, 'rb') as f:
                self.chunks, self.chunk_to_file = pickle.load(f)
                
            elapsed_time = time.time() - start_time
            print(f"Index loaded from {self.index_path} in {elapsed_time:.2f} seconds")
            print(f"Index contains {self.index.ntotal} vectors")
            return True
        except Exception as e:
            print(f"Error loading index: {e}")
            self.index = None
            self.chunks = []
            self.chunk_to_file = {}
            return False

    def add_directory(self, base_path):
        start_time = time.time()
        
        # Try to load existing index first
        if self.load_index():
            elapsed_time = time.time() - start_time
            print(f"Using existing index, initialization took {elapsed_time:.2f} seconds")
            return
            
        # If loading failed, build a new index
        print(f"Building new index from {base_path}...")
        text_files = self.read_text_files(base_path)
        for file_path, text in text_files.items():
            self.add_text_data(text, file_path)
            
        # Save the newly created index
        self.save_index()
        
        elapsed_time = time.time() - start_time
        print(f"Index built and saved, initialization took {elapsed_time:.2f} seconds")

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
                if file.endswith(".txt"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            text_data[file_path] = f.read()
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
        return text_data

    def add_incremental_update(self, new_docs_path):
        """Add new documents to the existing index without rebuilding"""
        text_files = self.read_text_files(new_docs_path)
        for file_path, text in text_files.items():
            self.add_text_data(text, file_path)
        self.save_index()

    def _chunk_with_metadata(self, text, file_path):
        """Enhanced chunking that includes metadata"""
        # ... existing code ...
        # Add metadata like creation date, source, etc.
        # ... existing code ...
