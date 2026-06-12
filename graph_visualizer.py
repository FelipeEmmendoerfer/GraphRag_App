import pandas as pd
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GraphVisualizer:

    def __init__(self, output_dir="./output"):
        self.output_dir = Path(output_dir)
        # GraphRAG 3.x salva parquet direto em output/ ou output/artifacts/
        # Busca nos dois locais
        self.artifacts_path = self.output_dir
    
    def extract_graph_data(self):

        try:

            if not self.data_path.exists():
                logger.warning(
                    f"Output path not found: {self.data_path}"
                )
                return {}

            entities_file = self.data_path / "entities.parquet"
            relationships_file = self.data_path / "relationships.parquet"

            if not entities_file.exists():
                logger.warning("entities.parquet não encontrado")
                return {}

            if not relationships_file.exists():
                logger.warning("relationships.parquet não encontrado")
                return {}

            df_entities = pd.read_parquet(entities_file)
            df_relationships = pd.read_parquet(relationships_file)

            nodes = []

            for _, row in df_entities.iterrows():

                label = str(
                    row.get(
                        "title",
                        row.get("name", row.get("id", ""))
                    )
                )

                nodes.append({
                    "id": str(row.get("id", label)),
                    "label": label,
                    "description": str(
                        row.get("description", "")
                    )[:200],
                    "size": 15
                })

            edges = []

            for _, row in df_relationships.iterrows():

                edges.append({
                    "source": str(
                        row.get("source", "")
                    ),
                    "target": str(
                        row.get("target", "")
                    ),
                    "label": str(
                        row.get("description", "")
                    ),
                    "weight": float(
                        row.get("weight", 1)
                    )
                })

            stats = {

                "total_entities": len(nodes),

                "total_relationships": len(edges),

                "communities":
                    int(df_entities["community"].nunique())
                    if "community" in df_entities.columns
                    else 0,

                "avg_degree":
                    round(
                        len(edges) /
                        max(len(nodes), 1),
                        2
                    )
            }

            return {
                "nodes": nodes,
                "edges": edges,
                "stats": stats
            }

        except Exception as e:

            logger.exception(e)

            return {
                "nodes": [],
                "edges": [],
                "stats": {}
            }

    def get_graph_summary(self):

        data = self.extract_graph_data()

        if not data.get("nodes"):

            return (
                "📊 Nenhum gráfico disponível.\n"
                "Execute uma indexação primeiro."
            )

        stats = data["stats"]

        return (
            f"📊 **Resumo do Grafo**\n\n"
            f"🔗 Entidades: {stats['total_entities']}\n\n"
            f"🎯 Relacionamentos: {stats['total_relationships']}\n\n"
            f"👥 Comunidades: {stats['communities']}\n\n"
            f"📈 Grau Médio: {stats['avg_degree']}"
        )

    def get_top_entities(self, n=10):

        data = self.extract_graph_data()

        edges = data.get("edges", [])

        degree_count = {}

        for edge in edges:

            source = edge["source"]
            target = edge["target"]

            degree_count[source] = (
                degree_count.get(source, 0) + 1
            )

            degree_count[target] = (
                degree_count.get(target, 0) + 1
            )

        return sorted(
            degree_count.items(),
            key=lambda x: x[1],
            reverse=True
        )[:n]

    def get_graph_json(self):

        return json.dumps(
            self.extract_graph_data(),
            ensure_ascii=False
        )