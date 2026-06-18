import os
import hashlib
import json
import subprocess
import shutil
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
        output_dir = Path("./ragtest/output")
        has_index = output_dir.exists() and bool(list(output_dir.rglob("*.parquet")))
        
        if not has_index:
            return "Nenhum índice encontrado. Faça upload e indexe documentos."
        if self.check_file_changes():
            return "Alterações detectadas. Re-indexação necessária."
        return "Índice existente e atualizado."

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

    def get_indexed_files(self):
        """Return list of files in input directory with metadata"""
        files = []
        for f in sorted(self.input_dir.glob("*")):
            if f.is_file():
                try:
                    size_kb = f.stat().st_size / 1024
                    files.append({
                        "name": f.name,
                        "path": str(f),
                        "size_kb": round(size_kb, 1),
                        "modified": f.stat().st_mtime
                    })
                except Exception as e:
                    files.append({
                        "name": f.name,
                        "path": str(f),
                        "size_kb": 0,
                        "error": str(e)
                    })
        return files

    def delete_file(self, filename):
        """Delete a file from the input directory"""
        file_path = self.input_dir / filename
        try:
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
                logger.info(f"File deleted: {filename}")
                
                # Also remove from ragtest/input if it exists there
                ragtest_input = Path("ragtest/input") / filename
                if ragtest_input.exists():
                    ragtest_input.unlink()
                    logger.info(f"Also removed from ragtest/input: {filename}")
                
                # Update cache
                if self.cache_file.exists():
                    try:
                        cache = json.loads(self.cache_file.read_text())
                        cache.pop(str(file_path), None)
                        self.cache_file.write_text(json.dumps(cache))
                    except Exception:
                        pass
                
                return True, f"Arquivo '{filename}' excluído com sucesso."
            else:
                return False, f"Arquivo '{filename}' não encontrado."
        except Exception as e:
            logger.error(f"Error deleting file {filename}: {e}")
            return False, f"Erro ao excluir '{filename}': {str(e)}"

    def clear_index(self):
        """Clear the current index (output files)"""
        try:
            output_dir = Path("./ragtest/output")
            cache_dir = Path("./ragtest/cache")
            
            if output_dir.exists():
                shutil.rmtree(output_dir)
                logger.info("Output directory cleared")
            if cache_dir.exists():
                shutil.rmtree(cache_dir)
                logger.info("Cache directory cleared")
            if self.cache_file.exists():
                self.cache_file.unlink()
                logger.info("Index cache cleared")
            
            return True, "Índice limpo com sucesso. Re-indexação necessária."
        except Exception as e:
            logger.error(f"Error clearing index: {e}")
            return False, f"Erro ao limpar índice: {str(e)}"

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

            logger.info(
                f"Found {len(input_files)} files to index: "
                f"{[f.name for f in input_files]}"
            )

            # Sync files to ragtest/input
            ragtest_input = Path("ragtest/input")
            ragtest_input.mkdir(parents=True, exist_ok=True)

            # Limpa arquivos antigos
            for old_file in ragtest_input.glob("*"):
                if old_file.is_file():
                    old_file.unlink()

            for f in input_files:
                if not f.is_file():
                    continue

                # TXT
                if f.suffix.lower() == ".txt":
                    shutil.copy2(f, ragtest_input / f.name)
                    logger.info(f"TXT copiado: {f.name}")

                # Markdown
                elif f.suffix.lower() == ".md":
                    conteudo = f.read_text(
                        encoding="utf-8",
                        errors="ignore"
                    )

                    destino = ragtest_input / f"{f.stem}.txt"

                    destino.write_text(
                        conteudo,
                        encoding="utf-8"
                    )

                    logger.info(
                        f"Markdown convertido: "
                        f"{f.name} -> {destino.name}"
                    )

            # Set up environment variables
            os.environ["GRAPHRAG_LLM_MODEL"] = "qwen3:8b"
            os.environ["GRAPHRAG_EMBEDDINGS_MODEL"] = "nomic-embed-text"
            os.environ["GRAPHRAG_LLM_API_BASE"] = "http://localhost:11434/v1"

            # Run indexing via CLI
            cmd = [
                python_exe,
                "-m",
                "graphrag",
                "index",
                "--root",
                "ragtest"
            ]

            logger.info(f"Running: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,
                cwd=str(self.input_dir.parent)
            )

            if result.stdout:
                logger.info(result.stdout)

            if result.stderr:
                logger.warning(result.stderr)

            if result.returncode != 0:
                logger.error(
                    f"Indexing failed with code "
                    f"{result.returncode}"
                )
                return False

            # Verify output was created
            output_dir = Path("./ragtest/output")

            if output_dir.exists() and list(output_dir.rglob("*.parquet")):
                logger.info("✅ Index criado com sucesso")

                cache = {
                    str(f): self._get_file_hash(f)
                    for f in self.input_dir.glob("*")
                    if f.is_file()
                }

                self.cache_file.write_text(
                    json.dumps(cache)
                )

                return True

            logger.warning(
                "Output directory not created "
                "or no parquet files found"
            )
            return False

        except subprocess.TimeoutExpired:
            logger.error(
                "Indexing timed out after 10 minutes"
            )
            return False

        except Exception as e:
            logger.error(f"Indexing failed: {e}")

            import traceback
            logger.error(traceback.format_exc())

            return False