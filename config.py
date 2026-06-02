from dotenv import load_dotenv
import os

load_dotenv()

# Runtime mode is now controlled by CLI:
#   python main.py --mode prepare
#   python main.py --mode evaluate
#
# Keep this only as a legacy fallback if some old code still imports it.
USE_REAL_API = False

MODEL_NAME = "gpt-4.1-mini"

# Input files
JOBS_JSON_PATH = "inputs/jobs.json"
DISCOVERED_JOBS_PATH = "inputs/discovered_jobs.json"
WEB_JOBS_PATH = "inputs/web_jobs.json"

# Optional legacy/source config
SOURCES_JSON_PATH = "sources.json"

# Outputs / database
OUTPUT_DIR = "outputs"
DATABASE_PATH = "jobs.db"

# API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Debug flags
DEBUG_DISCOVERY = False