import os
from typing import List, Dict, Any
import chromadb
from chromadb.utils import embedding_functions

class InventoryManager:
    """Scans and extracts text content from targeted local workspace files.

    Attributes:
        inventory_path (str): The root folder containing codebase target files.
        supported_extensions (tuple): File types permitted for structural indexing.
    """

    def __init__(self, inventory_path: str) -> None:
        """Initialises the inventory setup with file filters."""
        self.inventory_path: str = inventory_path
        self.supported_extensions: tuple = ('.py', '.js', '.cpp', '.h', '.html', '.css', '.txt')

    def scan_inventory(self) -> List[str]:
        """Finds all relevant engineering files inside the targeted directory tree.

        Returns:
            List[str]: Absolute or relative system file paths to pull text data from.
        """
        files_to_index: List[str] = []
        for root, _, files in os.walk(self.inventory_path):
            for file in files:
                if file.endswith(self.supported_extensions):
                    files_to_index.append(os.path.join(root, file))
        return files_to_index

    def read_and_chunk(self, file_path: str, chunk_size: int = 1000) -> List[str]:
        """Reads code files and splits them into smaller text strings for vector storage.

        Args:
            file_path (str): The exact file address to extract content from.
            chunk_size (int): Fixed maximum character limit per slice. Defaults to 1000.

        Returns:
            List[str]: Text substrings broken by character indices.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content: str = f.read()
                chunks: List[str] = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
                return chunks
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []


class MemoryVault:
    def __init__(self, memory_path: str) -> None:
        self.client: chromadb.PersistentClient = chromadb.PersistentClient(path=memory_path)
        self.emb_fn = embedding_functions.DefaultEmbeddingFunction()
        
        # Primary codebase inventory storage
        self.collection = self.client.get_or_create_collection(
            name="yves_inventory", 
            embedding_function=self.emb_fn
        )
        
        # NEW: Dedicated secondary table for routing logic
        self.router_collection = self.client.get_or_create_collection(
            name="yves_intent_router",
            embedding_function=self.emb_fn
        )
        
        # Automatically calibrate routing references on startup
        self._calibrate_router()

    def _calibrate_router(self) -> None:
        """Seeds the intent collection with anchoring reference vectors."""
        # Clear existing entries to prevent duplication errors on re-run
        try:
            existing = self.router_collection.get()
            if existing and existing['ids']:
                self.router_collection.delete(ids=existing['ids'])
        except Exception:
            pass

        # Reference anchor points mapping directly to operational intent
        technical_examples = [
            "optimise this function logic", "debug this compilation error",
            "refactor the class architecture", "find the security bug here",
            "write a script to parse data", "review this database schema",
            "why is this execution loop throwing an exception", "analyse code performance"
        ]
        
        casual_examples = [
            "hello good morning", "how are you doing today",
            "tell me a witty story", "what do you think about life",
            "who created your identity", "let's have a casual chat",
            "tell me a joke", "what is the capital city of France"
        ]

        ids = [f"tech_{i}" for i in range(len(technical_examples))] + [f"casual_{i}" for i in range(len(casual_examples))]
        documents = technical_examples + casual_examples
        metadatas = [{"category": "technical"} for _ in technical_examples] + [{"category": "casual"} for _ in casual_examples]

        self.router_collection.add(documents=documents, metadatas=metadatas, ids=ids)

    def predict_intent(self, query: str) -> str:
        """Queries the vector space to classify text category by proximity."""
        results = self.router_collection.query(query_texts=[query], n_results=3)
        if not results or not results['metadatas'] or len(results['metadatas'][0]) == 0:
            return "casual"
            
        # Count category votes from the top 3 closest vector matches
        votes = [meta['category'] for meta in results['metadatas'][0]]
        return max(set(votes), key=votes.count)


class YvesRetriever:
    """Orchestrates syncing the file scanner and database layers.

    Attributes:
        manager (InventoryManager): File scanner sub-system instance.
        vault (MemoryVault): Vector data warehouse storage connection.
    """

    def __init__(self, inventory_dir: str, memory_dir: str) -> None:
        """Initialises the sync wrapper with folder targets.

        Args:
            inventory_dir (str): Folder address holding target codebase items.
            memory_dir (str): Folder location designated to save ChromaDB files.
        """
        self.manager: InventoryManager = InventoryManager(inventory_dir)
        self.vault: MemoryVault = MemoryVault(memory_dir)

    def sync_inventory(self) -> None:
        """Scans the local source directory and registers all missing code files into the database."""
        files: List[str] = self.manager.scan_inventory()
        if not files:
            print("Scan found no files. Standing down.")
            return

        all_chunks: List[str] = []
        all_metadatas: List[Dict[str, str]] = []
        all_ids: List[str] = []

        for file_path in files:
            chunks: List[str] = self.manager.read_and_chunk(file_path)
            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                all_metadatas.append({"source": os.path.basename(file_path)})
                all_ids.append(f"{os.path.basename(file_path)}_chunk_{i}")

        if all_chunks:
            self.vault.store_chunks(all_chunks, all_metadatas, all_ids)
            print(f"Sync complete. {len(files)} files indexed into memory.")