# 🚀 Guia de Início Rápido

## Status Atual ✅

```
✅ Python 3.12 instalado
✅ GraphRAG 3.0+ pronto
✅ Streamlit configurado  
✅ Ollama rodando
✅ Estrutura de pastas criada
```

## Próximos Passos (5 minutos)

### 1️⃣ Baixar o modelo Ollama (⏱️ ~2-5 min, depende da conexão)

```powershell
ollama pull qwen2:8b
```

**Alternativas** se qwen2:8b for pesado:
- `ollama pull mistral` (mais leve, ~4GB)
- `ollama pull neural-chat` (~4GB)
- `ollama pull orca-mini` (~3GB)

### 2️⃣ Iniciar a aplicação

```powershell
cd c:\Users\Felipe\Desktop\meu_projeto
.\.venv\Scripts\activate
streamlit run app.py
```

A interface abrirá em: **http://localhost:8501**

### 3️⃣ Usar a aplicação

1. Vá para aba **"⚙️ Configuração"**
2. Clique em **"📤 Upload de Arquivos"**
3. Selecione um arquivo TXT, PDF ou DOCX
4. Clique em **"🚀 Indexar Agora"**
5. Vá para aba **"💬 Chat"**
6. Digite sua pergunta
7. Clique em **"🔍 Buscar"**

## Arquivos de Teste

Coloque um arquivo em `input/` para testar. Exemplo:

```
c:\Users\Felipe\Desktop\meu_projeto\input\seu_documento.txt
```

## 🆘 Solução de Problemas

### "Ollama Service not found"
Abra PowerShell **Nova** e rode:
```powershell
ollama serve
```

### "Module not found"
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt --upgrade
```

### "Model not found"
Espere o modelo ser baixado ou tente outro menor:
```powershell
ollama pull mistral
```

## 📊 Estrutura do Projeto

```
meu_projeto/
├── .venv/                   ← Ambiente virtual (3.12)
├── app.py                   ← Interface (streamlit)
├── engine.py                ← Motor de busca
├── indexer.py               ← Indexação
├── verify.py                ← Verificação
├── settings.yaml            ← Configuração
├── requirements.txt         ← Dependências
├── input/                   ← Seus documentos aqui 📄
├── output/                  ← Resultados aqui 📊
├── ragtest/                 ← Config RAG
├── README.md                ← Documentação completa
└── CORRECTIONS.md           ← Correções feitas
```

## 💡 Dicas

- **Primeira vez**: Pode levar alguns minutos para indexar
- **Múltiplos arquivos**: A indexação é acumulativa
- **Modelos**: Cada modelo tem características diferentes:
  - qwen2:8b = melhor qualidade, mais lento (~12GB RAM)
  - mistral = boa qualidade, rápido (~7GB RAM)
  - neural-chat = muito rápido, qualidade ok (~4GB RAM)

## 🎯 Próximas Melhorias

Depois de começar, você pode:
- Adicionar mais documentos
- Testar diferentes modelos  
- Ajustar `settings.yaml`
- Explorar diferentes métodos de busca

## 📖 Recursos Úteis

- [GraphRAG Doc](https://microsoft.github.io/graphrag/)
- [Streamlit Doc](https://docs.streamlit.io/)
- [Ollama Models](https://ollama.ai/library)

---

**Criado**: 2026-06-11  
**Status**: ✅ Pronto para uso  
**Python**: 3.12.0  
**GraphRAG**: 3.0+  

Divirta-se! 🎉
