"""
IdeaGeneratorAgent: A specialized agent for generating content ideas related to Movement Labs and Move Language.
"""

import os
import pandas as pd
from datetime import datetime
from typing import List, Dict
from crewai import Agent
from pathlib import Path

class IdeaGeneratorAgent:
    def __init__(self):
        self.name = "Content Strategy Specialist"
        self.role = "Content Strategy Specialist focused on Movement Labs and Move Language"
        self.goal = "Generate engaging and informative content ideas that resonate with the community"
        self.backstory = """You are a seasoned content strategist with deep knowledge of blockchain, 
        particularly Move Language and Movement Labs. You understand the technical aspects while being 
        able to communicate them effectively to different audience segments."""
        
        self.ideas_file = "data/content_ideas.xlsx"
        self._ensure_data_dir()
        
    def _ensure_data_dir(self):
        """Ensure the data directory exists."""
        Path("data").mkdir(exist_ok=True)
        
    def process_trends(self, recent_tweets: List[Dict]) -> List[Dict]:
        """
        Analyze recent tweets and generate new content ideas.
        
        Args:
            recent_tweets: List of recent tweets about Movement Labs/Move
            
        Returns:
            List of new content ideas
        """
        # Create agent with LLM
        agent = Agent(
            name=self.name,
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            allow_delegation=False
        )
        
        # Format tweets for prompt
        tweets_text = "\n".join([f"- {t['text']}" for t in recent_tweets])
        
        # Generate ideas using agent
        response = agent.execute(
            f"""Based on these recent tweets about Movement Labs and Move Language:
            
            {tweets_text}
            
            Generate 5 new content ideas that would resonate with the community.
            Each idea should include:
            - Title
            - Key points to cover
            - Target audience
            - Suggested tone
            
            Format as JSON list."""
        )
        
        # Parse response into structured ideas
        ideas = self._parse_ideas(response)
        
        # Save new ideas
        self.save_ideas(ideas)
        
        return ideas
        
    def load_existing_ideas(self) -> pd.DataFrame:
        """Load existing content ideas from Excel file."""
        try:
            return pd.read_excel(self.ideas_file)
        except FileNotFoundError:
            return pd.DataFrame(columns=[
                'title', 'key_points', 'target_audience', 
                'tone', 'created_at', 'used'
            ])
            
    def save_ideas(self, new_ideas: List[Dict]):
        """Save new ideas to Excel file."""
        existing_df = self.load_existing_ideas()
        
        # Convert new ideas to DataFrame
        new_df = pd.DataFrame(new_ideas)
        new_df['created_at'] = datetime.now()
        new_df['used'] = False
        
        # Append new ideas
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)
        updated_df.to_excel(self.ideas_file, index=False)
        
    def get_unused_idea(self) -> Dict:
        """Get a random unused idea and mark it as used."""
        ideas_df = self.load_existing_ideas()
        
        # Filter unused ideas
        unused = ideas_df[~ideas_df['used']]
        if len(unused) == 0:
            return None
            
        # Select random unused idea
        idea = unused.sample(1).iloc[0]
        
        # Mark as used
        ideas_df.loc[idea.name, 'used'] = True
        ideas_df.to_excel(self.ideas_file, index=False)
        
        return idea.to_dict()
        
    def _parse_ideas(self, llm_response: str) -> List[Dict]:
        """Parse LLM response into structured ideas."""
        # TODO: Implement proper JSON parsing
        # For now return dummy structure
        return [{
            'title': 'Understanding Move Language Smart Contracts',
            'key_points': 'Safety, Performance, Developer Experience',
            'target_audience': 'Web3 Developers',
            'tone': 'Technical but accessible'
        }] 