# AI-Powered Coding Assistant

## Project Overview
This project is an AI-powered coding assistant that helps developers improve their code by providing suggestions based on best practices and coding standards. The application consists of a web-based chat interface where users can input code or coding questions, and the system responds with optimized code suggestions. The verbal conversational aspect of the application is carried out with Web Speech API.

The system uses a RAG (Retrieval-Augmented Generation) approach:
1. A language model generates responses to coding questions
2. A FAISS-based RAG system retrieves relevant information from Python documentation
3. The system combines the model's knowledge with retrieved information to provide optimized code that follows best practices

## Technologies Used

### Frontend
- React.js - Web framework for the user interface
- JavaScript/JSX - Programming languages for frontend development
- Vite - Build tool and development server
- Web Speech API - Speech-to-text

### Backend
- Flask - Python web framework for the API
- OpenAI API - For creating and modification of the code

### RAG System
- FAISS (Facebook AI Similarity Search) - For efficient similarity search
- Sentence Transformers - For text embedding


## Installation Instructions

### Prerequisites
- Python 3.8+ with pip
- Node.js and npm
- OpenAI API key

### Setup

1. Clone the repository:
```
git clone <repository-url>
cd <repository-directory>
```

2. Set up the backend:
```
cd back
pip install flask flask-cors faiss-cpu sentence-transformers openai pyPDF2
```

3. Configure environment variables:
   - Create or edit the `.env` file in the `back` directory
   - Add your OpenAI API key: `OPENAI_API_KEY=your_api_key_here`
   - Change the ```docs_dir``` variable on app.py for the document folder location.

4. Set up the frontend:
```
cd front
npm install
```

## Running the Application

1. Start the backend server:
```
cd back
python app.py
```
The server will initialize the RAG system, which may take a few moments.

2. Start the frontend development server:
```
cd front
npm run dev
```

3. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:5173)

## Usage Guide

1. The application presents a chat interface with a conversation history sidebar and a main chat area.

2. Type your coding question or paste code snippets into the text area and press Enter or click "Send".

3. The system will process your request through the language model and RAG system to provide optimized code suggestions.

4. The response will appear in the chat window, showing improved code that follows best practices.

5. You can copy any message content by clicking the "Copy" button below each message.

6. To start a new conversation, click the "New Conversation" button.

7. Your conversation history is saved automatically and can be accessed from the sidebar.

## Team Contributions

### Veeti Salminen

RAG implementation

Improvements to Frontend + Backend

Documentation

### Rasmus Laurila

Backend + Frontend initial versions

Demo videos

Speech to text implementation

Final presentation
