import os
import hashlib
import json
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IndexManager:
    def __init__(self, input_dir="input", cache_file=".index_cache"):
        self.input_dir = Path(input_dir)
        self.cache_file = Path(cache_file)
        self.input_dir.mkdir(exist_ok=True)

    def _get_file_hash(self, filepath):
        """Calculate MD5 hash of a file"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            logger.warning(f"Could not hash file {filepath}: {e}")
            return ""

    def get_status(self):
        """Get current indexing status"""
        if not self.cache_file.exists():
            return "No index found."
        if self.check_file_changes():
            return "Changes detected. Re-indexing required."
        return "Index exists and is up to date."

    def check_file_changes(self):
        """Check if any files have changed since last indexing"""
        try:
            if not self.cache_file.exists():
                return False
            cache = json.loads(self.cache_file.read_text())
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Could not read cache: {e}")
            return True
        
        for f in self.input_dir.glob("*"):
            if f.is_file() and self._get_file_hash(f) != cache.get(str(f)):
                return True
        return False

    def run_indexing(self):
        """Run graphrag indexing"""
        try:
            cmd = ["python", "-m", "graphrag.index", "--root", "."]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                logger.error(f"Indexing failed: {result.stderr}")
                return False
            
            # Update cache with new file hashes
            cache = {str(f): self._get_file_hash(f) for f in self.input_dir.glob("*") if f.is_file()}
            self.cache_file.write_text(json.dumps(cache))
            logger.info("Indexing completed successfully")
            return True
        except subprocess.TimeoutExpired:
            logger.error("Indexing timed out after 5 minutes")
            return False
        except Exception as e:
            logger.error(f"Indexing failed: {e}")
            return False