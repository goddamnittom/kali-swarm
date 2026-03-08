import subprocess

class GeminiTools:
    """Tools for interacting with the Gemini CLI (gemini-cli)."""

    @staticmethod
    def query_gemini(prompt, timeout=120):
        """
        Sends a query to the Gemini CLI.
        This is useful for outsourcing complex reasoning, translation, or 
        tasks that the small local model (dolphin-phi) struggles with.
        """
        # Note: assumes gemini-cli is installed and configured in the environment
        # e.g., 'gemini "your prompt here"'
        # We need to escape the prompt properly to avoid bash injection, or use list execution
        
        try:
            # We use list execution to avoid shell injection with the prompt
            process = subprocess.Popen(
                ["gemini", prompt],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(timeout=timeout)
            
            if process.returncode != 0:
                return f"[Gemini CLI Error] Return {process.returncode}:\n{stderr.strip()}"
            
            return stdout.strip() if stdout.strip() else "[Success] No output from Gemini."
            
        except subprocess.TimeoutExpired:
            process.kill()
            return f"[Error] Gemini CLI timed out after {timeout} seconds."
        except FileNotFoundError:
            return "[Error] `gemini` command not found. Is gemini-cli installed and in PATH?"
        except Exception as e:
            return f"[Error] Execution failed: {str(e)}"
