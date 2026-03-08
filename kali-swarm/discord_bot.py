import os
import discord
from dotenv import load_dotenv
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
import asyncio
import re

# Temporary storage for proposed skills awaiting approval
PENDING_SKILLS = {}

# Load configuration
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
AUTHORIZED_USER_ID = int(os.getenv('AUTHORIZED_USER_ID', 0))

if not TOKEN or not AUTHORIZED_USER_ID:
    print("[-] Missing configuration. Check your .env file.")
    exit(1)

# Set up Discord intents
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Global variables for Swarm singletons
agent = None

@client.event
async def on_ready():
    global agent
    print(f'[*] Discord Bot logged in as {client.user}')
    
    # Initialize Swarm
    print("[*] Initializing Swarm on Kali Linux (Model: dolphin-phi)")
    llm = OllamaBackend(model="dolphin-phi")
    if not llm.check_connection():
        print("[-] Error: Ollama backend not reachable.")
        return
        
    memory = LightweightMemory(db_path="swarm_knowledge.json", llm_backend=llm)
    
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
    
    agent = Agent(
        name="KALI_COMMANDER_01",
        role="You are the lead agent of a swarm operating on Kali Linux. Use OSINT tools, system commands, and WiFi automation tools (wifite) to achieve the target safely.",
        tools=tools,
        llm_backend=llm,
        memory=memory
    )
    print("[+] Swarm agent ready. Awaiting commands.")

@client.event
async def on_message(message):
    global agent
    
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Strictly authenticate by User ID
    if message.author.id != AUTHORIZED_USER_ID:
        print(f"[!] Unauthorized access attempt by {message.author} (ID: {message.author.id})")
        return

    # Check if this is an approval/denial for a pending skill
    if message.author.id in PENDING_SKILLS:
        decision = message.content.strip().lower()
        if decision in ['yes', 'y', 'approve']:
            skill_code = PENDING_SKILLS[message.author.id]
            # Write to tools dir
            try:
                # Find the class name to name the file
                class_match = re.search(r'class\s+([A-Za-z0-9_]+)', skill_code)
                fname = class_match.group(1).lower() if class_match else "custom_skill"
                fpath = f"swarm/tools/{fname}.py"
                with open(fpath, "w") as f:
                    f.write(skill_code)
                await message.channel.send(f"✅ **Skill successfully implemented and saved to** `{fpath}`.\n*(Note: Restart the bot to load new modules globally.)*")
            except Exception as e:
                await message.channel.send(f"❌ **Failed to write skill:** `{str(e)}`")
        else:
            await message.channel.send("❌ **Proposed skill discarded.**")
        
        del PENDING_SKILLS[message.author.id]
        return

    task = message.content.strip()
    if not task:
        return

    print(f"[*] Received command via Discord: {task}")
    await message.channel.send(f"🤖 **Commander Agent received task:** `{task}`\nExecuting... please wait.")
    
    # Execute Swarm task in an executor to avoid blocking the asyncio event loop
    loop = asyncio.get_running_loop()
    try:
        if agent is None:
            await message.channel.send("❌ Error: Swarm agent not initialized properly.")
            return

        result = await loop.run_in_executor(None, agent.execute_task, task)
        
        if "PROPOSED_SKILL_PAYLOAD" in result:
            # The agent halted to propose a skill
            code_block = result.split("PROPOSED_SKILL_PAYLOAD\n")[1].strip()
            PENDING_SKILLS[message.author.id] = code_block
            
            prompt = f"⚠️ **The Swarm lacks context and has drafted a NEW SKILL to solve this.**\n\n```python\n{code_block}\n```\n\n**Do you approve implementing this script into the Swarm's permanent toolset?** (Reply `yes` or `no`)"
            
            # Send the proposal in chunks if extremely long
            if len(prompt) > 1950:
                for i in range(0, len(prompt), 1950):
                    await message.channel.send(prompt[i:i+1950])
            else:
                await message.channel.send(prompt)
            return

        # Check for TTS Audio attachment
        audio_file = None
        audio_match = re.search(r'\[ATTACH_AUDIO:(.*?)\]', result)
        if audio_match:
            audio_path = audio_match.group(1).strip()
            if os.path.exists(audio_path):
                audio_file = discord.File(audio_path)
            # Remove the tag from the final visual text
            result = result.replace(audio_match.group(0), "").strip()

        # We also want to fire the reflection off in the background, without blocking
        loop.run_in_executor(None, agent.reflect_on_execution, task, result)

        # Discord message limit is 2000 chars, so chunk if necessary
        if len(result) > 1950:
            for i in range(0, len(result), 1950):
                # Send the file only on the first chunk to avoid spamming the attachment
                if i == 0 and audio_file:
                    await message.channel.send(f"```\n{result[i:i+1950]}\n```", file=audio_file)
                else:
                    await message.channel.send(f"```\n{result[i:i+1950]}\n```")
        else:
            if audio_file:
                await message.channel.send(f"**Task Complete:**\n```\n{result}\n```", file=audio_file)
            else:
                await message.channel.send(f"**Task Complete:**\n```\n{result}\n```")
            
    except Exception as e:
        await message.channel.send(f"❌ **Error executing task:** `{str(e)}`")

if __name__ == "__main__":
    client.run(TOKEN)
