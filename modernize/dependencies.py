import json
import os

class CallDependencyRecord:
    def __init__(
        self,
        caller: str,
        target: str,
        resolution: str = "UNRESOLVED_DYNAMIC",
        reachable: str = "NO",
        executed: str = "NO",
        java_target: str = "NOT_GENERATED",
        migration_status: str = "UNMIGRATED",
        evidence: str = ""
    ):
        self.caller = caller
        self.target = target
        self.resolution = resolution
        self.reachable = reachable
        self.executed = executed
        self.java_target = java_target
        self.migration_status = migration_status
        self.evidence = evidence

    def to_dict(self) -> dict:
        return {
            "caller": self.caller,
            "target": self.target,
            "resolution": self.resolution,
            "reachable": self.reachable,
            "executed": self.executed,
            "java_target": self.java_target,
            "migration_status": self.migration_status,
            "evidence": self.evidence
        }

class DependencyMigrationStatus:
    def __init__(self, schema_version: str = "1.0"):
        self.schema_version = schema_version
        self.calls = []

    def add_call(self, record: CallDependencyRecord):
        self.calls.append(record)

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "calls": [call.to_dict() for call in self.calls]
        }

    def save(self, path: str):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, indent=2)
