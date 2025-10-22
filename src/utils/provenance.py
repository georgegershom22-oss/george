import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, Optional

@dataclass
class Artifact:
    name: str
    path: str
    kind: str  # raw|processed|combined
    description: str

@dataclass
class ProvenanceRecord:
    dataset_name: str
    generator: str
    source: str  # url or "synthetic"
    parameters: Dict[str, Any]
    created_at_utc: str
    artifacts: Dict[str, Artifact]

    def to_json(self) -> str:
        payload = asdict(self)
        payload["artifacts"] = {k: asdict(v) for k, v in self.artifacts.items()}
        return json.dumps(payload, indent=2)


def make_record(dataset_name: str, generator: str, source: str, parameters: Optional[Dict[str, Any]] = None,
                artifacts: Optional[Dict[str, Artifact]] = None) -> ProvenanceRecord:
    return ProvenanceRecord(
        dataset_name=dataset_name,
        generator=generator,
        source=source,
        parameters=parameters or {},
        created_at_utc=datetime.utcnow().isoformat(timespec="seconds") + "Z",
        artifacts=artifacts or {},
    )


def save_record(record: ProvenanceRecord, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(record.to_json())
