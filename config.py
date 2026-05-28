from dotenv import load_dotenv
import os

load_dotenv()

USE_REAL_API = False

MODEL_NAME = "gpt-4.1-mini"

INPUT_FILE = "inputs/jobs.json"

OUTPUT_DIR = "outputs"

DATABASE_PATH = "jobs.db"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")