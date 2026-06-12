import os
import hashlib
import json
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentIndexManager:
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
        """Run graphrag indexing via CLI"""
        try:
            import sys
            python_exe = sys.executable
            
            logger.info("Starting document indexing...")
            
            # Verify input files exist
            input_files = list(self.input_dir.glob("*"))
            if not input_files:
                logger.error("No input files found")
                return False
            
            logger.info(f"Found {len(input_files)} files to index: {[f.name for f in input_files]}")
            
            # Set up environment variables
            import os
            os.environ['GRAPHRAG_LLM_MODEL'] = 'qwen3:8b'
            os.environ['GRAPHRAG_EMBEDDINGS_MODEL'] = 'nomic-embed-text'
            os.environ['GRAPHRAG_LLM_API_BASE'] = 'http://localhost:11434/v1'
            
            # Run indexing via CLI
            cmd = [python_exe, "-m", "graphrag", "index", "--root", "."]
            logger.info(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minutes
                cwd=str(self.input_dir.parent)
            )
            
            if result.stdout:
                logger.info(f"Output: {result.stdout[:500]}")
            if result.stderr:
                logger.warning(f"Stderr: {result.stderr[:500]}")
            
            if result.returncode != 0:
                logger.error(f"Indexing failed with code {result.returncode}")
                return False
            
            # Verify output was created
            output_dir = Path("./output")
            if output_dir.exists():
                logger.info(f"✅ Index created at {output_dir}")
                # Update cache
                cache = {str(f): self._get_file_hash(f) for f in self.input_dir.glob("*") if f.is_file()}
                self.cache_file.write_text(json.dumps(cache))
                return True
            else:
                logger.warning("Output directory not created")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Indexing timed out after 10 minutes")
            return False
        except Exception as e:
            logger.error(f"Indexing failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False