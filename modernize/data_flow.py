import json
import os

class DataFlowTransition:
    def __init__(self, from_var: str, to_var: str, operation: str = "", expression: str = ""):
        self.from_var = from_var
        self.to_var = to_var
        self.operation = operation
        self.expression = expression

    def to_dict(self) -> dict:
        return {
            "from": self.from_var,
            "to": self.to_var,
            "operation": self.operation,
            "expression": self.expression
        }

class DataFlowModel:
    def __init__(self, schema_version: str = "1.0"):
        self.schema_version = schema_version
        self.inputs = []
        self.outputs = []
        self.transitions = []

    def add_input(self, name: str, source: str):
        self.inputs.append({"name": name, "source": source})

    def add_output(self, name: str, target: str):
        self.outputs.append({"name": name, "target": target})

    def add_transition(self, trans: DataFlowTransition):
        self.transitions.append(trans)

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "transitions": [t.to_dict() for t in self.transitions]
        }

    def save(self, path: str):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, indent=2)
