import os

class DynamicSkiller:
    """Tools to handle the creation and proposition of new skills dynamically."""

    @staticmethod
    def propose_new_skill(llm_backend, skill_description, discord_client=None, user_id=None):
        """
        Drafts a new python file for a missing skill based on description/context.
        Wait... the agent shouldn't block the event loop for user input here.
        Instead, the agent returns a special control string that the Discord C2 interprets.
        """
        # We don't implement the discord interaction here; we just draft the class 
        # and return it as a structured payload so the Agent can pass it up to C2.
        
        prompt = f"""
        Write a Python class with static methods to handle the following missing capability for my Kali Linux Swarm:
        {skill_description}
        
        Requirements:
        1. Always use the `subprocess.Popen` pattern with `"bash", "-c"` and timeouts.
        2. Name the class descriptively ending in 'Tools'.
        3. Do NOT provide any explanations, just the raw Python code. Do not include Markdown blocks like ```python, JUST THE CODE.
        """
        try:
            draft_code = llm_backend.generate(prompt=prompt, system="You are an expert Python developer for Kali Linux tools. Output ONLY valid Python.", temperature=0.2)
            if draft_code:
                # Strip markdown blocks if they accidentally included them
                draft_code = draft_code.replace("```python", "").replace("```", "").strip()
                return f"PROPOSED_SKILL_PAYLOAD\n{draft_code}"
            return "[Error] Failed to generate skill draft."
        except Exception as e:
            return f"[Error] Skiller Exception: {str(e)}"
