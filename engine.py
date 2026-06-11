import subprocess
import logging
import re

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
            cmd = ["python", "-m", "graphrag.query", "--root", ".", "--method", method, text]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                logger.error(f"GraphRAG Error: {result.stderr}")
                return {"response": f"Error: {result.stderr}", "context": ""}

            # Remove ANSI color codes from output
            raw_output = re.sub(r'\x1B\[[0-9;]*[mK]', '', result.stdout)
            
            response = "No response found."
            context = "No context found."
            
            # Parse response from output
            if "SUCCESS:" in raw_output:
                response = raw_output.split("SUCCESS:")[-1].strip()
            elif raw_output.strip():
                response = raw_output.strip()
            
            result_dict = {"response": response, "context": context}
            self.cache[cache_key] = result_dict
            return result_dict
            
        except subprocess.TimeoutExpired:
            error_msg = "Query timed out after 60 seconds"
            logger.error(error_msg)
            return {"response": error_msg, "context": ""}
        except Exception as e:
            error_msg = f"Query failed: {str(e)}"
            logger.error(error_msg)
            return {"response": error_msg, "context": ""}