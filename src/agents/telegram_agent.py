"""
TelegramAgent: A specialized agent for handling Telegram interactions with RAG capabilities.
"""

import os
from typing import List, Dict
from pathlib import Path
import openai
import asyncio
from collections import defaultdict
import json
from datetime import datetime, timedelta
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import LanceDB
from langchain.tools import Tool
from crewai import Agent, Task, Crew
import lancedb

from config.settings import (
    VECTOR_DB_PATH,
    CHAT_CONTEXT_EXPIRY_HOURS,
    MAX_CHAT_HISTORY,
    IMMEDIATE_CONTEXT_SIZE,
    MODEL_NAME,
    MAX_DOCS_PER_QUERY
)

CHAT_CONTEXT_FILE = "data/chat_contexts.json"

class TelegramAgent:
    def __init__(self):
        self.name = "Technical Support Specialist"
        self.role = "Technical documentation expert focused on Movement Labs and Move Language"
        self.goal = "Provide accurate and helpful responses about Movement Labs technology"
        self.backstory = """You are an expert in Movement Labs' technology stack and the Move Language.
        Your role is to help users understand technical concepts and solve problems by providing
        accurate information from the official documentation."""
        
        self.embeddings = OpenAIEmbeddings()
        self.user_locks = defaultdict(asyncio.Lock)
        self.chat_contexts = self._load_chat_contexts()
        
    def _load_chat_contexts(self) -> Dict:
        """Load chat contexts from file."""
        try:
            if os.path.exists(CHAT_CONTEXT_FILE):
                with open(CHAT_CONTEXT_FILE, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, OSError):
            # If file is corrupted or can't be read, start fresh
            if os.path.exists(CHAT_CONTEXT_FILE):
                os.remove(CHAT_CONTEXT_FILE)
        return {}
        
    def _save_chat_contexts(self):
        """Save chat contexts to file."""
        with open(CHAT_CONTEXT_FILE, 'w') as f:
            json.dump(self.chat_contexts, f)
            
    def _clean_expired_contexts(self):
        """Remove expired chat contexts."""
        current_time = datetime.now()
        expired_users = []
        
        for user_id, context in self.chat_contexts.items():
            last_interaction = datetime.fromisoformat(context['last_interaction'])
            if current_time - last_interaction > timedelta(hours=CHAT_CONTEXT_EXPIRY_HOURS):
                expired_users.append(user_id)
                
        for user_id in expired_users:
            del self.chat_contexts[user_id]
            
        if expired_users:
            self._save_chat_contexts()
            
    def _update_chat_context(self, user_id: str, message: str, response: str):
        """Update chat context for a user."""
        if user_id not in self.chat_contexts:
            self.chat_contexts[user_id] = {
                'messages': [],
                'last_interaction': datetime.now().isoformat()
            }
            
        context = self.chat_contexts[user_id]
        context['messages'].append({
            'user': message,
            'bot': response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last N messages for context
        if len(context['messages']) > MAX_CHAT_HISTORY:
            context['messages'] = context['messages'][-MAX_CHAT_HISTORY:]
            
        context['last_interaction'] = datetime.now().isoformat()
        self._save_chat_contexts()
            
    def _get_chat_history(self, user_id: str) -> str:
        """Get formatted chat history for a user."""
        if user_id not in self.chat_contexts:
            return ""
            
        context = self.chat_contexts[user_id]
        history = []
        for msg in context['messages'][-IMMEDIATE_CONTEXT_SIZE:]:
            history.extend([
                f"User: {msg['user']}",
                f"Assistant: {msg['bot']}"
            ])
            
        return "\n".join(history)
        
    def create_search_tool(self) -> Tool:
        """Create document search tool."""
        def search_docs(query: str) -> str:
            """Search documentation for relevant information."""
            try:
                db = lancedb.connect(VECTOR_DB_PATH)
                table = db.open_table("documents")
                
                # Convert query to embedding
                query_embedding = self.embeddings.embed_query(query)
                
                # Search vector store
                results = table.search(query_embedding).select(["text", "metadata"]).limit(MAX_DOCS_PER_QUERY).to_arrow()
                
                if len(results) == 0:
                    return "No relevant documentation found."
                    
                # Format results
                response = []
                for row in results.to_pylist():
                    metadata = json.loads(row['metadata'])
                    response.append(f"From {metadata['file']}:\n{row['text']}")
                    
                return "\n\n".join(response)
            except Exception as e:
                print(f"Error searching documents: {e}")
                return "Error searching documentation. Please try again."
            
        return Tool(
            name="search_movement_docs",
            func=search_docs,
            description="Search Movement Labs documentation for relevant information"
        )
        
    def create_research_agent(self) -> Agent:
        """Create documentation research agent."""
        return Agent(
            role="Movement Labs Documentation Expert",
            goal="Find and provide accurate information from Movement Labs documentation",
            backstory="""You are an expert in Movement Labs' documentation, with deep knowledge
            of Move Language, Movement blockchain, and related technologies. Your role is to search
            and analyze documentation to provide accurate and helpful information.""",
            tools=[self.create_search_tool()],
            allow_delegation=False,
            verbose=True
        )
        
    async def answer_question(self, question: str, user_id: str) -> str:
        """Answer a question using RAG asynchronously with chat context."""
        async with self.user_locks[user_id]:
            # Get chat history
            chat_history = self._get_chat_history(user_id)
            
            # Create research task
            task = Task(
                description=f"""Research and answer the following question:
                
                Chat History:
                {chat_history}
                
                Current Question:
                {question}
                
                Use the search tool to find relevant documentation.
                Provide a clear and accurate answer based on the documentation.
                If information is missing or unclear, say so explicitly.
                Maintain conversation context and reference previous discussion if relevant.""",
                expected_output="A clear and accurate answer to the user's question, based on Movement Labs documentation.",
                agent=self.create_research_agent()
            )
            
            # Create crew with single agent
            crew = Crew(
                agents=[self.create_research_agent()],
                tasks=[task],
                verbose=True
            )
            
            # Execute task in thread pool
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                crew.kickoff
            )
            
            # Convert CrewOutput to string
            response_text = str(response)
            
            # Update chat context
            self._update_chat_context(user_id, question, response_text)
            
            return response_text
        
    async def process_message(self, message: str, user_id: str) -> str:
        """Process an incoming Telegram message asynchronously."""
        # Clean expired contexts periodically
        self._clean_expired_contexts()
        
        # Extract question and generate response
        question = message.strip()
        return await self.answer_question(question, user_id) 