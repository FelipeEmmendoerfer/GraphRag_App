import streamlit as st
from pathlib import Path
import os
import pandas as pd
from indexer import DocumentIndexManager
from engine import QueryEngine
from graph_visualizer import GraphVisualizer
from datetime import datetime
import json

# ─── Page Configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="GraphRAG Interface",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Custom CSS - Modern Dark Theme ──────────────────────────────────────────
st.markdown("""
<style>
/* ===== GLOBAL STYLES ===== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
}

[data-testid="stHeader"] {
    background: transparent;
}

/* ===== TYPOGRAPHY ===== */
h1, h2, h3, h4, h5, h6, p, span, div, label {
    font-family: 'Inter', sans-serif !important;
}

/* ===== TAB STYLING ===== */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255, 255, 255, 0.03);
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
    border: 1px solid rgba(255, 255, 255, 0.06);
}

.stTabs [data-baseweb="tab"] {
    font-size: 14px;
    font-weight: 500;
    padding: 10px 24px;
    color: #8892a4;
    border-radius: 8px;
    transition: all 0.3s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #c8d0e0;
    background: rgba(255, 255, 255, 0.05);
}

.stTabs [aria-selected="true"] {
    color: #ffffff !important;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border-bottom: none !important;
    font-weight: 600;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

/* ===== BUTTON STYLING ===== */
.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    font-size: 14px;
    padding: 8px 20px;
    border: 1px solid rgba(102, 126, 234, 0.3);
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
    color: #c8d0e0;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    border-color: #667eea;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.25) 0%, rgba(118, 75, 162, 0.25) 100%);
    color: #ffffff;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.2);
    transform: translateY(-1px);
}

/* ===== METRIC CARDS ===== */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, rgba(30, 30, 60, 0.8) 0%, rgba(40, 40, 80, 0.6) 100%);
    border: 1px solid rgba(102, 126, 234, 0.15);
    border-radius: 14px;
    padding: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    transition: all 0.3s ease;
}

[data-testid="metric-container"]:hover {
    border-color: rgba(102, 126, 234, 0.4);
    box-shadow: 0 6px 25px rgba(102, 126, 234, 0.15);
    transform: translateY(-2px);
}

/* ===== CONTAINERS / CARDS ===== */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px !important;
    border-color: rgba(255, 255, 255, 0.06) !important;
    background: rgba(255, 255, 255, 0.02) !important;
}

/* ===== FILE UPLOADER ===== */
[data-testid="stFileUploader"] {
    border-radius: 12px;
}

[data-testid="stFileUploader"] > div {
    border-radius: 12px;
    border: 2px dashed rgba(102, 126, 234, 0.3);
    background: rgba(102, 126, 234, 0.03);
}

/* ===== TEXT INPUT ===== */
.stTextInput > div > div {
    border-radius: 10px;
    border-color: rgba(102, 126, 234, 0.2);
    background: rgba(255, 255, 255, 0.03);
}

.stTextInput > div > div:focus-within {
    border-color: #667eea;
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

/* ===== SELECT BOX ===== */
.stSelectbox > div > div {
    border-radius: 10px;
    border-color: rgba(102, 126, 234, 0.2);
    background: rgba(255, 255, 255, 0.03);
}

/* ===== EXPANDER ===== */
.streamlit-expanderHeader {
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.03);
}

/* ===== DIVIDER ===== */
hr {
    border-color: rgba(102, 126, 234, 0.15) !important;
}

/* ===== SUCCESS/ERROR/WARNING/INFO MESSAGES ===== */
.stAlert {
    border-radius: 10px;
}

/* ===== DATAFRAME ===== */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
}

/* ===== CHAT MESSAGES ===== */
.chat-message {
    background: linear-gradient(135deg, rgba(30, 30, 60, 0.6) 0%, rgba(40, 40, 80, 0.4) 100%);
    border: 1px solid rgba(102, 126, 234, 0.1);
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 12px;
}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.02);
}

::-webkit-scrollbar-thumb {
    background: rgba(102, 126, 234, 0.3);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(102, 126, 234, 0.5);
}

/* ===== HEADER STYLING ===== */
.main-header {
    text-align: center;
    padding: 20px 0 10px 0;
}

.main-header h1 {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 4px;
}

.main-header p {
    color: #8892a4;
    font-size: 1rem;
    font-weight: 300;
}

/* ===== FILE LIST ITEM ===== */
.file-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 14px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    margin-bottom: 6px;
    transition: all 0.2s ease;
}

.file-item:hover {
    border-color: rgba(102, 126, 234, 0.3);
    background: rgba(102, 126, 234, 0.05);
}

/* ===== GRAPH STATS CARD ===== */
.stats-card {
    background: linear-gradient(135deg, rgba(30, 30, 60, 0.8) 0%, rgba(40, 40, 80, 0.6) 100%);
    border: 1px solid rgba(102, 126, 234, 0.15);
    border-radius: 14px;
    padding: 20px;
    margin: 8px 0;
}
</style>
""", unsafe_allow_html=True)

# ─── Initialize Session State ─────────────────────────────────────────────────
if 'manager' not in st.session_state:
    st.session_state.manager = DocumentIndexManager(input_dir="input")
if 'engine' not in st.session_state:
    st.session_state.engine = QueryEngine()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'visualizer' not in st.session_state:
    st.session_state.visualizer = GraphVisualizer()

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🧠 GraphRAG Interface</h1>
    <p>Sistema de Recuperação Aumentada por Grafos de Conhecimento</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "⚙️ Configuração",
    "💬 Chat",
    "📊 Status",
    "🌐 Grafo"
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: CONFIGURAÇÃO
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.header("📂 Gerenciamento de Documentos")
    st.caption("Faça upload de arquivos, gerencie documentos e execute a indexação.")
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.subheader("📤 Upload de Arquivos")
        uploaded_files = st.file_uploader(
            "Arraste ou selecione arquivos para indexar",
            type=["txt", "pdf", "docx"],
            accept_multiple_files=True,
            help="Formatos suportados: TXT, PDF, DOCX"
        )
        if uploaded_files:
            input_dir = Path("input")
            input_dir.mkdir(exist_ok=True)
            for file in uploaded_files:
                try:
                    file_path = input_dir / file.name
                    with open(file_path, "wb") as f:
                        f.write(file.getbuffer())
                    st.success(f"✅ {file.name} salvo com sucesso")
                except Exception as e:
                    st.error(f"❌ Erro ao salvar {file.name}: {str(e)}")
    
    with col2:
        st.subheader("📋 Arquivos no Sistema")
        files = st.session_state.manager.get_indexed_files()
        
        if files:
            for f in files:
                col_name, col_size, col_del = st.columns([3, 1, 1])
                with col_name:
                    st.markdown(f"📄 **{f['name']}**")
                with col_size:
                    st.caption(f"{f['size_kb']} KB")
                with col_del:
                    if st.button("🗑️", key=f"del_{f['name']}", help=f"Excluir {f['name']}"):
                        success, msg = st.session_state.manager.delete_file(f['name'])
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
        else:
            st.info("📭 Nenhum arquivo encontrado. Faça upload para começar.")
    
    st.markdown("---")
    
    # Indexing controls
    st.subheader("🚀 Indexação")
    col_idx1, col_idx2, col_idx3 = st.columns([2, 1, 1])
    
    with col_idx1:
        if st.button("🚀 Indexar Documentos", use_container_width=True, type="primary"):
            with st.spinner("⏳ Indexando documentos... Isso pode levar alguns minutos."):
                try:
                    input_files = list(Path("input").glob("*"))
                    if not input_files:
                        st.warning("⚠️ Nenhum documento encontrado na pasta input/")
                    else:
                        st.info(f"📄 Processando {len(input_files)} arquivo(s)...")
                        success = st.session_state.manager.run_indexing()
                        if success:
                            st.success("✅ Indexação concluída com sucesso!")
                            st.balloons()
                            st.info("💡 Agora você pode fazer buscas na aba 'Chat'")
                        else:
                            st.error("❌ Erro durante indexação. Verifique:")
                            st.markdown("""
                            1. Se há arquivos válidos em `input/`
                            2. Se o Ollama está rodando (`localhost:11434`)
                            3. Se os modelos estão baixados (`ollama pull qwen3:8b`)
                            """)
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
    
    with col_idx2:
        if st.button("🧹 Limpar Índice", use_container_width=True):
            success, msg = st.session_state.manager.clear_index()
            if success:
                st.success(msg)
            else:
                st.error(msg)
    
    with col_idx3:
        status = st.session_state.manager.get_status()
        if "atualizado" in status.lower():
            st.success(f"🟢 {status}")
        elif "alterações" in status.lower():
            st.warning(f"🟡 {status}")
        else:
            st.info(f"🔵 {status}")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: CHAT
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.header("💬 Chat RAG")
    st.caption("Faça perguntas sobre seus documentos indexados.")
    
    # Search configuration
    col_method, col_spacer = st.columns([1, 2])
    with col_method:
        search_method = st.selectbox(
            "Método de Busca",
            ["local", "global", "drift", "basic"],
            help="Local: busca focada | Global: visão ampla | Drift: exploratória | Basic: simples"
        )
    
    # Query input
    user_query = st.text_input(
        "💭 Sua pergunta:",
        placeholder="Digite sua pergunta sobre os documentos indexados...",
        label_visibility="visible"
    )
    
    col_search, col_clear = st.columns([3, 1])
    with col_search:
        search_button = st.button("🔍 Buscar Resposta", use_container_width=True, type="primary")
    with col_clear:
        if st.button("🗑️ Limpar Histórico", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    if search_button and user_query:
        with st.spinner("🔍 Buscando resposta..."):
            try:
                output_dir = Path("./ragtest/output")
                has_index = output_dir.exists() and bool(list(output_dir.rglob("*.parquet")))
                
                if not has_index:
                    st.warning("⚠️ Nenhum índice encontrado. Primeiro indexe os documentos em '⚙️ Configuração'")
                else:
                    result = st.session_state.engine.query(user_query, method=search_method)
                    
                    if result.get("response", "").startswith("❌"):
                        st.error(result['response'])
                    else:
                        st.session_state.chat_history.append({
                            "query": user_query,
                            "response": result.get("response", "Sem resposta"),
                            "method": search_method,
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                            "context": result.get("context", None)
                        })
                        st.success("✅ Resposta encontrada!")
            except Exception as e:
                st.error(f"❌ Erro na busca: {str(e)}")
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("---")
        st.subheader("📝 Histórico de Conversas")
        
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.container(border=True):
                st.markdown(f"**🧑 Pergunta:** {chat['query']}")
                st.divider()
                st.markdown(chat['response'])
                
                col_info1, col_info2, col_info3 = st.columns(3)
                with col_info1:
                    st.caption(f"🔍 Método: `{chat['method']}`")
                with col_info2:
                    st.caption(f"🕐 {chat['timestamp']}")
                with col_info3:
                    st.caption(f"#{len(st.session_state.chat_history) - i}")
                
                if chat.get('context'):
                    with st.expander("📚 Ver Contexto Recuperado"):
                        st.code(chat['context'], language=None)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: STATUS
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.header("📊 Dashboard de Status")
    st.caption("Visão geral do estado do sistema e dos dados indexados.")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        num_files = len(list(Path("input").glob("*")))
    except Exception:
        num_files = 0
    
    output_dir = Path("./ragtest/output")
    index_exists = output_dir.exists() and bool(list(output_dir.rglob("*.parquet")))
    
    with col1:
        st.metric(
            "🟢 Status do Índice",
            "Indexado" if index_exists else "Sem índice",
            delta="Pronto" if index_exists else "Pendente",
            delta_color="normal" if index_exists else "off"
        )
    with col2:
        st.metric("📄 Documentos", num_files)
    with col3:
        st.metric("💬 Conversas", len(st.session_state.chat_history))
    with col4:
        st.metric("🔖 Versão", "3.1.0")
    
    st.markdown("---")
    
    # Detailed status
    col_detail1, col_detail2 = st.columns(2)
    
    with col_detail1:
        st.subheader("📁 Detalhes dos Arquivos")
        files = st.session_state.manager.get_indexed_files()
        if files:
            df_files = pd.DataFrame(files)
            if 'modified' in df_files.columns:
                df_files['modified'] = pd.to_datetime(df_files['modified'], unit='s').dt.strftime('%d/%m/%Y %H:%M')
            if 'path' in df_files.columns:
                df_files = df_files.drop(columns=['path'])
            if 'error' in df_files.columns:
                df_files = df_files.drop(columns=['error'], errors='ignore')
            df_files.columns = ['Arquivo', 'Tamanho (KB)', 'Modificado']
            st.dataframe(df_files, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum arquivo no sistema.")
    
    with col_detail2:
        st.subheader("🔧 Estado do Sistema")
        
        # Check index files
        if index_exists:
            parquet_files = list(output_dir.rglob("*.parquet"))
            st.success(f"✅ Índice ativo com {len(parquet_files)} arquivo(s) parquet")
            
            # Show parquet file details
            parquet_info = []
            for pf in parquet_files[:10]:
                size_kb = pf.stat().st_size / 1024
                parquet_info.append({
                    "Arquivo": pf.name,
                    "Tamanho (KB)": round(size_kb, 1)
                })
            if parquet_info:
                st.dataframe(pd.DataFrame(parquet_info), use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Nenhum índice encontrado. Execute a indexação na aba Configuração.")
        
        # System info
        st.markdown("---")
        st.caption("ℹ️ Informações do Sistema")
        st.markdown(f"""
        - **Motor:** GraphRAG 3.0+
        - **LLM:** Ollama (qwen3:8b)
        - **Embeddings:** nomic-embed-text
        - **Diretório de entrada:** `input/`
        - **Diretório de saída:** `ragtest/output/`
        """)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4: GRAFO
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.header("🌐 Visualização do Grafo de Conhecimento")
    st.caption("Explore as entidades e relacionamentos extraídos dos seus documentos.")
    
    # Refresh button
    col_refresh, col_spacer2 = st.columns([1, 3])
    with col_refresh:
        if st.button("🔄 Atualizar Grafo", use_container_width=True):
            st.session_state.visualizer = GraphVisualizer()
            st.rerun()
    
    # Check if index exists (corrigido: usar ragtest/output)
    output_dir = Path("./ragtest/output")
    if not output_dir.exists() or not list(output_dir.rglob("*.parquet")):
        st.warning("⚠️ Nenhum índice encontrado. Indexe documentos em '⚙️ Configuração' primeiro.")
        st.info("💡 Após a indexação, o grafo de conhecimento será gerado automaticamente a partir das entidades e relacionamentos extraídos.")
    else:
        # Get graph data
        graph_data = st.session_state.visualizer.extract_graph_data()
        
        if not graph_data or not graph_data.get("nodes"):
            st.info("📊 Nenhum dado de grafo encontrado nos arquivos de saída. Verifique se a indexação foi concluída corretamente.")
        else:
            # Summary metrics
            stats = graph_data.get("stats", {})
            col_g1, col_g2, col_g3, col_g4 = st.columns(4)
            with col_g1:
                st.metric("🔵 Entidades", stats.get('total_entities', 0))
            with col_g2:
                st.metric("🔗 Relacionamentos", stats.get('total_relationships', 0))
            with col_g3:
                st.metric("🏘️ Comunidades", stats.get('communities', 0))
            with col_g4:
                st.metric("📐 Grau Médio", f"{stats.get('avg_degree', 0):.2f}")
            
            st.markdown("---")
            
            # Display in columns
            col_left, col_right = st.columns([1, 1], gap="large")
            
            with col_left:
                st.subheader("🏆 Principais Entidades")
                top_entities = st.session_state.visualizer.get_top_entities(n=15)
                if top_entities:
                    entity_df = pd.DataFrame(top_entities, columns=["Entidade", "Conexões"])
                    st.bar_chart(entity_df.set_index("Entidade"), height=400)
                else:
                    st.info("Sem dados de entidades")
            
            with col_right:
                st.subheader("📊 Distribuição de Conexões")
                if graph_data.get("edges"):
                    # Calculate degree distribution
                    degree = {}
                    for edge in graph_data["edges"]:
                        degree[edge["source"]] = degree.get(edge["source"], 0) + 1
                        degree[edge["target"]] = degree.get(edge["target"], 0) + 1
                    
                    degree_values = list(degree.values())
                    if degree_values:
                        degree_df = pd.DataFrame({"Grau": degree_values})
                        st.bar_chart(degree_df["Grau"].value_counts().sort_index(), height=400)
                else:
                    st.info("Sem dados de arestas")
            
            st.markdown("---")
            
            # Data tables
            st.subheader("📋 Dados do Grafo")
            
            data_tab1, data_tab2 = st.tabs(["🔵 Entidades (Nós)", "🔗 Relacionamentos (Arestas)"])
            
            with data_tab1:
                if graph_data.get("nodes"):
                    nodes_df = pd.DataFrame(graph_data["nodes"][:50])
                    st.dataframe(nodes_df, use_container_width=True, hide_index=True)
                    st.caption(f"Exibindo {min(50, len(graph_data['nodes']))} de {len(graph_data['nodes'])} entidades")
                else:
                    st.info("Sem dados de nós")
            
            with data_tab2:
                if graph_data.get("edges"):
                    edges_df = pd.DataFrame(graph_data["edges"][:50])
                    st.dataframe(edges_df, use_container_width=True, hide_index=True)
                    st.caption(f"Exibindo {min(50, len(graph_data['edges']))} de {len(graph_data['edges'])} relacionamentos")
                else:
                    st.info("Sem dados de arestas")

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #555; font-size: 12px;'>"
    "GraphRAG Interface v3.1.0 | Powered by Microsoft GraphRAG + Ollama"
    "</div>",
    unsafe_allow_html=True
)
