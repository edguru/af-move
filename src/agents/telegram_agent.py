"""
TelegramAgent: A specialized agent for handling Telegram interactions with RAG capabilities.
"""

import os
import lancedb
from typing import List, Dict
from crewai import Agent
from pathlib import Path
import openai

VECTOR_DB_PATH = "data/vector_db"

class TelegramAgent:
    def __init__(self):
        self.name = "Technical Support Specialist"
        self.role = "Technical documentation expert focused on Movement Labs and Move Language"
        self.goal = "Provide accurate and helpful responses about Movement Labs technology"
        self.backstory = """You are an expert in Movement Labs' technology stack and the Move Language.
        Your role is to help users understand technical concepts and solve problems by providing
        accurate information from the official documentation."""
        
        self._init_vector_db()
        
    def _init_vector_db(self):
        """Initialize the vector database."""
        Path(VECTOR_DB_PATH).mkdir(parents=True, exist_ok=True)
        self.db = lancedb.connect(VECTOR_DB_PATH)
        
        # Create table if it doesn't exist
        if "documents" not in self.db.table_names():
            self.db.create_table(
                "documents",
                data=[{
                    "text": "Movement Labs documentation",
                    "embedding": [0.0] * 1536,  # OpenAI embedding dimension
                    "source": "init"
                }],
                mode="overwrite"
            )
            
    def _get_embedding(self, text: str) -> List[float]:
        """Get embeddings for text using OpenAI's API."""
        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
        
    def add_documents(self, documents: List[Dict[str, str]]):
        """
        Add documents to the vector database.
        
        Args:
            documents: List of dicts with 'text' and 'source' keys
        """
        # Get embeddings for all documents
        for doc in documents:
            doc['embedding'] = self._get_embedding(doc['text'])
            
        # Add to database
        table = self.db.open_table("documents")
        table.add(documents)
        
    def search_documents(self, query: str, k: int = 3) -> List[Dict]:
        """
        Search for relevant documents using vector similarity.
        
        Args:
            query: The search query
            k: Number of results to return
            
        Returns:
            List of relevant documents
        """
        query_embedding = self._get_embedding(query)
        table = self.db.open_table("documents")
        
        results = table.search(query_embedding).limit(k).to_list()
        return results
        
    def answer_question(self, question: str) -> str:
        """
        Answer a question using RAG.
        
        Args:
            question: The user's question
            
        Returns:
            Generated response
        """
        # Create agent
        agent = Agent(
            name=self.name,
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            allow_delegation=False
        )
        
        # Get relevant documents
        docs = self.search_documents(question)
        context = "\n\n".join([d['text'] for d in docs])
        
        # Generate response
        response = agent.execute(
            f"""Using the following documentation excerpts as context:
            
            {context}
            
            Answer this question accurately and helpfully:
            {question}
            
            If the context doesn't contain enough information to answer accurately,
            say so rather than making assumptions."""
        )
        
        return response
        
    def process_message(self, message: str) -> str:
        """
        Process an incoming Telegram message.
        
        Args:
            message: The user's message
            
        Returns:
            Response to send back
        """
        # Extract question from message
        # TODO: Add more sophisticated message processing
        question = message.strip()
        
        # Generate response
        response = self.answer_question(question)
        
        return response 