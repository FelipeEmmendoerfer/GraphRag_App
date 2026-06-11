import pandas as pd
import os
import logging

class GraphVisualizer:
    def __init__(self, output_dir="ragtest/output"):
        self.output_dir = output_dir
        self.base_path = os.path.join(output_dir, "create_base_entity_graph")
        logging.basicConfig(level=logging.INFO)

    def extract_graph_data(self):
        try:
            entities_path = os.path.join(self.base_path, "entities.parquet")
            relationships_path = os.path.join(self.base_path, "relationships.parquet")

            if not os.path.exists(entities_path) or not os.path.exists(relationships_path):
                return {}

            df_entities = pd.read_parquet(entities_path)
            df_relationships = pd.read_parquet(relationships_path)

            nodes = df_entities.to_dict(orient="records")
            edges = df_relationships.to_dict(orient="records")

            stats = {
                "total_entities": len(df_entities),
                "total_relationships": len(df_relationships),
                "communities": int(df_entities["community"].nunique()) if "community" in df_entities.columns else 0
            }

            return {"nodes": nodes, "edges": edges, "stats": stats}
        except Exception as e:
            logging.error(f"Error extracting graph data: {e}")
            return {}

    def get_graph_summary(self):
        data = self.extract_graph_data()
        if not data:
            return "No graph data available."
        
        stats = data.get("stats", {})
        return (f"Graph Summary:\n" 
                f"- Total Entities: {stats.get('total_entities', 0)}\n" 
                f"- Total Relationships: {stats.get('total_relationships', 0)}\n" 
                f"- Total Communities: {stats.get('communities', 0)}")