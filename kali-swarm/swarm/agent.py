import re
import time

class Agent:
    def __init__(self, name, role, tools, llm_backend, memory=None):
        self.name = name
        self.role = role
        self.tools = tools  # Dictionary mapping tool_name to callable
        self.llm = llm_backend
        self.memory = memory
        self.max_iterations = 8
        self.history = []

    def execute_task(self, task):
        print(f"\n[+] Agent {self.name} starting task: {task}\n")
        self.history.append({"role": "user", "content": task})
        
        # Pull relevant memories
        past_reflections = ""
        if self.memory:
            past_memories = self.memory.search_similar_tasks(task)
            if past_memories:
                past_reflections = "PAST REFLECTIONS (LEARNED BEHAVIORS):\n"
                for m in past_memories:
                    past_reflections += f"- Previous Task: {m['task']}\n"
                    past_reflections += f"  Outcome: {'Success' if m['success'] else 'Failure'}\n"
                    past_reflections += f"  Reflection: {m['reflection']}\n\n"

        system_prompt = self._build_system_prompt(past_reflections)
        
        prompt_context = task
        
        for iteration in range(self.max_iterations):
            # Format the conversation history for the context
            full_prompt = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in self.history])
            
            # Generate LLM response
            response = self.llm.generate(
                prompt=full_prompt,
                system=system_prompt,
                temperature=0.3
            )
            
            if not response:
                print(f"[!] {self.name} encountered LLM generation error.")
                break

            self.history.append({"role": "assistant", "content": response})
            print(f"-- {self.name} Output --\n{response}\n----------------------")

            # Check if finished
            if "FINAL_ANSWER" in response:
                print(f"[+] Task completed by {self.name}.")
                return response

            # Parse action
            action_match = re.search(r"ACTION:\s*([a-zA-Z_]+)(?:\s+ARGS:\s*(.+))?", response)
            if action_match:
                action_name = action_match.group(1).strip()
                args = action_match.group(2).strip() if action_match.group(2) else ""
                
                print(f"[*] Executing Action: {action_name} | Args: {args}")
                
                if action_name in self.tools:
                    # Execute
                    try:
                        observation = self.tools[action_name](args)
                        # Truncate observation to prevent context explosion on Pi 5
                        if len(observation) > 2000:
                            observation = observation[:2000] + "...[TRUNCATED]"
                        
                        obs_str = f"OBSERVATION: {observation}"
                        self.history.append({"role": "user", "content": obs_str})
                        print(f"[*] Observation: {observation[:100]}...")
                    except Exception as e:
                        err_str = f"OBSERVATION [ERROR]: {e}"
                        self.history.append({"role": "user", "content": err_str})
                else:
                    self.history.append({"role": "user", "content": f"OBSERVATION [ERROR]: Tool '{action_name}' not found."})
            else:
                self.history.append({"role": "user", "content": "OBSERVATION [ERROR]: No valid ACTION found. You must either provide an ACTION or a FINAL_ANSWER."})

            time.sleep(1) # Prevent looping too fast

        print(f"[-] Agent {self.name} reached max iterations.")
        return "[Failure] Max iterations reached without a FINAL_ANSWER."

    def reflect_on_execution(self, task, final_output):
        """Analyze the execution and store reflection in memory."""
        print(f"\n[*] Reflecting on execution of task: {task[:50]}...")
        if not self.memory:
            return
            
        reflection_prompt = f"""
        Review the following execution log and analyze why it succeeded or failed.
        Identify any poor tool usage, hallucinations, or successful tactics.
        Provide a concise piece of advice (a reflection) for future attempts.
        
        Task: {task}
        Final Output: {final_output}
        """
        
        reflection = self.llm.generate(
            prompt=reflection_prompt,
            system="You are a reflection agent meant to summarize AI agent performance.",
            temperature=0.5
        )
        
        success = "[Failure]" not in final_output
        self.memory.add_memory(task, self.history, reflection, success)
        print(f"[+] Reflection saved: {reflection[:100]}...\n")

    def _build_system_prompt(self, past_reflections):
        tool_desc = ""
        for name, func in self.tools.items():
            doc = getattr(func, '__doc__', 'No description.')
            tool_desc += f"- {name}: {doc}\n"
            
        return f"""You are {self.name}, an AI agent running on a Raspberry Pi 5 Kali Linux system.
Role: {self.role}

{past_reflections}

AVAILABLE TOOLS:
{tool_desc}

INSTRUCTIONS:
- You operate in a loop: THOUGHT -> ACTION -> OBSERVATION.
- First, write a THOUGHT explaining what you are going to do.
- Then, write an ACTION to test. Use this EXACT format:
ACTION: tool_name ARGS: argument string
- Wait for the OBSERVATION from the user.
- Repeat until you have the final answer.
- When finished, write:
FINAL_ANSWER: your comprehensive report or conclusion here.

Constraints: Only execute one ACTION step at a time. Do NOT simulate the OBSERVATION.
"""
