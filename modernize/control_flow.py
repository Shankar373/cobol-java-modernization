import json
import os

class ControlFlowEdge:
    def __init__(self, from_node: str, to_node: str, condition: str = ""):
        self.from_node = from_node
        self.to_node = to_node
        self.condition = condition

    def to_dict(self) -> dict:
        return {
            "from": self.from_node,
            "to": self.to_node,
            "condition": self.condition
        }

class ControlFlowModel:
    def __init__(self, schema_version: str = "1.0"):
        self.schema_version = schema_version
        self.paragraphs = {}
        self.edges = []

    def add_paragraph(self, name: str, statements: list):
        self.paragraphs[name] = statements

    def add_edge(self, edge: ControlFlowEdge):
        self.edges.append(edge)

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "paragraphs": self.paragraphs,
            "edges": [edge.to_dict() for edge in self.edges]
        }

    def save(self, path: str):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, indent=2)
