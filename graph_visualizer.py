import pandas as pd
import os
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GraphVisualizer:

    def __init__(self, output_dir="./ragtest/output"):
        self.output_dir = Path(output_dir)

    def extract_graph_data(self):

        try:

            if not self.output_dir.exists():
                logger.warning(
                    f"Output path not found: {self.output_dir}"
                )
                return {
                    "nodes": [],
                    "edges": [],
                    "stats": {}
                }

            entities_file = None
            relationships_file = None

            for root, dirs, files in os.walk(self.output_dir):

                for file in files:

                    name = file.lower()

                    if (
                        "entities" in name
                        and name.endswith(".parquet")
                    ):
                        entities_file = os.path.join(root, file)

                    elif (
                        "relationships" in name
                        and name.endswith(".parquet")
                    ):
                        relationships_file = os.path.join(root, file)

            if entities_file is None:
                logger.warning(
                    "entities.parquet não encontrado"
                )
                return {
                    "nodes": [],
                    "edges": [],
                    "stats": {}
                }

            if relationships_file is None:
                logger.warning(
                    "relationships.parquet não encontrado"
                )
                return {
                    "nodes": [],
                    "edges": [],
                    "stats": {}
                }

            logger.info(f"Entities: {entities_file}")
            logger.info(f"Relationships: {relationships_file}")

            df_entities = pd.read_parquet(entities_file)
            df_relationships = pd.read_parquet(
                relationships_file
            )

            nodes = []

            for _, row in df_entities.iterrows():

                node_id = str(
                    row.get(
                        "id",
                        row.get(
                            "title",
                            row.get("name", "")
                        )
                    )
                )

                label = str(
                    row.get(
                        "title",
                        row.get(
                            "name",
                            node_id
                        )
                    )
                )

                nodes.append(
                    {
                        "id": node_id,
                        "label": label,
                        "size": 20
                    }
                )

            edges = []

            for _, row in df_relationships.iterrows():

                source = str(
                    row.get("source", "")
                )

                target = str(
                    row.get("target", "")
                )

                if source and target:

                    edges.append(
                        {
                            "source": source,
                            "target": target,
                            "weight": float(
                                row.get(
                                    "weight",
                                    1
                                )
                            )
                        }
                    )

            stats = {
                "total_entities": len(nodes),
                "total_relationships": len(edges),
                "communities":
                    int(
                        df_entities["community"].nunique()
                    )
                    if "community" in df_entities.columns
                    else 0,
                "avg_degree":
                    round(
                        (2 * len(edges))
                        / max(len(nodes), 1),
                        2
                    )
            }

            logger.info(
                f"{len(nodes)} entidades carregadas"
            )

            logger.info(
                f"{len(edges)} relacionamentos carregados"
            )

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

        if not data["nodes"]:
            return "Nenhum grafo encontrado."

        s = data["stats"]

        return (
            f"Entidades: {s['total_entities']} | "
            f"Relacionamentos: {s['total_relationships']} | "
            f"Comunidades: {s['communities']}"
        )

    def get_top_entities(self, n=10):

        data = self.extract_graph_data()

        degree = {}

        for edge in data["edges"]:

            degree[edge["source"]] = (
                degree.get(edge["source"], 0)
                + 1
            )

            degree[edge["target"]] = (
                degree.get(edge["target"], 0)
                + 1
            )

        return sorted(
            degree.items(),
            key=lambda x: x[1],
            reverse=True
        )[:n]

    def get_graph_json(self):

        return json.dumps(
            self.extract_graph_data(),
            ensure_ascii=False
        )