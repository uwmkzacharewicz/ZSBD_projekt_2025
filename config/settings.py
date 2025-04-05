import os

# Aktywne środowisko
ACTIVE_ENV = "proxmox"  # lub "remote"
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

SCHEMA_SOURCE = "local"  # "local" albo "github"

SCHEMA_FILE_URL = "https://raw.githubusercontent.com/uwmkzacharewicz/ZSBD_projekt/main/schema.sql"
SCHEMA_FILE_LOCAL = os.path.join("db", "schema", "schema.sql")

ENABLE_LOGGING = True
SCHEDULE_IMPORT_EVERY_MINUTES = 30
