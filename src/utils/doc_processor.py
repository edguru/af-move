"""
Document processor for fetching and processing Movement Labs documentation.
"""

import os
from pathlib import Path
from typing import List, Dict
from langchain.text_splitter import MarkdownTextSplitter
from langchain.embeddings import OpenAIEmbeddings
import tempfile
import shutil
import lancedb
import json
import subprocess

class DocProcessor:
    def __init__(self, repo_url: str, branch: str = "main"):
        self.repo_url = repo_url
        self.branch = branch
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = MarkdownTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        
    def _clone_repo(self) -> str:
        """Clone repository to temporary directory."""
        temp_dir = tempfile.mkdtemp()
        try:
            # Use git clone command through subprocess
            result = subprocess.run(
                ["git", "clone", "--depth", "1", self.repo_url, temp_dir],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return temp_dir
            else:
                print(f"Error cloning repository {self.repo_url}: {result.stderr}")
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                return None
        except Exception as e:
            print(f"Error cloning repository {self.repo_url}: {e}")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            return None
        
    def _process_markdown_files(self, repo_dir: str) -> List[Dict]:
        """Process markdown files in repository."""
        documents = []
        
        if not repo_dir:
            return documents
            
        for root, _, files in os.walk(repo_dir):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    try:
                        # Read markdown file directly
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Split into chunks
                        chunks = self.text_splitter.split_text(content)
                        
                        # Add metadata
                        for chunk in chunks:
                            relative_path = os.path.relpath(file_path, repo_dir)
                            metadata = {
                                'source': self.repo_url,
                                'file': relative_path,
                                'repo': self.repo_url.split('/')[-1]
                            }
                            documents.append({
                                'text': chunk,
                                'metadata': metadata
                            })
                            
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
                        
        return documents
        
    def fetch_docs(self) -> List[Dict]:
        """Fetch and process documentation from repository."""
        temp_dir = None
        try:
            # Clone repository
            temp_dir = self._clone_repo()
            if not temp_dir:
                return []
                
            # Process markdown files
            documents = self._process_markdown_files(temp_dir)
            
            # Ensure we have valid documents
            if not documents:
                print(f"No valid documents found in repository: {self.repo_url}")
                return []
                
            # Validate document structure
            valid_documents = []
            for doc in documents:
                if isinstance(doc, dict) and 'text' in doc and 'metadata' in doc:
                    valid_documents.append(doc)
                else:
                    print(f"Invalid document structure found in repository: {self.repo_url}")
                    
            return valid_documents
            
        except Exception as e:
            print(f"Error fetching documents from {self.repo_url}: {e}")
            return []
            
        finally:
            # Cleanup temporary directory
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                
    def save_docs_locally(self, documents: List[Dict], output_dir: str = "data/docs"):
        """Save processed documents locally."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Group documents by repository
        docs_by_repo = {}
        for doc in documents:
            repo = doc['metadata']['repo']
            if repo not in docs_by_repo:
                docs_by_repo[repo] = []
            docs_by_repo[repo].append(doc)
            
        # Save each repository's documents
        for repo, docs in docs_by_repo.items():
            repo_file = output_path / f"{repo}.json"
            with open(repo_file, 'w', encoding='utf-8') as f:
                json.dump(docs, f, indent=2, ensure_ascii=False)
                
    def index_documents(self, documents: List[Dict], vector_db_path: str):
        """Index documents in vector database."""
        # Create or get table
        db = lancedb.connect(vector_db_path)
        
        # Prepare data for indexing
        data = []
        for doc in documents:
            # Get embedding for the document
            embedding = self.embeddings.embed_query(doc['text'])
            
            # Add to data list
            data.append({
                "text": doc['text'],
                "metadata": json.dumps(doc['metadata']),  # Convert metadata to string
                "vector": embedding
            })
            
        try:
            # Try to open existing table
            table = db.open_table("documents")
            # Add new documents
            table.add(data)
        except Exception:
            # Create new table if it doesn't exist
            table = db.create_table(
                "documents",
                data=data,
                mode="overwrite"
            )
            
        print(f"Indexed {len(data)} documents in vector database") 