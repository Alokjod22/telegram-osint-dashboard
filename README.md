# Telegram OSINT Research Bot Platform

A general-purpose Open Source Intelligence (OSINT) research bot and investigation engine built for Telegram, powered by Python, Gemini AI, SQLite/PostgreSQL, and FastAPI.

---

## Features

- **Multi-Source OSINT Engine**:
  - **Domain & DNS**: DNS records (A, MX, TXT, NS), WHOIS/RDAP, HTTP security headers, robots.txt, sitemaps.
  - **Username Intelligence**: Multi-platform public profile search (GitHub, GitLab, Twitter, Reddit, Dev.to, Medium, DockerHub).
  - **Phone Number OSINT**: E.164 normalization, country/carrier detection via public numbering plans.
  - **News & Web Search**: Search engine aggregation and article correlation.
  - **Document Processor**: Extractor for PDF, TXT, CSV, JSON, and HTML.
- **AI Analysis Engine**: Powered by Google Gemini API (`google-genai`) for entity correlation, search result summarization, timeline generation, and contradiction detection.
- **Abuse & Violation Evidence Reporter**: Drafts structured evidence reports for manual policy violation submission (`abuse@telegram.org`, `stopca@telegram.org`, `dmca@telegram.org`).
- **Investigation Workspace & Reports**: Independent investigation tracking with report export in Markdown, HTML, JSON, and PDF.
- **Admin Web Dashboard**: FastAPI-based local web dashboard for monitoring searches, investigation status, and source health.

---

## Local Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file:
```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite+aiosqlite:///./osint_bot.db
```

### 3. Run the Bot
```bash
python bot/main.py
```

### 4. Run the Admin Dashboard
```bash
uvicorn dashboard.app:app --reload --port 8000
```
Open `http://localhost:8000` in your browser.

---

## Deploying on Oracle Cloud Infrastructure (OCI VPS)

### Step 1: Provision Oracle Cloud Always Free VM
1. Log into your **Oracle Cloud Console**.
2. Create a Compute Instance:
   - **OS**: Ubuntu 22.04 LTS or Oracle Linux 8/9.
   - **Shape**: `VM.Standard.A1.Flex` (ARM 4 OCPU, 24 GB RAM) or `VM.Standard.E2.1.Micro` (x86).
3. Under **Networking > Ingress Rules**, add an Ingress Rule:
   - **Source**: `0.0.0.0/0`
   - **Protocol**: TCP
   - **Destination Port Range**: `8000` (for Dashboard)

### Step 2: SSH into your Oracle VPS & Run Setup
```bash
git clone https://github.com/your-username/telegram_osint_bot.git
cd telegram_osint_bot

# Make deployment script executable
chmod +x deploy_oracle.sh

# Run Oracle Cloud Deployment Script
./deploy_oracle.sh
```

---

## Running Automated Tests

Run the pytest test suite:
```bash
pytest tests/
```
