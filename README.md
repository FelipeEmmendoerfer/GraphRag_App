# 🔍 GraphRAG Interface

Um sistema RAG (Retrieval Augmented Generation) baseado em GraphRAG com interface Streamlit para busca e análise de documentos usando LLMs locais.

## ✨ Features

- 📤 **Upload de Documentos**: Suporte para TXT, PDF e DOCX
- 🔍 **Múltiplos Métodos de Busca**: Local, Global, Drift e Basic
- 💬 **Interface de Chat**: Conversa com seus documentos
- 📊 **Dashboard de Status**: Monitoramento em tempo real
- ⚡ **Processamento Local**: Use Ollama para LLMs locais

## 🛠️ Requisitos

- **Python**: 3.10-3.12 (recomendado 3.12)
- **Ollama**: Serviço local rodando em `localhost:11434`
- **Modelos Ollama**:
  - `nomic-embed-text` (embeddings)
  - `qwen2:8b` (LLM principal) ou outro modelo

## 📦 Instalação

### 1. Clonar e configurar

```bash
cd meu_projeto
```

### 2. Criar ambiente virtual (se necessário)

```bash
python -m venv .venv
.\.venv\Scripts\activate  # Windows
# ou
source .venv/bin/activate  # Linux/Mac
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Verificar ambiente

```bash
python verify.py
```

## 🚀 Como Usar

### 1. Iniciar Ollama

```bash
ollama serve
```

Em outro terminal:
```bash
ollama pull nomic-embed-text
ollama pull qwen2:8b
```

### 2. Iniciar a aplicação

```bash
streamlit run app.py
```

A interface estará disponível em: `http://localhost:8501`

## 📋 Como Usar a Interface

### Aba "Configuração"
- Upload de arquivos para análise
- Visualização de documentos carregados
- Botão para iniciar indexação dos documentos

### Aba "Chat"
- Selecione o método de busca
- Digite sua pergunta
- Receba respostas com contexto dos documentos

### Aba "Status"
- Visualize métricas do sistema
- Status de indexação
- Histórico de conversas

## 📁 Estrutura do Projeto

```
meu_projeto/
├── app.py                    # Interface Streamlit principal
├── engine.py                 # Motor de busca com GraphRAG
├── indexer.py                # Gerenciador de indexação
├── verify.py                 # Script de verificação
├── settings.yaml             # Configuração do GraphRAG
├── requirements.txt          # Dependências Python
├── input/                    # Documentos para análise
├── output/                   # Resultados gerados
└── ragtest/                  # Configurações do RAG
```

## ⚙️ Configuração

### settings.yaml

Configure o comportamento do GraphRAG em `settings.yaml`:

```yaml
llm:
  type: ollama
  model: qwen2:8b
  
embeddings:
  type: ollama
  model: nomic-embed-text

search:
  method: local  # local, global, drift, basic
  top_k: 10
```

## 🔧 Troubleshooting

### Erro: "Ollama Service not found"

```bash
# Verificar se Ollama está rodando
ollama serve

# Em outro terminal, testar conexão
curl http://localhost:11434
```

### Erro: "Module not found"

```bash
pip install -r requirements.txt --upgrade
```

### Erro: "Python version incompatible"

Instale Python 3.12:
- [python.org](https://www.python.org/downloads/)
- Ou use Conda: `conda create -n graphrag python=3.12`

## 📚 Métodos de Busca

- **Local**: Busca em entidades locais e comunidades do grafo
- **Global**: Análise global dos dados com sumarização
- **Drift**: Reduz desvio através de votação múltipla
- **Basic**: Busca simples e rápida por similaridade

## 🐛 Problemas Conhecidos

1. Primeira indexação pode levar tempo (depende do tamanho dos documentos)
2. Modelos Ollama precisam ser baixados manualmente
3. Python 3.14+ não é suportado ainda por graphrag

## 📝 Logs

Consulte os logs para diagnosticar problemas:

```bash
# Logs da aplicação
.venv/Lib/site-packages/graphrag/logs
```

## 🤝 Contribuindo

Para reportar erros ou sugerir melhorias:
1. Verifique o arquivo TROUBLESHOOTING.md
2. Execute `python verify.py` para diagnosticar
3. Compartilhe os logs relevantes

## 📄 Licença

MIT License - veja LICENSE.md

## 📖 Recursos

- [GraphRAG Docs](https://microsoft.github.io/graphrag/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [Ollama](https://ollama.ai/)