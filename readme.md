# Secrets and sensitive data
secrets.yaml

# Home Assistant internal storage
.storage/
.cloud/
.google.token

# Backups
backups/
*.tar

# Logs
*.log
home-assistant.log
home-assistant.log.*
home-assistant.log.fault

# Database
home-assistant_v2.db
home-assistant_v2.db-shm
home-assistant_v2.db-wal

# HA runtime files
.ha_run.lock
.HA_VERSION
hacs.zip

# HA managed folders
deps/
tts/
www/
blueprints/

# Compiled Python
__pycache__/
*.pyc

# Themes (optional - remove if you want to track themes)
# themes/

# Custom components deps
custom_components/**/node_modules/

# OS files
.DS_Store
Thumbs.db

# VS Code server (installed remotely)
.vscode-server/