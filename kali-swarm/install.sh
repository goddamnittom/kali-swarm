#!/bin/bash

# Kali Linux Swarm (Pi 5) Foolproof Installer

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}===============================================${NC}"
echo -e "${GREEN}   Kali Swarm (Raspberry Pi 5) Installer       ${NC}"
echo -e "${GREEN}===============================================${NC}"

# Check if running as root (needed for apt)
if [ "$EUID" -ne 0 ]; then 
  echo -e "${RED}[!] Please run this installer with sudo: sudo ./install.sh${NC}"
  exit 1
fi

echo -e "\n${YELLOW}[*] Step 1: Updating System & Installing Kali APT Dependencies...${NC}"
apt update
apt install -y python3-pip python3-venv git wifite aircrack-ng hostapd dnsmasq bluez nuclei hashcat curl

echo -e "\n${YELLOW}[*] Step 2: Installing Ollama LLM Engine...${NC}"
if ! command -v ollama &> /dev/null; then
    echo "[+] Ollama not found. Installing..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "[+] Ollama is already installed."
fi

# Start Ollama service if not running
systemctl enable --now ollama

echo -e "\n${YELLOW}[*] Step 3: Pulling the Uncensored Model (dolphin-phi)...${NC}"
echo "[+] This may take a few minutes depending on your internet connection."
# Run this as the normal user if possible, but root is fine for global ollama
ollama pull dolphin-phi

echo -e "\n${YELLOW}[*] Step 4: Setting up Python Environment...${NC}"
# It's best practice to use a venv on Kali now
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "[+] Virtual environment created."
fi
source venv/bin/activate
pip install -r requirements.txt

echo -e "\n${YELLOW}[*] Step 5: Configuring Discord C2...${NC}"
if [ ! -f .env ]; then
    echo -e "${GREEN}Let's set up your Discord Bot credentials.${NC}"
    read -p "Enter your Discord Bot Token: " discord_token
    read -p "Enter your personal Discord User ID: " discord_user_id
    
    echo "DISCORD_BOT_TOKEN=$discord_token" > .env
    echo "AUTHORIZED_USER_ID=$discord_user_id" >> .env
    echo "[+] .env file created securely."
else
    echo "[+] .env file already exists. Skipping configuration."
fi

echo -e "\n${GREEN}===============================================${NC}"
echo -e "${GREEN}[SUCCESS] Kali Swarm Installation Complete!${NC}"
echo -e "To start the Swarm Command & Control interface, run:"
echo -e "\n  ${YELLOW}source venv/bin/activate${NC}"
echo -e "  ${YELLOW}sudo python3 discord_bot.py${NC}  (sudo required for wifi/bt tools)"
echo -e "\nOr, to run the local CLI agent:"
echo -e "  ${YELLOW}source venv/bin/activate${NC}"
echo -e "  ${YELLOW}sudo python3 main.py --task \"your objective here\"${NC}"
echo -e "${GREEN}===============================================${NC}"
