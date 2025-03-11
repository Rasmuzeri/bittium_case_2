import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class RAGSystem:
    def __init__(self, model_name="all-MiniLM-L12-v2", chunk_size=256,
                 overlap=50):
        self.model = SentenceTransformer(model_name)
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.index = None
        self.chunks = []
        self.chunk_to_file = {}

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

    def add_directory(self, base_path):
        text_files = self.read_text_files(base_path)
        for file_path, text in text_files.items():
            self.add_text_data(text, file_path)

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
