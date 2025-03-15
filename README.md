# AI-Powered Coding Assistant

## Project Overview
This project is an AI-powered coding assistant that helps developers improve their code by providing suggestions based on best practices and coding standards. The application consists of a web-based chat interface where users can input code or coding questions, and the system responds with optimized code suggestions.

The system uses a multi-agent approach:
1. A primary AI agent generates initial code responses
2. A second agent creates relevant queries about coding standards and best practices
3. A RAG (Retrieval-Augmented Generation) system retrieves information from Python documentation
4. A third agent combines the initial code with the retrieved information to provide optimized code that follows best practices

## Technologies Used

### Frontend
- React.js - Web framework for the user interface
- JavaScript/JSX - Programming languages for frontend development
- Speech Recognition API - For voice input capability
- LocalStorage - For persisting conversations and user preferences

### Backend
- Flask - Python web framework for the API
- Flask-CORS - Cross-Origin Resource Sharing support
- Hugging Face Transformers - For AI model integration
- HuggingFaceTB/SmolLM-135M-Instruct - Small language model for code generation
- PyTorch - Deep learning framework

### RAG System
- FAISS (Facebook AI Similarity Search) - For efficient similarity search
- Sentence Transformers - For text embedding (all-MiniLM-L12-v2 model)
- Python 3.13 Documentation - Dataset for code standards and best practices

## Installation Instructions

### Prerequisites
- Python 3.8+ with pip
- Node.js and npm
- Git

### Setup

1. Clone the repository:
```
git clone <repository-url>
cd <repository-directory>
```

2. Set up the backend:
```
cd back
pip install flask flask-cors transformers torch faiss-cpu sentence-transformers
```

3. Set up the frontend:
```
cd front
npm install
```

4. Prepare the Python documentation (if not already included):
   - The system expects Python 3.13 documentation in text format in the `python-3.13-docs-text` directory
   - If not present, the system will look for it at `E:/bittium_case_2/python-3.13-docs-text/`

## Running the Application

1. Start the backend server:
```
cd back
python app.py
```
The server will initialize the RAG system and load the AI model, which may take a few moments.

2. Start the frontend development server:
```
cd front
npm run dev
```

3. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:5173)

## Usage Guide

1. The application presents a chat interface with a conversation history sidebar and a main chat area.

2. Type your coding question or paste code snippets into the text area and press Enter or click "Send".

3. Alternatively, click the microphone button to use voice input for your query.

4. The system will process your request through multiple AI agents and the RAG system to provide optimized code suggestions.

5. The response will appear in the chat window, showing improved code that follows best practices.

6. You can copy any message content by clicking the "Copy" button below each message.

7. To start a new conversation, click the "New Conversation" button.

8. Your conversation history is saved automatically and can be accessed from the sidebar.

## Features

- **Conversation Management**: 
  - Multiple conversations stored in a sidebar
  - Ability to switch between different conversations
  - Delete individual conversations
  - Automatic naming of conversations based on first message

- **Chat Interface**: 
  - Clean, modern chat interface with user messages aligned to the right and AI responses to the left
  - Copy functionality for each message
  - Visual feedback when copying message content

- **Theme Support**:
  - Toggle between light and dark modes
  - Theme preference is remembered between sessions
  - Smooth transition animations between themes

- **Voice Input**: 
  - Speak your queries using the microphone button
  - Visual feedback during voice recording

- **Responsive Design**: 
  - Collapsible sidebar for better mobile experience
  - Works well on various screen sizes
  - Adaptive layout based on screen size

- **Persistence**:
  - All conversations are saved to localStorage
  - Theme preference is remembered
  - Active conversation is restored on page reload

## Project Architecture

The system uses a three-agent architecture:
- Agent 1: Generates initial code responses based on user queries
- Agent 2: Creates specific queries to search for relevant coding standards
- RAG System: Retrieves information from Python documentation based on these queries
- Agent 3: Combines the initial code with retrieved information to produce optimized code

This approach ensures that the code suggestions not only solve the user's problem but also adhere to the latest coding standards and best practices.

## Frontend Architecture

The frontend is built with React and uses a component-based architecture:

- **App Component**: The main component that manages state and renders the UI
- **Conversation Management**: Handles creating, switching between, and deleting conversations
- **Theme Management**: Provides light and dark mode with smooth transitions
- **Message Display**: Renders user and AI messages with appropriate styling
- **Input Handling**: Manages text input, voice input, and message sending
- **Persistence Layer**: Saves and loads data from localStorage

The application uses React's useState and useEffect hooks for state management and side effects, providing a responsive and interactive user experience.
