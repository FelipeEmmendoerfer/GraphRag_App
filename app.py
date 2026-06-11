import streamlit as st
from pathlib import Path
import os
from indexer import IndexManager
from engine import QueryEngine
from datetime import datetime
import json

st.set_page_config(page_title="GraphRAG Interface", layout="wide")

# Initialize session state
if 'manager' not in st.session_state:
    st.session_state.manager = IndexManager(input_dir="input")
if 'engine' not in st.session_state:
    st.session_state.engine = QueryEngine()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

st.title("🔍 GraphRAG Interface")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["⚙️ Configuração", "💬 Chat", "📊 Status"])

with tab1:
    st.header("Gerenciamento de Documentos")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📤 Upload de Arquivos")
        uploaded_files = st.file_uploader(
            "Selecione arquivos para indexar", 
            type=["txt", "pdf", "docx"], 
            accept_multiple_files=True
        )
        if uploaded_files:
            input_dir = Path("input")
            input_dir.mkdir(exist_ok=True)
            for file in uploaded_files:
                try:
                    file_path = input_dir / file.name
                    with open(file_path, "wb") as f:
                        f.write(file.getbuffer())
                    st.success(f"✅ {file.name} salvo")
                except Exception as e:
                    st.error(f"❌ Erro ao salvar {file.name}: {str(e)}")
    
    with col2:
        st.subheader("📋 Arquivos Atuais")
        input_dir = Path("input")
        input_dir.mkdir(exist_ok=True)
        files = list(input_dir.glob("*"))
        if files:
            for f in files:
                try:
                    size_kb = f.stat().st_size / 1024
                    st.write(f"📄 {f.name} ({size_kb:.1f} KB)")
                except Exception as e:
                    st.write(f"📄 {f.name} (erro ao ler tamanho)")
        else:
            st.info("Nenhum arquivo encontrado")
    
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🚀 Indexar Agora", use_container_width=True):
            with st.spinner("Indexando documentos..."):
                try:
                    success = st.session_state.manager.run_indexing()
                    if success:
                        st.success("✅ Indexação concluída com sucesso!")
                    else:
                        st.error("❌ Erro durante indexação. Verifique os logs.")
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
    
    with col2:
        status = st.session_state.manager.get_status()
        st.info(status)

with tab2:
    st.header("Chat RAG")
    search_method = st.selectbox("Método de Busca", ["local", "global", "drift", "basic"])
    user_query = st.text_input(
        "Sua pergunta:", 
        placeholder="Digite sua pergunta sobre os documentos..."
    )
    
    col1, col2 = st.columns([2, 1])
    with col1:
        search_button = st.button("🔍 Buscar", use_container_width=True)
    with col2:
        if st.button("🗑️ Limpar", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    if search_button and user_query:
        with st.spinner("Buscando resposta..."):
            try:
                result = st.session_state.engine.query(user_query, method=search_method)
                st.session_state.chat_history.append({
                    "query": user_query, 
                    "response": result.get("response", "Sem resposta"), 
                    "method": search_method, 
                    "timestamp": datetime.now().strftime("%H:%M:%S"), 
                    "context": result.get("context", None)
                })
            except Exception as e:
                st.error(f"Erro na busca: {str(e)}")
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("---")
        for chat in reversed(st.session_state.chat_history):
            with st.container(border=True):
                st.write(f"**Q:** {chat['query']}")
                st.write(f"**A:** {chat['response']}")
                st.caption(f"Método: {chat['method']} | Hora: {chat['timestamp']}")
                if chat.get('context'):
                    with st.expander("📚 Contexto Recuperado"):
                        st.write(chat['context'])

with tab3:
    st.header("Dashboard de Status")
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        num_files = len(list(Path("input").glob("*")))
    except:
        num_files = 0
    
    col1.metric("Status", "Pronto")
    col2.metric("Documentos", num_files)
    col3.metric("Conversas", len(st.session_state.chat_history))
    col4.metric("Versão", "3.0.1")