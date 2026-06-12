import subprocess
import logging
import re
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryEngine:
    def __init__(self):
        self.cache = {}

    def query(self, text, method='local'):
        """Execute a query using GraphRAG"""
        cache_key = f"{method}:{text}"
        
        # Return cached result if available
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            import sys
            import os
            
            python_exe = sys.executable
            
            # Set up environment
            os.environ['GRAPHRAG_LLM_MODEL'] = 'qwen2:8b'
            os.environ['GRAPHRAG_EMBEDDINGS_MODEL'] = 'nomic-embed-text'
            os.environ['GRAPHRAG_LLM_API_BASE'] = 'http://localhost:11434'
            
            # Check if index exists
            output_dir = Path("./output")
            if not output_dir.exists():
                return {
                    "response": "❌ Índice não encontrado. Execute a indexação primeiro.",
                    "context": ""
                }
            
            # Build command
            cmd = [python_exe, "-m", "graphrag", "query", "--root", ".", "--method", method, text]
            logger.info(f"Running query: {' '.join(cmd[:5])}... {text[:30]}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                logger.error(f"GraphRAG query failed: {result.stderr[:200]}")
                return {
                    "response": f"❌ Erro na busca: {result.stderr[:100]}",
                    "context": ""
                }
            
            # Remove ANSI color codes
            raw_output = re.sub(r'\x1B\[[0-9;]*[mK]', '', result.stdout)
            
            # Extract response
            response = "Nenhuma resposta encontrada."
            if raw_output.strip():
                # Look for common response markers
                if "SUCCESS:" in raw_output:
                    response = raw_output.split("SUCCESS:")[-1].strip()
                elif "Response:" in raw_output:
                    response = raw_output.split("Response:")[-1].strip()
                else:
                    response = raw_output.strip()[:500]  # Limit length
            
            result_dict = {
                "response": response,
                "context": result.stderr if result.stderr else ""
            }
            
            self.cache[cache_key] = result_dict
            logger.info(f"Query successful, cached result for {cache_key}")
            return result_dict
            
        except subprocess.TimeoutExpired:
            error_msg = "⏱️ Busca expirou (timeout de 60 segundos)"
            logger.error(error_msg)
            return {"response": error_msg, "context": ""}
        except Exception as e:
            error_msg = f"❌ Erro na busca: {str(e)}"
            logger.error(error_msg)
            return {"response": error_msg, "context": ""}