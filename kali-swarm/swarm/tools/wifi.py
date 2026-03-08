import subprocess
import shlex
import time

class WiFiTools:
    """Tools for autonomous WiFi auditing using aircrack-ng and wifite. Requires root."""

    @staticmethod
    def _run_cmd(cmd, timeout=60):
        try:
            process = subprocess.Popen(
                ["bash", "-c", cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                if process.returncode != 0:
                    return f"[Error] Return {process.returncode}:\n{stderr.strip()}"
                return stdout.strip() if stdout.strip() else "[Success] Command executed silently."
            except subprocess.TimeoutExpired:
                process.kill()
                return f"[Error] Command timed out after {timeout} seconds."
        except Exception as e:
            return f"[Error] Execution failed: {str(e)}"

    @staticmethod
    def get_interfaces():
        """List wireless interfaces using iwconfig."""
        return WiFiTools._run_cmd("iwconfig 2>/dev/null | grep -o '^[[:alnum:]]*'")

    @staticmethod
    def enable_monitor_mode(interface):
        """Enable monitor mode on a specific interface using airmon-ng."""
        result = WiFiTools._run_cmd(f"sudo airmon-ng start {interface}")
        return result

    @staticmethod
    def disable_monitor_mode(interface):
        """Disable monitor mode (e.g., wlan0mon -> wlan0)."""
        result = WiFiTools._run_cmd(f"sudo airmon-ng stop {interface}")
        return result

    @staticmethod
    def start_wifite_auto(interface, target_bssid=""):
        """
        Run Wifite in automated mode.
        If target_bssid is provided, it attempts to target only that AP.
        Otherwise, it attacks all targets automatically. 
        Note: This is a synchronous blocking call with a high timeout.
        """
        cmd = f"sudo wifite -i {interface} --kill --dict /usr/share/wordlists/rockyou.txt"
        if target_bssid:
            cmd += f" --bssid {target_bssid}"
        
        # Wifite can take a very long time, set timeout appropriately.
        # We add --pcap to save captures just in case.
        return WiFiTools._run_cmd(cmd, timeout=300)

    @staticmethod
    def list_captured_handshakes(directory="hs/"):
        """List captured handshakes saved by wifite."""
        return WiFiTools._run_cmd(f"ls -la {directory}*.cap 2>/dev/null || echo 'No captures found.'")

    @staticmethod
    def deauth_target(interface, bssid, client_mac="FF:FF:FF:FF:FF:FF", amount=10):
        """
        Send deauthentication packets to disconnect a client from an access point.
        If client_mac is not provided (or is broadcast), it attempts to deauth all clients on that BSSID.
        Requires the interface to be in monitor mode.
        """
        # aireplay-ng -0 <amount> -a <bssid> -c <client_mac> <interface>
        cmd = f"sudo aireplay-ng -0 {amount} -a {bssid} -c {client_mac} {interface}"
        return WiFiTools._run_cmd(cmd, timeout=30)

