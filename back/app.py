from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
import torch
import json
import time
import os
from faiss_rag import RAGSystem
import logging
from datetime import datetime


# Initialize RAG system with a specific index path
print("Initializing RAG system...")
start_time = time.time()
rag = RAGSystem(index_path="./rag_index")

# Set the documents directory path
docs_dir = os.path.abspath("python-3.13-docs-text/")
if not os.path.exists(docs_dir):
    docs_dir = "E:/bittium_case_2/python-3.13-docs-text/"

# Add documents to the RAG system
rag.add_directory(docs_dir)
print(f"RAG system initialization completed in {time.time() - start_time:.2f} seconds")

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Enable CORS for all origins on /api/* routes

# Load the Hugging Face model once at startup
device = "cuda" if torch.cuda.is_available() else "cpu"
model_id = "HuggingFaceTB/SmolLM-135M-Instruct"
print("Loading chatbot model...")
start_time = time.time()
chatbot = pipeline('text-generation', model=model_id, max_new_tokens=200, device=device)
print(f"Chatbot model loaded in {time.time() - start_time:.2f} seconds")

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

    agent1 = "You are a coding assistant"

    messages = [
        {'role': 'system', 'content': agent1},
        {'role': 'user', 'content': user_message}
    ]

    response1 = chatbot(messages)[0]['generated_text'][-1]['content']
    print("response1")
    print(response1)

    agent2 = """Your task is to create queries for the RAG model.
    The input is a code created by another AI agent.
    The output is a list of queries that the RAG model can use to find relevant information
    about the style and features of the code. The code must follow the most recent good practices
    and coding standards. The queries should be specific and relevant to the code.
    The RAG contains documents about coding languages, coding standards, and best practices.
    The output must be in JSON format.
    The output must be in json format and follow the following structure:
    {
        "queries": [
        "query1",
        "query2",
        ]
    }
    """

    messages2 = [
        {'role': 'system', 'content': agent2},
        {'role': 'user', 'content': response1}
    ]

    response2 = chatbot(messages2)[0]['generated_text'][-1]['content']

    print("response2")
    print(response2)

    queries = json.loads(response2)['queries']

    rag_responses = []

    for query in queries:
        rag_response = rag.search(query, k=2)
        rag_responses.append(rag_response)

    print("rag_responses")
    print(rag_responses)

    agent3 = """
    You are given two inputs: a code created by another AI agent and a list of RAG responses
    retrieved from a database containting information about the latest coding standards and 
    best practices. Your task is to analyze each RAG response and how it applies to the code.
    If you notice any issues or areas for improvement in the code, modify the code to follow
    the most recent good practices and coding standards. The intent of the code must not change.
    """

    messages3 = [
        {'role': 'system', 'content': agent3},
        {'role': 'user', 'content': response1},
        {'role': 'user', 'content': rag_responses}
    ]

    # Generate a response using the Hugging Face model
    bot_response = chatbot(messages3)[0]['generated_text'][-1]['content']
    
    elapsed_time = time.time() - start_time
    logging.info(f"Request {request_id} processed in {elapsed_time:.2f} seconds")
    
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True)
