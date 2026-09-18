#!/bin/bash
# Oracle Cloud Infrastructure (OCI) Ubuntu / Oracle Linux One-Click VPS Deployment Script
set -e

echo "=================================================="
echo "🚀 Deploying Telegram OSINT Bot on Oracle Cloud VPS"
echo "=================================================="

# Update package repositories
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Docker & Docker Compose
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    sudo apt-get install -y docker-compose-plugin docker-compose
fi

# Configure Oracle Cloud Firewall (iptables / ufw) for Dashboard Port 8000
echo "🛡️ Configuring Oracle Cloud Firewall Ingress Rules..."
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT || true
sudo iptables-save | sudo tee /etc/iptables/rules.v4 || true
if command -v ufw &> /dev/null; then
    sudo ufw allow 8000/tcp || true
fi

# Check .env file
if [ ! -f .env ]; then
    echo "⚠️ .env file not found! Creating default .env file..."
    cat <<EOT > .env
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
EOT
    echo "Please edit the .env file with your real bot token and API keys."
fi

# Build & Run Containers
echo "🐳 Launching OSINT Bot & Admin Dashboard via Docker Compose..."
docker-compose up -d --build

echo "=================================================="
echo "✅ Oracle Cloud Deployment Complete!"
echo "🌐 Admin Dashboard: http://YOUR_ORACLE_VPS_IP:8000"
echo "🤖 Telegram Bot is running in the background."
echo "=================================================="
