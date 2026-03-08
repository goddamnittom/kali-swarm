import subprocess

class VulnerabilityTools:
    """Tools for running nuclei automated vulnerability scans."""

    @staticmethod
    def _run_cmd(cmd, timeout=300):
        try:
            process = subprocess.Popen(
                ["bash", "-c", cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(timeout=timeout)
            if process.returncode != 0 and "No results found" not in stdout:
                # nuclei sometimes returns non-zero depending on what it found or missed, 
                # but we usually want the stdout anyway.
                pass
            return stdout.strip() if stdout.strip() else "[Nuclei] Scan completed with no actionable results."
        except subprocess.TimeoutExpired:
            return f"[Error] Command timed out after {timeout} seconds."
        except Exception as e:
            return f"[Error] Execution failed: {str(e)}"

    @staticmethod
    def run_nuclei(target, templates_dir="", severity="critical,high,medium"):
        """
        Run a nuclei scan against a target URL or IP.
        severity: comma-separated list of severities to filter for.
        """
        cmd = f"nuclei -u {target} -s {severity}"
        if templates_dir:
            cmd += f" -t {templates_dir}"
        
        # Adding jsonl output to a temp file could be better for parsing, 
        # but for Swarm LLM we want stdout summary.
        return VulnerabilityTools._run_cmd(cmd, timeout=600)
