# Production Deployment Guide

This document describes the steps required to configure, deploy, run, and maintain the ACKO AI Native Insurance Platform on an enterprise server.

---

## 📋 1. System Requirements & Setup

### Requirements
* **OS**: Linux (Ubuntu 22.04 LTS recommended) or Windows Server.
* **Python**: `3.11` version runtime.
* **Database**: PostgreSQL `17` running and configured with a dedicated user pool.
* **Hardware**: Minimum 4 Physical Cores, 8 GB RAM, and 50 GB SSD space.

---

## 🛠️ 2. Step-by-Step Installation

### Step 1: Clone Repository & Create virtualenv
```bash
git clone https://github.com/Yoge2003/acko_ai_native_insurance_platform.git
cd acko_ai_native_insurance_platform
python3 -m venv .venv
source .venv/bin/activate
```

### Step 2: Install Packages (Pinned dependencies)
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Environment
Copy `.env.example` into `.env` and fill the variables:
```ini
APP_ENV=production
DATABASE_URL=postgresql://acko_user:SecurePassword@127.0.0.1:5432/acko_db
GEMINI_API_KEY=AIzaSy...YourKey...
CHROMA_DB_PATH=./chroma_db
SECRET_KEY=GeneratingA512BitSecureKeyHere
```

### Step 4: Run Alembic DDL Migrations
To initialize the PostgreSQL tables, run:
```bash
alembic upgrade head
```

---

## 🌐 3. Reverse Proxy & Streamlit Setup

To deploy Streamlit in a shared enterprise setting, run it behind a reverse proxy (e.g. Nginx) with SSL certificates.

### 1. Systemd Service File (`/etc/systemd/system/acko.service`)
```ini
[Unit]
Description=ACKO AI Streamlit Application Server
After=network.target

[Service]
User=acko_runner
WorkingDirectory=/opt/acko_ai_native_insurance_platform
ExecStart=/opt/acko_ai_native_insurance_platform/.venv/bin/python run_app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 2. Nginx VHost File (`/etc/nginx/sites-available/acko`)
```nginx
server {
    listen 80;
    server_name insurance.acko-internal.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```
Enable the virtual host and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/acko /etc/nginx/sites-enabled/
sudo systemctl restart nginx
sudo systemctl daemon-reload
sudo systemctl enable acko
sudo systemctl start acko
```

---

## 🔒 4. Maintenance & Log Rotations

Telemetry logs are captured inside `logs/` directory. System-specific logging records rotate automatically when file sizes reach 5MB. Ensure the backup count parameter is configured (default: 5) to restrict disk space consumption.
