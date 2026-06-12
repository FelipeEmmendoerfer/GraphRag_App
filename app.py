import streamlit as st
from pathlib import Path
import os
from indexer import DocumentIndexManager
from engine import QueryEngine
from graph_visualizer import GraphVisualizer
from datetime import datetime
import json

st.set_page_config(page_title="GraphRAG Interface", layout="wide")

# Initialize session state
if 'manager' not in st.session_state:
    st.session_state.manager = DocumentIndexManager(input_dir="input")
if 'engine' not in st.session_state:
    st.session_state.engine = QueryEngine()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'visualizer' not in st.session_state:
    st.session_state.visualizer = GraphVisualizer()

st.title("🔍 GraphRAG Interface")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["⚙️ Configuração", "💬 Chat", "📊 Status", "🌐 Gráfo"])

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
                    input_files = list(Path("input").glob("*"))
                    if not input_files:
                        st.warning("⚠️ Nenhum documento encontrado em input/")
                    else:
                        st.info(f"📄 Indexando {len(input_files)} arquivo(s)...")
                        success = st.session_state.manager.run_indexing()
                        if success:
                            st.success("✅ Indexação concluída com sucesso!")
                            st.info("💡 Agora você pode fazer buscas na aba 'Chat'")
                        else:
                            st.error("❌ Erro durante indexação. Verifique:")
                            st.error("1. Se há arquivos em input/")
                            st.error("2. Se o Ollama está rodando (localhost:11434)")
                            st.error("3. Se os modelos estão baixados (ollama pull qwen2:8b)")
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
                    st.error(f"Detalhes: {type(e).__name__}")
    
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
                # Verificar se index existe
                if not Path("./output").exists() or not list(Path("./output").glob("*")):
                    st.warning("⚠️ Nenhum índice encontrado. Primeiro indexe os documentos em '⚙️ Configuração'")
                else:
                    result = st.session_state.engine.query(user_query, method=search_method)
                    
                    if "Error" in result.get("response", ""):
                        st.error(f"❌ Erro na busca: {result['response']}")
                    else:
                        st.session_state.chat_history.append({
                            "query": user_query, 
                            "response": result.get("response", "Sem resposta"), 
                            "method": search_method, 
                            "timestamp": datetime.now().strftime("%H:%M:%S"), 
                            "context": result.get("context", None)
                        })
                        st.success("✅ Resposta encontrada!")
                        st.rerun()
            except Exception as e:
                st.error(f"❌ Erro na busca: {str(e)}")
                st.error(f"Certifique-se de:")
                st.error("1. Ter documentos indexados")
                st.error("2. Ollama estar rodando")
                st.error("3. Modelo estar disponível")
    
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

with tab4:
    st.header("🌐 Visualização do Gráfo de Conhecimento")
    
    # Refresh button
    if st.button("🔄 Atualizar Gráfo", use_container_width=True):
        st.session_state.visualizer = GraphVisualizer()
        st.rerun()
    
    # Check if index exists
    output_dir = Path("./output")
    if not output_dir.exists():
        st.warning("⚠️ Nenhum índice encontrado. Indexe documentos em '⚙️ Configuração' primeiro.")
    else:
        # Get graph data
        graph_data = st.session_state.visualizer.extract_graph_data()
        
        if not graph_data or not graph_data.get("nodes"):
            st.info("📊 Aguardando dados do gráfo...")
        else:
            # Display summary
            st.markdown(st.session_state.visualizer.get_graph_summary())
            
            st.markdown("---")
            
            # Display in columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔝 Principais Entidades")
                top_entities = st.session_state.visualizer.get_top_entities(n=10)
                if top_entities:
                    entity_df = {
                        "Entidade": [e[0] for e in top_entities],
                        "Grau": [e[1] for e in top_entities]
                    }
                    import pandas as pd
                    st.bar_chart(pd.DataFrame(entity_df).set_index("Entidade"))
                else:
                    st.info("Sem dados de entidades")
            
            with col2:
                st.subheader("📈 Estatísticas do Gráfo")
                stats = graph_data.get("stats", {})
                stats_text = f"""
                - **Entidades (nós):** {stats.get('total_entities', 0)}
                - **Relacionamentos (arestas):** {stats.get('total_relationships', 0)}
                - **Comunidades:** {stats.get('communities', 0)}
                - **Grau Médio:** {stats.get('avg_degree', 0):.2f}
                """
                st.markdown(stats_text)
            
            st.markdown("---")
            
            # Display sample nodes and edges
            st.subheader("📋 Amostra de Dados")
            
            sample_tabs = st.tabs(["Nós (Entidades)", "Arestas (Relacionamentos)"])
            
            with sample_tabs[0]:
                import pandas as pd
                if graph_data.get("nodes"):
                    nodes_df = pd.DataFrame(graph_data["nodes"][:20])  # Show first 20
                    st.dataframe(nodes_df, use_container_width=True)
                else:
                    st.info("Sem dados de nós")
            
            with sample_tabs[1]:
                import pandas as pd
                if graph_data.get("edges"):
                    edges_df = pd.DataFrame(graph_data["edges"][:20])  # Show first 20
                    st.dataframe(edges_df, use_container_width=True)
                else:
                    st.info("Sem dados de arestas")