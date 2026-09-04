import chromadb


class VectorMemory:
  """Manages persistent semantic embeddings via ChromaDB."""

  def __init__(self, storage_path: str = "./chroma_db") -> None:
    self.client = chromadb.PersistentClient(path=storage_path)
    self.collection = self.client.get_or_create_collection(
        name="yves_memory"
    )

  def store(self, content: str, category: str = "general") -> str:
    """Stores text into vector memory."""
    count = self.collection.count()
    doc_id = f"mem_{count + 1}"
    self.collection.add(
        documents=[content], metadatas=[{"category": category}], ids=[doc_id]
    )
    return f"Memory saved successfully (ID: {doc_id})."

  def query(self, query_text: str, n_results: int = 3) -> list[str]:
    """Retrieves relevant memory fragments."""
    if self.collection.count() == 0:
      return []
    results = self.collection.query(
        query_texts=[query_text],
        n_results=min(n_results, self.collection.count()),
    )
    return results["documents"][0] if results["documents"] else []


# Instantiate global memory engine
memory_engine = VectorMemory()