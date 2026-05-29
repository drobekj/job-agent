from dotenv import load_dotenv
import os

load_dotenv()

USE_REAL_API = False

MODEL_NAME = "gpt-4.1-mini"

JOBS_JSON_PATH = "inputs/jobs.json"
SOURCES_JSON_PATH = "sources.json"

OUTPUT_DIR = "outputs"

DATABASE_PATH = "jobs.db"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

DISCOVERED_JOBS_PATH = "inputs/discovered_jobs.json"

DEBUG_DISCOVERY = False