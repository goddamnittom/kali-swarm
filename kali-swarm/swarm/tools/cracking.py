import subprocess

class HashcatTools:
    """Tools for automated hash cracking using Hashcat on Pi5 CPU."""

    @staticmethod
    def _run_cmd(cmd, timeout=3600): # 1 hour default timeout for cracking
        try:
            # We must use bash to execute hashcat
            process = subprocess.Popen(
                ["bash", "-c", cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(timeout=timeout)
            if process.returncode not in [0, 1]: 
                # hashcat returns 0 if cracked, 1 if exhausted/not found
                return f"[Error] Return {process.returncode}:\n{stderr.strip()}"
            return stdout.strip() if stdout.strip() else "[Hashcat] Finished."
        except subprocess.TimeoutExpired:
            process.kill()
            return f"[Status] Hashcat process timed out after {timeout} seconds. Check results or resume later."
        except Exception as e:
            return f"[Error] Execution failed: {str(e)}"

    @staticmethod
    def crack_wpa(capture_file, dict_file="/usr/share/wordlists/rockyou.txt"):
        """
        Run hashcat against a captured WPA handshake.
        If it's a .cap, we need it converted to .hc22000 first, but assuming Wifite already provides that or similar.
        If it's .hc22000 format directly:
        """
        if capture_file.endswith(".cap"):
            # Simplistic approach: tell the agent to convert it first or use aircrack directly
            return "[Agent Note] Please use `aircrack-ng` for raw .cap files or convert to .hc22000 for hashcat."

        # -m 22000 = WPA-PBKDF2-PMKID+EAPOL
        # -a 0 = straight dictionary
        # -O = Optimized kernel for Pi CPU
        cmd = f"hashcat -m 22000 -a 0 -O {capture_file} {dict_file}"
        return HashcatTools._run_cmd(cmd)

    @staticmethod
    def show_cracked(capture_file):
        """Show cracked passwords for a given capture/hash file."""
        cmd = f"hashcat -m 22000 {capture_file} --show"
        return HashcatTools._run_cmd(cmd, timeout=10)
