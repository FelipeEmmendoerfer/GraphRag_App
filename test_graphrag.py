#!/usr/bin/env python3
"""
GraphRAG Diagnostic Tool
Testa cada componente do pipeline GraphRAG
"""

import subprocess
import sys
import os
from pathlib import Path

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def run_command(cmd, description):
    """Run a command and print results"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ SUCESSO")
            if result.stdout:
                print(f"   {result.stdout[:200]}")
            return True
        else:
            print(f"❌ FALHA (código {result.returncode})")
            if result.stderr:
                print(f"   Erro: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱️ TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ EXCEÇÃO: {str(e)}")
        return False

def check_python_version():
    """Check Python version"""
    print_header("1. Verificando Python")
    version = sys.version
    print(f"Python: {version}")
    if sys.version_info >= (3, 10) and sys.version_info < (3, 13):
        print("✅ Versão compatível")
        return True
    else:
        print("❌ Versão incompatível")
        return False

def check_graphrag():
    """Check GraphRAG installation"""
    print_header("2. Verificando GraphRAG")
    try:
        import graphrag
        version = getattr(graphrag, '__version__', 'unknown')
        print(f"✅ GraphRAG instalado: {version}")
        return True
    except ImportError:
        print("❌ GraphRAG não está instalado")
        return False

def check_ollama():
    """Check Ollama service"""
    print_header("3. Verificando Ollama")
    return run_command("curl -s http://localhost:11434/api/tags", "Conectando a Ollama")

def check_input_files():
    """Check input directory"""
    print_header("4. Verificando Arquivos de Entrada")
    input_dir = Path("input")
    input_dir.mkdir(exist_ok=True)
    
    files = list(input_dir.glob("*"))
    if files:
        print(f"✅ {len(files)} arquivo(s) encontrado(s):")
        for f in files:
            size_kb = f.stat().st_size / 1024
            print(f"   - {f.name} ({size_kb:.1f} KB)")
        return True
    else:
        print("❌ Nenhum arquivo encontrado em input/")
        return False

def check_settings():
    """Check settings.yaml"""
    print_header("5. Verificando settings.yaml")
    settings_file = Path("settings.yaml")
    
    if settings_file.exists():
        print("✅ settings.yaml encontrado")
        with open(settings_file) as f:
            content = f.read()
            if 'ollama' in content.lower():
                print("   ✅ Configurado para Ollama")
            else:
                print("   ⚠️ Não está configurado para Ollama")
        return True
    else:
        print("❌ settings.yaml não encontrado")
        return False

def check_graphrag_modules():
    """Check GraphRAG modules"""
    print_header("6. Verificando Módulos do GraphRAG")
    modules = [
        "graphrag.index",
        "graphrag.query",
        "graphrag.index.cli",
        "graphrag.query.cli"
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {str(e)}")
            all_ok = False
    
    return all_ok

def test_indexing():
    """Test indexing command"""
    print_header("7. Testando Indexação")
    
    # Check if we have input files
    input_files = list(Path("input").glob("*"))
    if not input_files:
        print("❌ Sem arquivos em input/ - não é possível testar")
        return False
    
    python_exe = sys.executable
    cmd = f'{python_exe} -m graphrag.index --help'
    print(f"Testando comando: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Comando de indexação está disponível")
            return True
        else:
            print(f"❌ Comando de indexação falhou: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar: {str(e)}")
        return False

def test_query():
    """Test query command"""
    print_header("8. Testando Query")
    
    # Check if index exists
    output_dir = Path("./output")
    if not output_dir.exists():
        print("❌ Índice não existe - execute indexação primeiro")
        return False
    
    python_exe = sys.executable
    cmd = f'{python_exe} -m graphrag.query --help'
    print(f"Testando comando: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Comando de query está disponível")
            return True
        else:
            print(f"❌ Comando de query falhou: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar: {str(e)}")
        return False

def main():
    """Run all diagnostics"""
    print("\n🔍 GraphRAG Diagnostic Tool\n")
    
    results = {
        "Python": check_python_version(),
        "GraphRAG": check_graphrag(),
        "Ollama": check_ollama(),
        "Input Files": check_input_files(),
        "Settings": check_settings(),
        "Modules": check_graphrag_modules(),
        "Indexing": test_indexing(),
        "Query": test_query(),
    }
    
    print_header("RESUMO DOS TESTES")
    for name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    all_passed = all(results.values())
    print_header("RESULTADO FINAL")
    if all_passed:
        print("🎉 Todos os testes passaram!")
        print("\n✅ Sistema pronto para:")
        print("   1. Executar indexação")
        print("   2. Executar queries")
    else:
        print("⚠️ Alguns testes falharam. Verifique os erros acima.")
        print("\nDicas de troubleshooting:")
        if not results["Ollama"]:
            print("   - Inicie Ollama: ollama serve")
        if not results["GraphRAG"]:
            print("   - Instale GraphRAG: pip install graphrag")
        if not results["Input Files"]:
            print("   - Adicione arquivos a input/")

if __name__ == "__main__":
    main()
