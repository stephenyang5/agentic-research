"""
Load settings from environment variables.
- Keeps secrets and tunables out of pubmed.py / summarizer.py
- One place to change defaults later
"""

import os

from dotenv import load_dotenv

# Reads .env into process environment. Safe to call even if .env is missing.
load_dotenv()

# NCBI requires an email so they can contact you if your script misbehaves.
NCBI_EMAIL: str = os.getenv("NCBI_EMAIL", "")

# Optional. Raises NCBI rate limits when set. Empty string means "not provided".
NCBI_API_KEY: str = os.getenv("NCBI_API_KEY", "")

# How many paper IDs to request from a search. Week 1 goal: top 10.
DEFAULT_MAX_RETURNS: int = 10

# Local Ollama model name (must already be pulled, e.g. `ollama pull llama3.2`).
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL")

# Where the Ollama server listens. Default is fine for a local install.
OLLAMA_HOST: str = os.getenv("OLLAMA_HOST")
