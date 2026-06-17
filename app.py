import streamlit as st
from pathlib import Path
import os
import pandas as pd
from indexer import DocumentIndexManager
from engine import QueryEngine
from graph_visualizer import GraphVisualizer
from datetime import datetime
import json
import streamlit.components.v1 as components

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

[data-testid="stMetricLabel"] {
    color: #a0aec0 !important;
}

[data-testid="stMetricValue"] {
    color: #e2e8f0 !important;
}

/* ===== CONTAINERS / CARDS ===== */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px !important;
    border-color: rgba(255, 255, 255, 0.06) !important;
    background: rgba(255, 255, 255, 0.02) !important;
}

/* ===== FILE UPLOADER ===== */
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

/* ===== DIVIDER ===== */
hr {
    border-color: rgba(102, 126, 234, 0.15) !important;
}

/* ===== DATAFRAME - fix white background ===== */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
}

[data-testid="stDataFrame"] iframe {
    border-radius: 10px;
}

/* ===== CHARTS - fix white background ===== */
[data-testid="stVegaLiteChart"] {
    background: transparent !important;
    border-radius: 10px;
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
    <h1>GraphRAG Interface</h1>
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
        elif "alterações" in status.lower() or "re-indexação" in status.lower():
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
            "Status do Índice",
            "Indexado" if index_exists else "Sem índice",
            delta="Pronto" if index_exists else "Pendente",
            delta_color="normal" if index_exists else "off"
        )
    with col2:
        st.metric("Documentos", num_files)
    with col3:
        st.metric("Conversas", len(st.session_state.chat_history))
    with col4:
        st.metric("Versão", "3.2.0")
    
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
        
        if index_exists:
            parquet_files = list(output_dir.rglob("*.parquet"))
            st.success(f"✅ Índice ativo com {len(parquet_files)} arquivo(s) parquet")
            
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
        
        st.markdown("---")
        st.caption("ℹ️ Informações do Sistema")
        st.markdown("""
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
    
    # Check if index exists
    output_dir = Path("./ragtest/output")
    if not output_dir.exists() or not list(output_dir.rglob("*.parquet")):
        st.warning("⚠️ Nenhum índice encontrado. Indexe documentos em '⚙️ Configuração' primeiro.")
        st.info("💡 Após a indexação, o grafo de conhecimento será gerado automaticamente.")
    else:
        # Get graph data
        graph_data = st.session_state.visualizer.extract_graph_data()
        
        if not graph_data or not graph_data.get("nodes"):
            st.info("📊 Nenhum dado de grafo encontrado. Verifique se a indexação foi concluída corretamente.")
        else:
            # Summary metrics
            stats = graph_data.get("stats", {})
            col_g1, col_g2, col_g3, col_g4 = st.columns(4)
            with col_g1:
                st.metric("Entidades", stats.get('total_entities', 0))
            with col_g2:
                st.metric("Relacionamentos", stats.get('total_relationships', 0))
            with col_g3:
                st.metric("Comunidades", stats.get('communities', 0))
            with col_g4:
                st.metric("Grau Médio", f"{stats.get('avg_degree', 0):.2f}")
            
            st.markdown("---")
            
            # ─── VISUALIZAÇÃO INTERATIVA DO GRAFO (ESTILO GEPHI) ──────────────
            st.subheader("🔮 Visualização Interativa do Grafo")
            
            # Controls for the graph
            col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
            with col_ctrl1:
                physics_enabled = st.checkbox("Física (Force Atlas)", value=True, help="Ativar simulação de forças estilo Gephi")
            with col_ctrl2:
                show_labels = st.checkbox("Mostrar Labels", value=True)
            with col_ctrl3:
                graph_height = st.selectbox("Altura do Grafo", [500, 600, 700, 800, 900], index=2)
            
            # Build interactive graph with pyvis
            try:
                from pyvis.network import Network
                import networkx as nx
                
                # Create NetworkX graph first for layout
                G = nx.Graph()
                
                # Add nodes
                for node in graph_data["nodes"]:
                    G.add_node(node["id"], label=node["label"], title=node.get("description", ""))
                
                # Add edges
                for edge in graph_data["edges"]:
                    G.add_edge(edge["source"], edge["target"], 
                              weight=edge.get("weight", 1),
                              title=edge.get("relationship", ""))
                
                # Create Pyvis network
                net = Network(
                    height=f"{graph_height}px",
                    width="100%",
                    bgcolor="#0f0f1a",
                    font_color="#e2e8f0",
                    directed=False
                )
                
                # Configure physics (Force Atlas 2 style - like Gephi)
                if physics_enabled:
                    net.set_options("""
                    {
                        "physics": {
                            "enabled": true,
                            "forceAtlas2Based": {
                                "gravitationalConstant": -80,
                                "centralGravity": 0.01,
                                "springLength": 120,
                                "springConstant": 0.08,
                                "damping": 0.4,
                                "avoidOverlap": 0.8
                            },
                            "solver": "forceAtlas2Based",
                            "stabilization": {
                                "enabled": true,
                                "iterations": 200,
                                "updateInterval": 25
                            }
                        },
                        "nodes": {
                            "font": {
                                "size": 12,
                                "color": "#e2e8f0",
                                "face": "Inter, sans-serif"
                            },
                            "borderWidth": 2,
                            "borderWidthSelected": 4,
                            "shadow": {
                                "enabled": true,
                                "color": "rgba(102, 126, 234, 0.3)",
                                "size": 10
                            }
                        },
                        "edges": {
                            "color": {
                                "color": "rgba(102, 126, 234, 0.4)",
                                "highlight": "#667eea",
                                "hover": "#764ba2"
                            },
                            "smooth": {
                                "enabled": true,
                                "type": "continuous"
                            },
                            "width": 1.5
                        },
                        "interaction": {
                            "hover": true,
                            "tooltipDelay": 200,
                            "navigationButtons": true,
                            "keyboard": {
                                "enabled": true
                            },
                            "zoomView": true,
                            "dragView": true
                        }
                    }
                    """)
                else:
                    net.set_options("""
                    {
                        "physics": {
                            "enabled": false
                        },
                        "nodes": {
                            "font": {
                                "size": 12,
                                "color": "#e2e8f0",
                                "face": "Inter, sans-serif"
                            },
                            "borderWidth": 2,
                            "shadow": {
                                "enabled": true,
                                "color": "rgba(102, 126, 234, 0.3)",
                                "size": 10
                            }
                        },
                        "edges": {
                            "color": {
                                "color": "rgba(102, 126, 234, 0.4)",
                                "highlight": "#667eea",
                                "hover": "#764ba2"
                            },
                            "smooth": {
                                "enabled": true,
                                "type": "continuous"
                            },
                            "width": 1.5
                        },
                        "interaction": {
                            "hover": true,
                            "tooltipDelay": 200,
                            "navigationButtons": true,
                            "keyboard": {
                                "enabled": true
                            }
                        }
                    }
                    """)
                
                # Calculate degree for node sizing
                degree_dict = dict(G.degree())
                max_degree = max(degree_dict.values()) if degree_dict else 1
                
                # Color palette (Gephi-style community colors)
                colors = [
                    "#667eea", "#764ba2", "#f093fb", "#4fd1c5", "#f6ad55",
                    "#fc8181", "#68d391", "#63b3ed", "#b794f4", "#fbb6ce",
                    "#9ae6b4", "#fbd38d", "#bee3f8", "#c4b5fd", "#a3e635"
                ]
                
                # Add nodes with size based on degree
                for node in graph_data["nodes"]:
                    node_id = node["id"]
                    degree = degree_dict.get(node_id, 1)
                    size = 10 + (degree / max_degree) * 40  # Scale between 10 and 50
                    
                    # Assign color based on type or hash
                    color_idx = hash(node.get("type", node_id)) % len(colors)
                    color = colors[color_idx]
                    
                    tooltip = f"<b>{node['label']}</b><br>"
                    tooltip += f"Tipo: {node.get('type', 'N/A')}<br>"
                    tooltip += f"Conexões: {degree}<br>"
                    if node.get("description"):
                        tooltip += f"<br>{node['description']}"
                    
                    net.add_node(
                        node_id,
                        label=node["label"] if show_labels else "",
                        size=size,
                        color={
                            "background": color,
                            "border": color,
                            "highlight": {"background": "#ffffff", "border": color}
                        },
                        title=tooltip,
                        font={"size": max(8, int(8 + degree * 2)), "color": "#e2e8f0"}
                    )
                
                # Add edges
                for edge in graph_data["edges"]:
                    tooltip = edge.get("relationship", "")
                    weight = edge.get("weight", 1)
                    net.add_edge(
                        edge["source"],
                        edge["target"],
                        title=tooltip,
                        width=min(1 + weight * 0.5, 5)
                    )
                
                # Generate HTML
                html_path = Path("graph_viz.html")
                net.save_graph(str(html_path))
                
                # Read and display the HTML
                with open(html_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
                
                # Embed in Streamlit
                components.html(html_content, height=graph_height + 50, scrolling=False)
                
                st.caption(f"🖱️ Arraste nós para reorganizar | Scroll para zoom | Clique para selecionar | Hover para detalhes")
                
            except ImportError:
                st.error("❌ Biblioteca pyvis não encontrada. Instale com: `pip install pyvis networkx`")
            except Exception as e:
                st.error(f"❌ Erro ao gerar visualização: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
            
            st.markdown("---")
            
            # ─── TABELAS DE DADOS ─────────────────────────────────────────────
            st.subheader("📋 Dados do Grafo")
            
            data_tab1, data_tab2 = st.tabs(["🔵 Entidades (Nós)", "🔗 Relacionamentos (Arestas)"])
            
            with data_tab1:
                if graph_data.get("nodes"):
                    nodes_display = []
                    for node in graph_data["nodes"][:50]:
                        nodes_display.append({
                            "Entidade": node["label"],
                            "Tipo": node.get("type", "N/A"),
                            "Descrição": node.get("description", "")[:100]
                        })
                    st.dataframe(pd.DataFrame(nodes_display), use_container_width=True, hide_index=True)
                    st.caption(f"Exibindo {min(50, len(graph_data['nodes']))} de {len(graph_data['nodes'])} entidades")
                else:
                    st.info("Sem dados de nós")
            
            with data_tab2:
                if graph_data.get("edges"):
                    edges_display = []
                    for edge in graph_data["edges"][:50]:
                        edges_display.append({
                            "Origem": edge["source"],
                            "Destino": edge["target"],
                            "Relação": edge.get("relationship", "N/A"),
                            "Peso": edge.get("weight", 1)
                        })
                    st.dataframe(pd.DataFrame(edges_display), use_container_width=True, hide_index=True)
                    st.caption(f"Exibindo {min(50, len(graph_data['edges']))} de {len(graph_data['edges'])} relacionamentos")
                else:
                    st.info("Sem dados de arestas")

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #555; font-size: 12px; padding: 10px 0;'>"
    "GraphRAG Interface v3.2.0 | Powered by Microsoft GraphRAG + Ollama"
    "</div>",
    unsafe_allow_html=True
)
