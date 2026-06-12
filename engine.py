import subprocess
import logging
import re
from pathlib import Path
import sys
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryEngine:
    def __init__(self):
        self.cache = {}

    def query(self, text, method="local"):

        cache_key = f"{method}:{text}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        try:

            python_exe = sys.executable

            env = os.environ.copy()

            env["GRAPHRAG_LLM_MODEL"] = "qwen3:8b"
            env["GRAPHRAG_EMBEDDINGS_MODEL"] = "nomic-embed-text"
            env["GRAPHRAG_LLM_API_BASE"] = "http://localhost:11434/v1"

            output_dir = Path("./output")

            parquet_files = list(output_dir.rglob("*.parquet"))
            if not parquet_files:
                return {
                    "response": "❌ Índice não encontrado. Execute a indexação primeiro.",
                    "context": ""
                }

  
            cmd = [python_exe, "-m", "graphrag", "query", "--root", "ragtest", "--method", method, text]

            logger.info(f"Running query: {text}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                env=env
            )

            if result.returncode != 0:
                logger.error(result.stderr)

                return {
                    "response": "❌ Erro ao executar consulta GraphRAG",
                    "context": result.stderr
                }

            raw_output = re.sub(
                r'\x1B\[[0-9;]*[mK]',
                '',
                result.stdout
            )

            response = raw_output.strip()

            if not response:
                response = "Nenhuma resposta encontrada."

            result_dict = {
                "response": response,
                "context": result.stderr
            }

            self.cache[cache_key] = result_dict

            return result_dict

        except subprocess.TimeoutExpired:
            return {
                "response": "⏱️ Timeout da consulta",
                "context": ""
            }

        except Exception as e:
            logger.exception(e)

            return {
                "response": f"❌ Erro: {str(e)}",
                "context": ""
            }