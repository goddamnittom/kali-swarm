import json
import os
import math

class LightweightMemory:
    """
    To keep RAM usage low on Raspberry Pi 5, this memory system uses a simple 
    JSON file combined with cosine similarity of embeddings fetched from Ollama 
    (or basic kw matching if embeddings fail).
    """
    def __init__(self, db_path="swarm_memory.json", llm_backend=None):
        self.db_path = db_path
        self.llm_backend = llm_backend
        self.memory = []
        self._load_db()

    def _load_db(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, "r", encoding="utf-8") as f:
                try:
                    self.memory = json.load(f)
                except:
                    self.memory = []

    def _save_db(self):
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=4)

    def add_memory(self, task, actions, reflection_feedback, success):
        # Generate an embedding for the task text if possible
        embedding = []
        if self.llm_backend:
            embedding = self.llm_backend.get_embeddings(task)

        entry = {
            "task": task,
            "actions": actions,
            "reflection": reflection_feedback,
            "success": success,
            "embedding": embedding
        }
        self.memory.append(entry)
        self._save_db()
        return "[Success] Memory saved for future reflection."

    def cosine_similarity(self, v1, v2):
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        norm_a = math.sqrt(sum(a * a for a in v1))
        norm_b = math.sqrt(sum(b * b for b in v2))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def search_similar_tasks(self, query_task, top_k=3):
        if not self.memory:
            return []

        query_embedding = []
        if self.llm_backend:
            query_embedding = self.llm_backend.get_embeddings(query_task)

        results = []
        for mem in self.memory:
            # Score based on embedding similarity if available
            score = 0.0
            if query_embedding and mem.get("embedding"):
                score = self.cosine_similarity(query_embedding, mem["embedding"])
            else:
                # Fallback to simple sub-string matching
                task_str = str(mem.get("task", ""))
                score = float(any(word.lower() in task_str.lower() for word in str(query_task).split()))

            results.append((score, mem))
        
        # Sort by best score descending
        results.sort(key=lambda x: x[0], reverse=True)
        # Return context omitting the heavy embedding vector
        top_results = []
        for i, (score, data) in enumerate(results):
            if i >= top_k:
                break
            if score > 0.6: # similarity threshold
                top_results.append({
                    "task": data.get("task", ""),
                    "reflection": data.get("reflection", ""),
                    "success": data.get("success", False),
                    "similarity": round(score, 2)
                })

        return top_results
