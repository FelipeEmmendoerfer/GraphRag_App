import pandas as pd
import os
import logging
import json
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GraphVisualizer:
    def __init__(self, output_dir="./output"):
        self.output_dir = Path(output_dir)
        self.artifacts_path = self.output_dir / "artifacts"
        
    def extract_graph_data(self):
        """Extract nodes and edges from GraphRAG output"""
        try:
            # Look for parquet files in artifacts
            if not self.artifacts_path.exists():
                logger.warning(f"Artifacts path not found: {self.artifacts_path}")
                return {}
            
            # Find entities and relationships files
            entities_file = None
            relationships_file = None
            
            for root, dirs, files in os.walk(self.artifacts_path):
                for file in files:
                    if 'entities' in file and file.endswith('.parquet'):
                        entities_file = os.path.join(root, file)
                    elif 'relationships' in file and file.endswith('.parquet'):
                        relationships_file = os.path.join(root, file)
            
            if not entities_file or not relationships_file:
                logger.info("Entities or relationships file not found")
                return {"nodes": [], "edges": [], "stats": {}}
            
            df_entities = pd.read_parquet(entities_file)
            df_relationships = pd.read_parquet(relationships_file)
            
            # Prepare nodes
            nodes = []
            for _, row in df_entities.iterrows():
                nodes.append({
                    "id": str(row.get("id", row.get("title", ""))),
                    "label": str(row.get("title", "")),
                    "size": min(30, 10 + len(str(row.get("description", "")))),
                    "description": str(row.get("description", ""))[:100]
                })
            
            # Prepare edges
            edges = []
            for _, row in df_relationships.iterrows():
                edges.append({
                    "source": str(row.get("source", "")),
                    "target": str(row.get("target", "")),
                    "label": str(row.get("description", "")),
                    "weight": row.get("weight", 1)
                })
            
            stats = {
                "total_entities": len(df_entities),
                "total_relationships": len(df_relationships),
                "communities": int(df_entities["community"].nunique()) if "community" in df_entities.columns else 0,
                "avg_degree": len(edges) / max(len(nodes), 1)
            }
            
            return {"nodes": nodes, "edges": edges, "stats": stats}
            
        except Exception as e:
            logger.error(f"Error extracting graph data: {e}")
            return {"nodes": [], "edges": [], "stats": {}}

    def get_graph_summary(self):
        """Get text summary of graph"""
        data = self.extract_graph_data()
        if not data or not data.get("nodes"):
            return "📊 Nenhum gráfico disponível ainda. Indexe um documento primeiro."
        
        stats = data.get("stats", {})
        return (f"📊 **Resumo do Gráfico:**\n" 
                f"- 🔗 Entidades: {stats.get('total_entities', 0)}\n" 
                f"- 🎯 Relacionamentos: {stats.get('total_relationships', 0)}\n" 
                f"- 👥 Comunidades: {stats.get('communities', 0)}\n"
                f"- 📈 Grau Médio: {stats.get('avg_degree', 0):.2f}")
    
    def get_top_entities(self, n=5):
        """Get top entities by degree"""
        data = self.extract_graph_data()
        edges = data.get("edges", [])
        
        if not edges:
            return []
        
        # Count degrees
        degree_count = {}
        for edge in edges:
            source = edge.get("source", "")
            target = edge.get("target", "")
            degree_count[source] = degree_count.get(source, 0) + 1
            degree_count[target] = degree_count.get(target, 0) + 1
        
        # Sort and return top n
        top_entities = sorted(degree_count.items(), key=lambda x: x[1], reverse=True)[:n]
        return [(name, count) for name, count in top_entities]
    
    def get_graph_json(self):
        """Return graph data as JSON for visualization libraries"""
        data = self.extract_graph_data()
        return json.dumps(data)