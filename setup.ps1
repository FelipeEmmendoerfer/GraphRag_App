# Script de Setup para GraphRAG Project
# Execute com: .\setup.ps1 -ExecutionPolicy Bypass

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GraphRAG Project - Setup Script" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Verificar Python
Write-Host "[1/5] Verificando Python..." -ForegroundColor Yellow
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python nao encontrado. Instale o Python 3.10+" -ForegroundColor Red
    exit
}

$pyVersion = python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")'
Write-Host "✅ Python $pyVersion encontrado`n" -ForegroundColor Green

# Verificar Ollama
Write-Host "[2/5] Verificando Ollama..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri 'http://localhost:11434' -ErrorAction Stop
    Write-Host "✅ Ollama esta rodando em localhost:11434`n" -ForegroundColor Green
} catch {
    Write-Host "❌ Ollama nao esta rodando na porta 11434" -ForegroundColor Red
    Write-Host "   Inicie com: ollama serve`n" -ForegroundColor Yellow
    exit
}

# Criar venv se nao existir
Write-Host "[3/5] Configurando ambiente virtual..." -ForegroundColor Yellow
if (!(Test-Path '.venv')) {
    python -m venv .venv
    Write-Host "✅ Venv criado`n" -ForegroundColor Green
} else {
    Write-Host "✅ Venv já existe`n" -ForegroundColor Green
}

# Ativar venv e instalar dependências
Write-Host "[4/5] Instalando dependências..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt --quiet
Write-Host "✅ Dependências instaladas`n" -ForegroundColor Green

# Criar pastas necessárias
Write-Host "[5/5] Criando estrutura de pastas..." -ForegroundColor Yellow
foreach ($dir in @('input', 'output', 'ragtest')) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
    }
}
Write-Host "✅ Estrutura de pastas pronta`n" -ForegroundColor Green

# Resumo final
Write-Host "========================================" -ForegroundColor Green
Write-Host "Setup concluido com sucesso!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Proximos passos:" -ForegroundColor Cyan
Write-Host "1. Baixar modelo Ollama:" -ForegroundColor White
Write-Host "   ollama pull qwen2:8b" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Executar a aplicacao:" -ForegroundColor White
Write-Host "   streamlit run app.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Abrir http://localhost:8501 no navegador`n" -ForegroundColor White

Write-Host "Para verificar a configuracao, execute:" -ForegroundColor Cyan
Write-Host "python verify.py`n" -ForegroundColor Yellow