from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import json
import time
import os
from faiss_rag import RAGSystem
import logging
from datetime import datetime
from llm_handler import LLMHandler


# Initialize RAG system with a specific index path
print("Initializing RAG system...")
start_time = time.time()
rag = RAGSystem(index_path="./rag_index")

# Set the documents directory path
docs_dir = os.path.abspath("python-3.13-docs-text/")
if not os.path.exists(docs_dir):
    docs_dir = "C:/Users/veeti/Documents/bittium_case_2/documents"

# Add documents to the RAG system - now with incremental updating
rag.add_directory(docs_dir)
print(f"RAG system initialization completed in {time.time() - start_time:.2f} seconds")

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Enable CORS for all origins on /api/* routes

# Initialize the LLM handler
print("Initializing LLM handler...")
start_time = time.time()
llm_handler = LLMHandler(model="gpt-3.5-turbo")
print(f"LLM handler initialized in {time.time() - start_time:.2f} seconds")

# Set up logging
logging.basicConfig(
    filename='ai_assistant.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@app.route('/api/chat', methods=['POST'])
def chat():
    start_time = time.time()
    request_id = str(int(time.time() * 1000))
    
    logging.info(f"Request {request_id} received")
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    
    user_message = data['message']

    # Get initial response from the LLM
    response1 = llm_handler.chat_response(user_message)
    print("response1")
    print(response1)

    # Generate queries for the RAG system
    queries = llm_handler.generate_code_queries(response1)
    print("Generated queries:", queries)

    # Get RAG responses for each query
    rag_responses = []
    for query in queries:
        rag_response = rag.search(query, k=2)
        rag_responses.append(rag_response)
    print("rag_responses")
    print(rag_responses)

    # Improve the code with RAG responses
    bot_response = llm_handler.improve_code_with_rag(response1, rag_responses)
    
    elapsed_time = time.time() - start_time
    logging.info(f"Request {request_id} processed in {elapsed_time:.2f} seconds")
    
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True)
