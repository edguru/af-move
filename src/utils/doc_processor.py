"""
DocProcessor: Utility class for fetching and processing documentation from GitHub repositories.
"""

import os
import requests
import base64
from typing import List, Dict
from pathlib import Path

class DocProcessor:
    def __init__(self, repo_url: str):
        """
        Initialize with a GitHub repository URL.
        
        Args:
            repo_url: Full URL to the GitHub repository
        """
        self.api_url = self._convert_to_api_url(repo_url)
        
    def _convert_to_api_url(self, repo_url: str) -> str:
        """Convert GitHub URL to API URL."""
        # Example: https://github.com/owner/repo -> https://api.github.com/repos/owner/repo
        parts = repo_url.split('github.com/')
        if len(parts) != 2:
            raise ValueError("Invalid GitHub URL")
            
        return f"https://api.github.com/repos/{parts[1]}"
        
    def fetch_docs(self, path: str = "docs/") -> List[Dict[str, str]]:
        """
        Fetch documentation files from a specified path in the repository.
        
        Args:
            path: Path to documentation directory
            
        Returns:
            List of dicts with 'text' and 'source' keys
        """
        documents = []
        
        # Get contents of path
        response = requests.get(f"{self.api_url}/contents/{path}")
        if response.status_code != 200:
            raise Exception(f"Failed to fetch contents: {response.text}")
            
        contents = response.json()
        
        # Process each item
        for item in contents:
            if item['type'] == 'file' and self._is_doc_file(item['name']):
                content = self._fetch_file_content(item['download_url'])
                documents.append({
                    'text': content,
                    'source': f"{path}/{item['name']}"
                })
            elif item['type'] == 'dir':
                # Recursively process subdirectories
                sub_docs = self.fetch_docs(f"{path}/{item['name']}")
                documents.extend(sub_docs)
                
        return documents
        
    def _is_doc_file(self, filename: str) -> bool:
        """Check if a file is a documentation file."""
        doc_extensions = {'.md', '.mdx', '.txt', '.rst'}
        return any(filename.endswith(ext) for ext in doc_extensions)
        
    def _fetch_file_content(self, url: str) -> str:
        """Fetch and decode file content."""
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch file: {response.text}")
            
        return response.text
        
    def save_docs_locally(self, documents: List[Dict[str, str]], output_dir: str = "data/docs"):
        """
        Save fetched documents to local directory.
        
        Args:
            documents: List of document dicts
            output_dir: Directory to save files
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        for doc in documents:
            # Create safe filename from source
            filename = doc['source'].replace('/', '_')
            filepath = os.path.join(output_dir, filename)
            
            # Save content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(doc['text'])
                
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to split
            chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            # Find end of chunk
            end = start + chunk_size
            
            # Adjust end to not split words
            if end < len(text):
                # Find next space after chunk_size
                while end < len(text) and not text[end].isspace():
                    end += 1
                    
            chunk = text[start:end]
            chunks.append(chunk)
            
            # Move start position for next chunk
            start = end - overlap
            
            # Adjust start to not split words
            while start < len(text) and not text[start].isspace():
                start += 1
                
        return chunks 