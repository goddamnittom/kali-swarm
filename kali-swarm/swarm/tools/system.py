import subprocess
import shlex
import time
import os

class SystemTools:
    @staticmethod
    def execute_command(command, timeout=30):
        """Execute a general shell command safely."""
        print(f"[System] Executing: {command}")
        try:
            # We use shlex to parse command into a list safely (though it's still running raw)
            args = shlex.split(command)
            # We don't use shell=True to avoid injection unless absolutely necessary.
            # But the agent might pass pipes or redirections. If it does, we'll try to execute it via bash.
            
            process = subprocess.Popen(
                ["bash", "-c", command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            start_time = time.time()
            stdout, stderr = "", ""
            
            # Non-blocking read loop with timeout
            while True:
                if process.poll() is not None:
                    break
                if time.time() - start_time > timeout:
                    process.kill()
                    return "[Error] Command timed out after {} seconds".format(timeout)
                time.sleep(0.1)

            stdout, stderr = process.communicate()
            
            out = stdout.strip()
            err = stderr.strip()
            
            if process.returncode != 0:
                return f"[Status: Exit {process.returncode}]\n[Stdout]\n{out}\n[Stderr]\n{err}"
            return out if out else (err if err else "[Success] No output.")
            
        except Exception as e:
            return f"[Error] Command execution failed: {e}"

    @staticmethod
    def read_file(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                return content[:8000] # Truncate to prevent context overload
        except Exception as e:
            return f"[Error] Reading file: {e}"

    @staticmethod
    def get_tool_list():
        return {
            "execute_command": "Run a bash command on Kali. Args: command (str), timeout (int).",
            "read_file": "Read contents of a file on the file system. Args: filepath (str)."
        }
