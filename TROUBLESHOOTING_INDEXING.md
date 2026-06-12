.\.venv\Scripts\python.exe -m graphrag.index --root . 2>&1 | head -50# 🔧 Guia de Troubleshooting - Indexação e Busca

## Problema: Indexação não funciona

### Solução passo-a-passo:

#### 1️⃣ Verificar se há arquivo para indexar

```powershell
cd c:\Users\Felipe\Desktop\meu_projeto
ls input/
```

Deve mostrar pelo menos um arquivo `.txt`, `.pdf` ou `.docx`.

#### 2️⃣ Verificar Ollama

```powershell
# Terminal novo
ollama serve
```

Em outro terminal:
```powershell
ollama list
```

Deve mostrar os modelos instalados.

#### 3️⃣ Baixar modelo se necessário

```powershell
ollama pull qwen2:8b
```

#### 4️⃣ Testar indexação manual

```powershell
cd c:\Users\Felipe\Desktop\meu_projeto
.\.venv\Scripts\python.exe -m graphrag.index --root .
```

Se tiver erro, copie e cole a mensagem aqui.

#### 5️⃣ Verificar se settings.yaml está correto

O arquivo `settings.yaml` deve estar na raiz do projeto.

## Problema: Busca não retorna resultados

### Solução:

#### 1️⃣ Verificar se index foi criado

```powershell
ls output/
```

Deve ter pasta `artifacts/` com índices.

#### 2️⃣ Testar busca manual

```powershell
cd c:\Users\Felipe\Desktop\meu_projeto
.\.venv\Scripts\python.exe -m graphrag.query --root . --method local "sua pergunta aqui"
```

#### 3️⃣ Verificar logs

```powershell
# Logs do Streamlit
cat ~/.streamlit/logs/2024*.log
```

## Quick Fix: Versão Simplificada (Teste)

Se quer testar sem GraphRAG completo, edite `engine.py`:

```python
def query(self, text, method='local'):
    # Modo teste - retorna dummy response
    return {
        "response": f"[TESTE] Resposta para: {text}",
        "context": "Índice não disponível - use modo teste"
    }
```

## Checklist Completo

- [ ] Ollama rodando (`ollama serve`)
- [ ] Modelo baixado (`ollama list` mostra qwen2:8b)
- [ ] Arquivo em `input/`
- [ ] `settings.yaml` existe
- [ ] Botão "Indexar Agora" clicado
- [ ] Pasta `output/` criada com conteúdo
- [ ] Teste manual de busca funciona

## Comandos Úteis

```powershell
# Resetar tudo
rm -r output/
rm .index_cache
rm -r .venv\Lib\site-packages\__pycache__

# Rodar com debug
streamlit run app.py --logger.level=debug

# Testar Python diretamente
.\.venv\Scripts\python.exe -c "import graphrag; print(graphrag.__version__)"
```

---

Se ainda tiver problemas, capture o erro completo e compartilhe! 🚀
