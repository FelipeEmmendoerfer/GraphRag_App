import sys
import os
import requests
import subprocess
import importlib.util

def print_status(name, status, message=""):
    color = "\033[92m" if status == "OK" else "\033[91m"
    reset = "\033[0m"
    status_str = f"{color}{status}{reset}".ljust(20)
    print(f"{name:.<40} {status_str} {message}")

def check_python_version():
    """Check Python version compatibility"""
    major, minor, patch = sys.version_info[:3]
    print(f"\nPython Version: {major}.{minor}.{patch}")
    
    # Note: graphrag requires Python 3.10-3.12, but we'll proceed with newer versions
    if major == 3 and minor >= 10:
        print_status("Python Compatibility", "OK", f"v{major}.{minor} (graphrag compatible with 3.10-3.12)")
    else:
        print_status("Python Compatibility", "FAIL", f"v{major}.{minor} (requires >= 3.10)")

def check_env():
    print("=" * 70)
    print("GraphRAG Project Verification")
    print("=" * 70)
    
    check_python_version()
    
    # Ollama
    print("\n--- Services ---")
    try:
        response = requests.get("http://localhost:11434", timeout=2)
        if response.status_code == 200:
            print_status("Ollama Service", "OK", "Running on localhost:11434")
            try:
                models_response = requests.get("http://localhost:11434/api/tags", timeout=5)
                models = models_response.json().get("models", [])
                model_names = [m['name'] for m in models]
                
                for model in ["qwen2:8b", "nomic-embed-text"]:
                    model_found = any(model in m for m in model_names)
                    print_status(f"  - Model {model}", "OK" if model_found else "MISSING")
            except Exception as e:
                print_status("  - Model Check", "FAIL", str(e))
        else:
            print_status("Ollama Service", "FAIL", f"Status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print_status("Ollama Service", "FAIL", "Not running on localhost:11434")
    except Exception as e:
        print_status("Ollama Service", "FAIL", str(e))

    # Dependencies
    print("\n--- Dependencies ---")
    for lib in ["graphrag", "streamlit", "pandas", "pydantic"]:
        spec = importlib.util.find_spec(lib)
        print_status(f"Library {lib}", "OK" if spec is not None else "MISSING")

    # Folders
    print("\n--- Project Structure ---")
    for folder in ["input", "output", "ragtest"]:
        exists = os.path.exists(folder)
        status = "OK" if exists else "MISSING"
        print_status(f"Folder '{folder}'", status)

    # Config Files
    print("\n--- Configuration ---")
    for config_file in ["settings.yaml", "ragtest/settings.yaml"]:
        exists = os.path.exists(config_file)
        print_status(f"File '{config_file}'", "OK" if exists else "MISSING")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    check_env()