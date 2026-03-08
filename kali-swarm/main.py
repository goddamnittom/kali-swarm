import argparse
from llm_backend import OllamaBackend
from swarm.memory.vector_db import LightweightMemory
from swarm.agent import Agent
from swarm.tools.system import SystemTools
from swarm.tools.ui import UITools
from swarm.tools.osint_skill_tree import OSINTSkills
from swarm.tools.wifi import WiFiTools
from swarm.tools.bluetooth import BluetoothTools
from swarm.tools.evil_twin import EvilTwinTools
from swarm.tools.vuln_scanner import VulnerabilityTools
from swarm.tools.cracking import HashcatTools
from swarm.tools.phishing import PhishingTools
from swarm.tools.gemini import GeminiTools
from swarm.tools.dynamic_skiller import DynamicSkiller
from swarm.tools.tts import TTSTools

def main():
    parser = argparse.ArgumentParser(description="Kali Linux Autonomous Swarm (Pi 5 Edition)")
    parser.add_argument("--task", type=str, required=True, help="The initial objective for the swarm.")
    parser.add_argument("--model", type=str, default="dolphin-phi", help="The Ollama uncensored model to use. Keep under 4GB for Pi 5.")
    args = parser.parse_args()

    print(f"[*] Initializing Swarm on Kali Linux (Model: {args.model})")
    
    # 1. Initialize Backend
    llm = OllamaBackend(model=args.model)
    if not llm.check_connection():
        print("[-] Error: Ollama backend not reachable. Ensure 'ollama serve' is running.")
        return
        
    print("[+] LLM Backend connected successfully.")

    # 2. Initialize Memory
    memory = LightweightMemory(db_path="swarm_knowledge.json", llm_backend=llm)
    print(f"[+] Memory module loaded. Context count: {len(memory.memory)}")

    # 3. Setup Tools
    tools = {
        "execute_command": SystemTools.execute_command,
        "read_file": SystemTools.read_file,
        "ui_click": UITools.click,
        "ui_type": UITools.type_text,
        "ui_screenshot": UITools.screenshot,
        "osint_skills": lambda _: OSINTSkills.get_skill_tree(),
        "wifi_interfaces": lambda _: WiFiTools.get_interfaces(),
        "wifi_monitor_start": WiFiTools.enable_monitor_mode,
        "wifi_monitor_stop": WiFiTools.disable_monitor_mode,
        "wifi_automate_wifite": lambda target: WiFiTools.start_wifite_auto(target.split(' ')[0], target.split(' ')[1] if ' ' in target else ""),
        "wifi_list_handshakes": lambda _: WiFiTools.list_captured_handshakes(),
        "wifi_deauth_target": lambda args: WiFiTools.deauth_target(*args.split()) if len(args.split()) >= 2 else "[Error] Requires interface and bssid.",
        "bt_interfaces": lambda _: BluetoothTools.get_interfaces(),
        "bt_scan_le": lambda iface: BluetoothTools.scan_le(iface) if iface else BluetoothTools.scan_le(),
        "bt_l2ping_flood": lambda args: BluetoothTools.l2ping_flood(*args.split()) if len(args.split()) >= 1 else "[Error] MAC missing",
        "evil_twin_start": lambda args: EvilTwinTools.start_rogue_ap(*args.split()) if len(args.split()) >= 2 else "[Error] Need interface and ssid",
        "evil_twin_stop": lambda _: EvilTwinTools.stop_rogue_ap(),
        "host_captive_dns": lambda iface: EvilTwinTools.start_captive_dns(iface) if iface else "[Error] No interface",
        "nuclei_scan": lambda target: VulnerabilityTools.run_nuclei(target),
        "hashcat_crack": lambda file: HashcatTools.crack_wpa(file),
        "phishing_draft": lambda args: PhishingTools.draft_phishing_email(llm, *args.split('|')) if '|' in args else "[Error] Format: target_info | sender_context",
        "gemini_query": lambda prompt: GeminiTools.query_gemini(prompt),
        "propose_new_skill": lambda description: DynamicSkiller.propose_new_skill(llm, description),
        "tts_generate": lambda text: TTSTools.generate_tts(text)
    }
    print(f"[+] Tools loaded: {list(tools.keys())}")

    # 4. Instantiate Swarm Commander
    # Due to Pi 5 memory constraints, we'll start with a single highly capable commander/generalist 
    # rather than loading 3 concurrent LLM sessions. The commander will simulate the swarm roles.
    
    agent = Agent(
        name="KALI_COMMANDER_01",
        role="You are the lead agent of a swarm operating on Kali Linux. Use OSINT tools, system commands, and WiFi automation tools (wifite) to achieve the user's objective safely. Read the 'osint_skills' tree to understand your capabilities.",
        tools=tools,
        llm_backend=llm,
        memory=memory
    )

    # 5. Execute Task
    result = agent.execute_task(args.task)
    
    # 6. Self-Reflection and Improvement
    agent.reflect_on_execution(args.task, result)
    
    print("\n--- SWARM EXECUTION COMPLETE ---")

if __name__ == "__main__":
    main()
