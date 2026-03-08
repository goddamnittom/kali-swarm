import subprocess
import shlex

class BluetoothTools:
    """Tools for autonomous Bluetooth auditing. Requires hciconfig, hcitool, l2ping."""

    @staticmethod
    def _run_cmd(cmd, timeout=30):
        try:
            process = subprocess.Popen(
                ["bash", "-c", cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(timeout=timeout)
            if process.returncode != 0:
                return f"[Error] Return {process.returncode}:\n{stderr.strip()}"
            return stdout.strip() if stdout.strip() else "[Success] Command completed."
        except subprocess.TimeoutExpired:
            return f"[Error] Command timed out after {timeout} seconds."
        except Exception as e:
            return f"[Error] Execution failed: {str(e)}"

    @staticmethod
    def get_interfaces():
        """List Bluetooth interfaces using hciconfig."""
        return BluetoothTools._run_cmd("hciconfig -a")

    @staticmethod
    def enable_interface(interface="hci0"):
        """Enable a Bluetooth interface."""
        return BluetoothTools._run_cmd(f"sudo hciconfig {interface} up")

    @staticmethod
    def scan_classic(interface="hci0"):
        """Scan for classic Bluetooth devices."""
        return BluetoothTools._run_cmd(f"sudo hcitool -i {interface} scan", timeout=20)

    @staticmethod
    def scan_le(interface="hci0"):
        """Scan for Bluetooth Low Energy (BLE) devices."""
        # lescan normally runs indefinitely, so we use timeout command inside bash
        return BluetoothTools._run_cmd(f"sudo timeout 15s hcitool -i {interface} lescan", timeout=20)

    @staticmethod
    def l2ping_flood(mac_address, interface="hci0", packets=1000):
        """Flood a classic Bluetooth device with l2ping requests (DoS)."""
        return BluetoothTools._run_cmd(f"sudo l2ping -i {interface} -c {packets} -f {mac_address}", timeout=60)
