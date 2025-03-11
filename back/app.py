from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
import torch
import json
from faiss_rag import RAGSystem


rag = RAGSystem()
rag.add_directory("E:/bittium_case_2/python-3.13-docs-text/deprecations")


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Enable CORS for all origins on /api/* routes

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    
    
    device = "cuda" if torch.cuda.is_available() else "cpu"

    model_id = "HuggingFaceTB/SmolLM-135M-Instruct"
    
    # Load the Hugging Face model
    chatbot = pipeline('text-generation', model=model_id, max_new_tokens=200, device=device)

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
    
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True)
