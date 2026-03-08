import json
import urllib.request
import urllib.error

class OllamaBackend:
    def __init__(self, host="http://localhost:11434", model="phi3:mini", max_retries=3):
        self.host = host
        self.model = model
        self.max_retries = max_retries

    def check_connection(self):
        try:
            req = urllib.request.Request(f"{self.host}/api/version", method="GET")
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status == 200
        except Exception:
            return False

    def generate(self, prompt, system="", json_format=False, temperature=0.7):
        url = f"{self.host}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_ctx": 4096  # Limit sequence length for Raspberry Pi RAM constraints
            }
        }
        
        if json_format:
            payload["format"] = "json"

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        
        for attempt in range(self.max_retries):
            try:
                with urllib.request.urlopen(req, timeout=120) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    return result.get("response", "")
            except Exception as e:
                print(f"[Ollama Error] Attempt {attempt+1}/{self.max_retries} failed: {e}")
                if attempt == self.max_retries - 1:
                    return None
        return None

    def get_embeddings(self, text):
        url = f"{self.host}/api/embeddings"
        payload = {
            "model": self.model,
            "prompt": text
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get("embedding", [])
        except Exception as e:
            print(f"[Ollama Embeddings Error] Failed to generate embedding: {e}")
            return []
