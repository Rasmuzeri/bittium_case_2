import os
import time
import logging
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class LLMHandler:
    """
    A class to handle LLM requests using the OpenAI API.
    """
    
    def __init__(self, api_key=None, model="gpt-3.5-turbo"):
        """
        Initialize the LLM handler with the OpenAI API key and model.
        
        Args:
            api_key (str, optional): OpenAI API key. Defaults to environment variable OPENAI_API_KEY.
            model (str, optional): OpenAI model to use. Defaults to "gpt-3.5-turbo".
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable or pass to constructor.")
        
        self.model = model
        self.client = OpenAI(api_key=self.api_key)
        logging.info(f"LLM Handler initialized with model: {model}")
    
    def generate_response(self, messages, temperature=0.7):
        """
        Generate a response using the OpenAI API.
        
        Args:
            messages (list): List of message dictionaries with 'role' and 'content' keys.
            temperature (float, optional): Temperature for generation. Defaults to 0.7.
            
        Returns:
            str: The generated response text.
        """
        start_time = time.time()
        request_id = str(int(time.time() * 1000))
        logging.info(f"LLM request {request_id} started")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature
            )
            
            result = response.choices[0].message.content
            
            elapsed_time = time.time() - start_time
            logging.info(f"LLM request {request_id} completed in {elapsed_time:.2f} seconds")
            
            return result
        except Exception as e:
            logging.error(f"Error in LLM request {request_id}: {str(e)}")
            raise

    def generate_code_queries(self, code):
        """
        Generate RAG queries based on a code snippet.
        
        Args:
            code (str): The code to analyze
            
        Returns:
            list: List of query strings for the RAG system
        """
        system_prompt = """You are a code analysis expert tasked with generating efficient search queries.

        CONTEXT:
        - You're given code written by an AI agent
        - These queries will be used to search a knowledge base of coding standards and best practices
        - The search results will be used to improve the code quality

        INSTRUCTIONS:
        1. Analyze the provided code for potential improvement areas (style, efficiency, security, etc.)
        2. Identify the programming language and relevant frameworks used
        3. Generate 3-5 specific, targeted search queries that will find the most relevant best practices
        4. Prioritize queries about modern/recent standards over general guidelines
        5. Include language-specific queries when appropriate

        CRITICAL: Your response MUST be a valid JSON object and nothing else. Do not include markdown formatting, explanations, or any text outside the JSON object.

        The output MUST follow this exact structure:
        {
            "queries": [
                "query1",
                "query2",
                "query3"
            ]
        }

        Make each query specific and actionable - avoid generic terms like "best practices" alone.
        """
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': code}
        ]
        
        response = self.generate_response(messages)
        
        try:
            return json.loads(response)['queries']
        except (json.JSONDecodeError, KeyError):
            logging.error(f"Failed to parse queries from response: {response}")
            return ["python best practices", "coding standards"]
    
    def improve_code_with_rag(self, code, rag_responses):
        """
        Improve code based on RAG responses.
        
        Args:
            code (str): The original code
            rag_responses (list): List of RAG system responses
            
        Returns:
            str: Improved code
        """
        system_prompt = """You are an expert code reviewer and refactoring specialist.

        CONTEXT:
        - You're given: (1) code written by an AI agent, and (2) RAG responses containing modern coding standards
        - Your goal is to improve the code while maintaining its exact functionality
        - The RAG responses are from a trusted knowledge base of best practices

        INSTRUCTIONS:
        1. First understand the complete functionality of the provided code
        2. Carefully analyze each RAG response for relevant guidelines
        3. Apply improvements based on the RAG responses, focusing on:
           - Code readability and maintainability
           - Performance optimizations
           - Security best practices
           - Modern language features
           - Proper error handling
        4. Preserve the original functionality - do not alter the program's behavior

        FORMAT YOUR RESPONSE:
        1. Include a clear explanation of what the code does and how it works
        2. Include the improved code with proper formatting
        3. Explain key concepts or functions used in the code
        4. At the end of your response, include a section titled "REFERENCES" that lists ONLY the file names of the specific RAG documents you used for your improvements
        5. The references should be in a simple bulleted list format with just the file names
        6. Keep the original function/class structure and naming when appropriate

        CRITICAL: Your explanation should be natural and educational. Present the code improvements as recommendations while clearly indicating which concepts from the references informed your decisions.
        """
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': code},
            {'role': 'user', 'content': str(rag_responses)}
        ]
        
        return self.generate_response(messages)
    
    def chat_response(self, user_message):
        """
        Generate a simple chat response to a user message.
        
        Args:
            user_message (str): The user's message
            
        Returns:
            str: The assistant's response
        """
        system_prompt = """You are a knowledgeable coding assistant specialized in providing clear and helpful answers.

        CAPABILITIES:
        - Explain complex programming concepts simply
        - Provide code examples that follow modern best practices
        - Debug issues and suggest solutions
        - Recommend design patterns and architectural approaches
        - Reference reliable documentation when appropriate

        When responding:
        1. Be concise but thorough
        2. Include relevant code examples when helpful
        3. Explain your reasoning
        4. Consider performance, security, and maintainability
        5. Format code properly with appropriate syntax highlighting

        The user is seeking practical coding assistance, so focus on actionable, specific advice.
        """
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_message}
        ]
        
        return self.generate_response(messages) 